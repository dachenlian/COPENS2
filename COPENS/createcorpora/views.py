from pathlib import Path
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render, render_to_response
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import UploadCorpusForm, SearchForm
from . import utils
from .models import Corpus, CopensUser


class Home(ListView):
    template_name = 'createcorpora/home.html'
    model = Corpus
    paginate_by = 100

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = CopensUser.objects.get(user=self.request.user)
            context['private_corpora'] = Corpus.objects.filter(owner=user)
        context['public_corpora'] = Corpus.objects.filter(is_public=True)
        return context


class ResultsView(View):
    """
    Results after querying CWB are returned here.
    """
    template_name = 'createcorpora/results.html'

    def get(self, request):
        print(list(self.request.GET.items()))
        print(self.request.GET.getlist('db_choices'))
        return render(request, self.template_name)


class SearchView(FormView):
    """
    User chooses what databases to query from.
    """
    template_name = 'createcorpora/search.html'
    form_class = SearchForm

    def get_form_kwargs(self):
        """
        Add the current logged in user to the form's context.
        """
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        print(form.cleaned_data.items())


class UploadCorporaView(LoginRequiredMixin, FormView):
    """
    User can upload personal corpora to COPENS.
    """
    login_url = 'account_login'
    template_name = 'createcorpora/index.html'
    form_class = UploadCorpusForm
    success_url = reverse_lazy('create:upload')

    def form_valid(self, form):
        print(form.cleaned_data.items())
        file = form.cleaned_data['file']
        p_attrs = form.cleaned_data['positional_attrs']
        s_attrs = form.cleaned_data['structural_attrs']
        zh_name = form.cleaned_data['zh_name']
        en_name = form.cleaned_data['en_name']
        is_public = form.cleaned_data['is_public']

        utils.save_file_to_drive(file)
        utils.cwb_encode(Path(settings.CWB_RAW_DIR) / file.name, p_attrs=p_attrs, s_attrs=s_attrs)
        utils.cwb_make(Path(file.name).stem)
        user = CopensUser.objects.get(user=self.request.user)
        Corpus.objects.create(
            owner=user,
            zh_name=zh_name,
            en_name=en_name,
            is_public=is_public,
        )

        return super().form_valid(form)



class UserPanelView(LoginRequiredMixin, FormView):
    login_url = 'account_login'
    template_name = 'createcorpora/user_panel.html'
    form_class = UploadCorpusForm
    success_url = reverse_lazy('create:upload')

    def form_valid(self, form):
        file = self.request.FILES['file']
        p_attrs = self.request.POST['positional_attrs']
        s_attrs = self.request.POST['structural_attrs']
        utils.save_file_to_drive(file)
        utils.cwb_encode(Path(settings.CWB_RAW_DIR) / file.name, p_attrs=p_attrs, s_attrs=s_attrs)
        utils.cwb_make(Path(file.name).stem)
        return super().form_valid(form)
