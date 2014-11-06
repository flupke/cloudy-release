from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import UserProfile


class UserProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['secret'].widget.attrs['readonly'] = True
        self.helper = FormHelper()
        self.helper.add_input(Submit('gen_secret', 'Generate new auth key'))

    class Meta:
        model = UserProfile
        exclude = ['user']
