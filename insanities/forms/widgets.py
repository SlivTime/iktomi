# -*- coding: utf-8 -*-

from copy import deepcopy
import simplejson
from ..utils import weakproxy, cached_property
from . import convs
from .media import FormMedia, FormCSSRef, FormJSRef


class Widget(object):

    #: Template to render widget
    template = None
    #: List of :class:`FormMediaAtom<insanities.forms.media.FormMediaAtom>`
    #: objects associated with the widget
    media = []
    #: Value of HTML element's *class* attribute
    classname = ''

    def __init__(self, element=None, **kwargs):
        self._elem = weakproxy(element)
        self._init_kwargs = kwargs
        self.__dict__.update(kwargs)

    @property
    def id(self):
        return self._elem.id

    @property
    def env(self):
        return self._elem.env

    def get_media(self):
        return FormMedia(self.media)

    def prepare_data(self, **kwargs):
        return kwargs

    def render(self, **kwargs):
        '''
        Renders widget to template
        '''
        data = self.prepare_data(**kwargs)
        data['widget'] = self
        return self.env.render(self.template, **data)

    def __call__(self, **kwargs):
        kwargs = dict(self._init_kwargs, **kwargs)
        kwargs.setdefault('element', self._elem)
        return self.__class__(**kwargs)


# Fields got some specific attributes we want to proxy
class FieldWidget(Widget):
    @property
    def multiple(self):
        return self._elem.multiple

    @property
    def input_name(self):
        return self._elem.input_name

    @property
    def field(self):
        return self._elem

    def prepare_data(self, **kwargs):
        kwargs['field'] = self._elem
        return kwargs


class TextInput(FieldWidget):

    template = 'widgets/textinput'
    classname = 'textinput'


class HiddenInput(FieldWidget):

    template = 'widgets/hiddeninput'


class PasswordInput(FieldWidget):

    template = 'widgets/passwordinput'
    classname = 'textinput'


class Select(FieldWidget):
    '''
    Takes options from :class:`EnumChoice<EnumChoice>` converter,
    looks up if converter allows null and passed this value as template
    :obj:`required` variable.
    '''
    template = 'widgets/select'
    classname = 'select'
    #: HTML select element's select attribute value.
    size = None
    #: Label assigned to None value if field is not required
    null_label = '--------'

    def get_options(self, value):
        options = []
        if not self.multiple and (value is None or not self.field.conv.required):
            options = [{'value': '',
                        'title': self.null_label,
                        'selected': value in (None, '')}]
        assert isinstance(self.field.conv, convs.EnumChoice)

        values = value if self.multiple else [value]
        values = map(unicode, values)
        for choice, label in self.field.conv:
            choice = unicode(choice)
            options.append(dict(value=choice,
                                title=label,
                                selected=(choice in values)))
        return options

    def prepare_data(self, **kwargs):
        print kwargs
        return dict(kwargs,
                    options=self.get_options(kwargs.get('value', [])),
                    required=('true' if self.field.conv.required else 'false'))


class CheckBoxSelect(Select):

    template = 'widgets/select-checkbox'


class CheckBox(FieldWidget):

    template = 'widgets/checkbox'


class Textarea(FieldWidget):

    template = 'widgets/textarea'


class ReadonlySelect(Select):

    template = 'widgets/readonlyselect'


class CharDisplay(FieldWidget):

    template = 'widgets/span'
    classname = 'chardisplay'
    #: If is True, value is escaped while rendering. 
    #: Passed to template as :obj:`should_escape` variable.
    escape = False
    #: Function converting the value to string.
    getter = staticmethod(lambda v: v)

    def prepare_data(self, **data):
        return dict(data,
                    value=self.getter(value),
                    should_escape=self.escape)


class ImageView(FieldWidget):

    template = 'widgets/imageview'
    classname = 'imageview'


class FileInput(FieldWidget):
    '''
    '''
    template = 'widgets/fileinput'

    def prepare_data(self, **data):
        field = self.field
        value = field.value
        delete = field.form.data.get(field.input_name + '__delete', False)
        if value is None:
            value = field.parent.initial.get(field.name, None)
            if isinstance(value, field.stored_file_cls):
                mode = 'existing'
            else:
                value = None
                mode = 'empty'
        elif isinstance(value, field.stored_file_cls):
            mode = 'existing'
        elif isinstance(value, field.temp_file_cls):
            mode = 'temp'
        else:
            assert None
        return dict(data, value=value, mode=mode, input_name=self.input_name,
                    delete=delete, temp_url=self.env.rctx.conf.temp_url,
                    null=field.null)


class ImageInput(FileInput):
    template = 'widgets/imageinput'

