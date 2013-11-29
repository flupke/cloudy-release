from django import forms 
from codemirror.widgets import CodeMirrorTextarea

from .models import Deployment


class EditDeploymentForm(forms.ModelForm):

    variables = forms.CharField(widget=CodeMirrorTextarea(mode="yaml",
        config={
            'tabMode': 'indent',
            'indentUnit': 4
        }, theme='mbo', dependencies=('javascript', 'python'),
        js_var_format='%s_editor'))

    class Meta:
        model = Deployment
