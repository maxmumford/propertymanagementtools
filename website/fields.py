from django.db import models
import widgets
 
class DatePickerField(models.DateField):

    __metaclass__ = models.SubfieldBase
 
    def formfield(self, **kwargs):
        kwargs['widget'] = widgets.DatePickerWidget
        return super(DatePickerField, self).formfield(**kwargs)
