#from fields import BaseField
#from . import widgets
import iktomi

class HasFields(object):
    '''
        Base object that has `fields` attribute containing mixed BaseField and
        NoFieldWidget instances.

        HasField.__init__ divides the to two lists:
        * self.fields containing all BaseField instances
        * self.widgets containing all field widgets and NoFieldWidget instances
    '''

    def __init__(self):
        self.widgets = self.get_widgets(self.fields)
        self.fields = self.get_fields(self.fields)

    @staticmethod
    def get_fields(lst):
        fields = []
        for field in lst:
            if isinstance(field, iktomi.forms.fields.BaseField):
                fields.append(field)
            elif isinstance(field, iktomi.forms.widgets.FieldBlock):
                fields += field.fields
            elif not isinstance(field, iktomi.forms.widgets.NoFieldWidget):
                raise RuntimeError('fields argument should be either '
                                   'BaseField or NoFieldWidget instance')
        return fields

    @staticmethod
    def get_widgets(lst):
        ws = []
        for field in lst:
            if isinstance(field, iktomi.forms.fields.BaseField) and field.widget:
                ws.append(field.widget)
            elif isinstance(field, iktomi.forms.widgets.NoFieldWidget):
                ws.append(field)
        return ws
