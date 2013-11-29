from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


def crispy_context(submit_text='Submit', html5_required=True, **attrs):
    '''
    Creates context dict with a default :class:`crispy_forms.helper.FormHelper`
    object named "form_helper".
    '''
    helper = FormHelper()
    helper.add_input(Submit('submit', submit_text))
    helper.html5_required = html5_required
    helper.__dict__.update(attrs)
    return {'form_helper': helper}
