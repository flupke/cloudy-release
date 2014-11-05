from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import UserProfile


class UserProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['auth_key'].widget.attrs['readonly'] = True
        self.helper = FormHelper()
        self.helper.add_input(Submit('gen_auth_key', 'Generate new auth key'))

    class Meta:
        model = UserProfile
        exclude = ['user']
