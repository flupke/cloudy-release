from vanilla import ListView

from .models import Project


class ProjectsList(ListView):

    model = Project
