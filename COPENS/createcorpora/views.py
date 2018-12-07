from pathlib import Path
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

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


class ResultsView(View):
    """
    Results after querying CWB are returned here.
    """
    template_name = 'createcorpora/results.html'

    def get(self, request):
        if not self.request.GET.get('db_choices'):
            messages.warning(self.request, 'At least one database must be selected.')
            return redirect('create:search')

        form = SearchForm(self.request.GET)
        if form.is_valid():
            print(form.cleaned_data.items())
            query = form.cleaned_data['query']
            db_choices = form.cleaned_data['db_choices']
            show_pos = form.cleaned_data['show_pos']
            context = form.cleaned_data['context']

        return render(request, self.template_name)


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

        copens_user = get_object_or_404(CopensUser, user=self.request.user)
        raw_dir = Path(copens_user.raw_dir)
        data_dir = Path(copens_user.data_dir)
        registry_dir = Path(copens_user.registry_dir)

        utils.save_file_to_drive(file, raw_dir)
        utils.cwb_encode(vrt_file=raw_dir / file.name, data_dir=data_dir,
                         registry_dir=registry_dir, p_attrs=p_attrs, s_attrs=s_attrs)
        utils.cwb_make(Path(file.name).stem, registry_dir=registry_dir)

        Corpus.objects.create(
            owner=copens_user,
            zh_name=zh_name,
            en_name=en_name,
            is_public=is_public,
        )

        return super().form_valid(form)


class UserPanelView(UploadCorporaView):
    template_name = 'createcorpora/user_panel.html'
