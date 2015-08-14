from django.utils.safestring import mark_safe
from django.forms import TextInput
from django.db import models

class DatePickerWidget(TextInput):

    def render(self, name, value, attrs=None):
        """
        Create a twitter bootstrap datepicker widget using the dateinput field as a base.
        This widget is used with the DatePickerField defined in fields.py
        """
        output = []
        # render normal text input
        date_input_html = super(DatePickerWidget, self).render(name, value, attrs)
        output.append(u"<div class='input-group date datepicker'>" % {'name': name})

        # convert text input to hidden field
        output.append(date_input_html.replace('type="text"', 'type="hidden"'))

        # add text input for datepicker and link the two up with javascript
        output.append("<input type='text' value='%(value)s' id='%(name)s_datepicker' class='form-control'>" % {'value': value or '', 'name': name})
        output.append("</div>")
        output.append("""<script>$(document).ready(function(){
                            // set the datepicker to the english version of the hidden field
                            var american_date = $('#id_%(name)s').val();
                            if(american_date.length > 0){
                                var american_date_parts = american_date.split('/')
                                $('#%(name)s_datepicker').val(american_date_parts[1] + '/' + american_date_parts[0] + '/' + american_date_parts[2])
                            }

                            // set up the datapicker and update the hidden field to english format
                            $('#%(name)s_datepicker').datepicker({'format': 'dd/mm/yyyy'}).on('changeDate', function (e) {
                                $('#id_%(name)s').val(e.format('mm/dd/yyyy'))
                            });
                        });</script>""" % {'name': name})
        return mark_safe(u''.join(output))
