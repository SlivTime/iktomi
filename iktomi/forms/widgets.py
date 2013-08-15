# -*- coding: utf-8 -*-

from ..utils import weakproxy, cached_property
from ..utils.deprecation import deprecated
from . import convs
from .media import FormMedia

class Widget(object):

    #: Template to render widget
    template = None
    #: List of :class:`FormMediaAtom<iktomi.forms.media.FormMediaAtom>`
    #: objects associated with the widget
    media = []
    #: Value of HTML element's *class* attribute
    classname = ''
    #: describes how the widget is rendered.
    #: the following values are supported by default:
    #: 'default': label is rendered in usual place
    #: 'checkbox': label and widget are rendered close to each other
    #: 'full-width': for table-like templates, otherwise should be rendered as default
    #: 'hidden': label is not rendered
    render_type = 'default'

    def __init__(self, field=None, **kwargs):
        self.field = weakproxy(field)
        self._init_kwargs = kwargs
        self.__dict__.update(kwargs)

    @cached_property
    def parent(self):
        return self.field

    @property
    def multiple(self):
        return self.parent.multiple

    @property
    def input_name(self):
        return self.field.input_name

    @property
    def id(self):
        return self.field.id

    @property
    def error(self):
        return self.field.error

    @property
    def env(self):
        return self.parent.env

    @cached_property
    def label(self):
        return self.field.label

    def get_media(self):
        return FormMedia(self.media)

    def prepare_data(self):
        '''
        Method returning data passed to template.
        Subclasses can override it.
        '''
        value = self.get_raw_value()
        return dict(widget=self,
                    field=self.field,
                    value=value,
                    readonly=not self.field.writable)

    def get_raw_value(self):
        return self.field.raw_value

    def render(self):
        '''
        Renders widget to template
        '''
        data = self.prepare_data()
        if self.field.readable:
            return self.env.template.render(self.template, **data)
        return ''

    def __call__(self, **kwargs):
        kwargs = dict(self._init_kwargs, **kwargs)
        kwargs.setdefault('field', self.field)
        return self.__class__(**kwargs)


class TextInput(Widget):

    template = 'widgets/textinput'
    classname = 'textinput'


class Textarea(Widget):

    template = 'widgets/textarea'


class HiddenInput(Widget):

    render_type = 'hidden'
    template = 'widgets/hiddeninput'


class PasswordInput(Widget):

    template = 'widgets/passwordinput'
    classname = 'textinput'


class Select(Widget):
    '''
    Takes options from :class:`EnumChoice<EnumChoice>` converter,
    looks up if converter allows null and passed this value as template
    :obj:`required` variable.
    '''
    template = 'widgets/select'
    classname = None
    #: HTML select element's select attribute value.
    size = None
    #: Label assigned to None value if field is not required
    null_label = '--------'

    def get_options(self, value):
        options = []
        if not self.multiple and (value == '' or not self.field.conv.required):
            options = [{'value': '',
                        'title': self.null_label,
                        'selected': value in (None, '')}]
        # XXX ugly
        choice_conv = self.field.conv
        if isinstance(choice_conv, convs.ListOf):
            choice_conv = choice_conv.conv
        assert isinstance(choice_conv, convs.EnumChoice)

        values = value if self.multiple else [value]
        values = map(unicode, values)
        for choice, label in choice_conv.options():
            choice = unicode(choice)
            options.append(dict(value=choice,
                                title=label,
                                selected=(choice in values)))
        return options

    def prepare_data(self):
        data = Widget.prepare_data(self)
        return dict(data,
                    options=self.get_options(data['value']),
                    required=('true' if self.field.conv.required else 'false'))


class CheckBoxSelect(Select):

    classname = 'select-checkbox'
    template = 'widgets/select-checkbox'


class CheckBox(Widget):

    render_type = 'checkbox'
    template = 'widgets/checkbox'


class CharDisplay(Widget):

    template = 'widgets/span'
    classname = 'chardisplay'
    #: If is True, value is escaped while rendering. 
    #: Passed to template as :obj:`should_escape` variable.
    escape = True
    #: Function converting the value to string.
    getter = staticmethod(lambda v: v)

    def prepare_data(self):
        data = Widget.prepare_data(self)
        return dict(data,
                    value=self.getter(data['value']),
                    should_escape=self.escape)


class FileInput(Widget):

    template = 'widgets/file'


class AggregateWidget(Widget):

    def get_raw_value(self):
        return None


class FieldListWidget(AggregateWidget):

    template = 'widgets/fieldlist'


class FieldSetWidget(AggregateWidget):

    template = 'widgets/fieldset'


class NoFieldWidget(Widget):

    multiple = None
    input_name = None
    id = '' # XXX
    field = None
    label = None
    error = None

    def __init__(self, parent=None, **kwargs):
        self.parent = weakproxy(parent)
        self._init_kwargs = kwargs
        self.__dict__.update(kwargs)

    def get_raw_value(self):
        return None

    def render(self):
        data = self.prepare_data()
        return self.env.template.render(self.template, **data)

    def __call__(self, **kwargs):
        kwargs = dict(self._init_kwargs, **kwargs)
        kwargs.setdefault('parent', self.parent)
        return self.__class__(**kwargs)


class FieldBlock(NoFieldWidget):

    template = 'widgets/collapsable_block'
    classname_defaults = {'close': 'collapsable closed',
                          'open': 'collapsable'}
    open_with_data = False
    opened = True
    prefix = ''

    def __init__(self, title, fields=[], **kwargs):
        if kwargs.get('parent'):
            parent = kwargs['parent']
            fields = [field(parent=parent) for field in fields]
        kwargs.update(dict(
            title=title,
            fields=fields,
        ))
        NoFieldWidget.__init__(self, **kwargs)

    @cached_property
    def classname(self):
        if self.open_with_data or self.opened:
            for f in self.fields:
                if self.opened or self.form.python_data[f.name]:
                    return self.classname_defaults['open']
        return self.classname_defaults['close']

    def __add__(self, x):
        # XXX is this needed?
        return [self] + x

    def __radd__(self, x):
        # XXX is this needed?
        return x + [self]


field_block = FieldBlock
#field_block = deprecated('field_block() is deprecated. Use FieldBlock instead')(FieldBlock)


