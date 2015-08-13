from django.utils.safestring import mark_safe
from django.forms import DateInput
from django.db import models

class DatePickerWidget(DateInput):
    def render(self, name, value, attrs=None):
        """
        Create a twitter bootstrap datepicker widget using the dateinput field as a base.
        This widget is used with the DatePickerField defined in fields.py
        """
        output = []
        self.attrs = {'class': 'form-control'}
        date_input_html = super(DatePickerWidget, self).render(name, value, attrs)
        output.append(u"<div class='input-group date datepicker'>")
        output.append(date_input_html)
        output.append("""<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span></div>""")
        return mark_safe(u''.join(output))
 