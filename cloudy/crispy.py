from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


def crispy_context(submit_text='Submit', **attrs):
    '''
    Creates context dict with a default :class:`crispy_forms.helper.FormHelper`
    object named "form_helper".
    '''
    helper = FormHelper()
    helper.add_input(Submit('submit', submit_text))
    helper.html5_required = True
    helper.__dict__.update(attrs)
    return {'form_helper': helper}
