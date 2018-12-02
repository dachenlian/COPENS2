from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import UploadCorpusForm


class UploadCorporaView(FormView):
    template_name = 'createcorpora/index.html'
    form_class = UploadCorpusForm
