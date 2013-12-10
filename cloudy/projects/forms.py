from django import forms 
from codemirror.widgets import CodeMirrorTextarea

from .models import Deployment, DeploymentBaseVariables


VARIABLES_FIELD = forms.CharField(widget=CodeMirrorTextarea(mode="yaml",
    config={
        'tabMode': 'indent',
        'indentUnit': 4
    }, theme='mbo', dependencies=('javascript', 'python'),
    js_var_format='%s_editor'), required=False, label='Deployment variables')


class EditDeploymentForm(forms.ModelForm):

    variables = VARIABLES_FIELD

    class Meta:
        model = Deployment


class EditDeploymentBaseVariablesForm(forms.ModelForm):

    variables = VARIABLES_FIELD

    class Meta:
        model = DeploymentBaseVariables
