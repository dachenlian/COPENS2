import os

from pathlib import Path
from django.db.models import Q
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings

from .forms import UploadCorpusForm, SearchForm
from . import utils
from .models import Corpus, CopensUser
from .mixins import MultiFormMixin, MultiFormsView

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
        if not self.request.GET.get('corpora'):
            messages.warning(self.request, '請至少選擇一個語料庫')
            return redirect('create:home')

        if self.request.GET.get('page'):
            results_list = self.request.session.get('results_list')
            paginator = Paginator(results_list, 100)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            return render(request, self.template_name, {'results': results})

        form = SearchForm(self.request.GET)

        if form.is_valid():
            results_list = []
            user_registry = utils.get_user_registry(self.request)
            print('********************')
            print(user_registry)

            print('********************')
            print(list(form.cleaned_data.items()))
            results_dict = utils.cqp_query(user_registry=user_registry, **form.cleaned_data)
            print(results_dict)

            for corpus, path in results_dict.items():
                results_list.extend(utils.read_results(path))

            paginator = Paginator(results_list, 100)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            self.request.session['results_list'] = results_list

            return render(request, self.template_name, {'results': results})

        return redirect('create:home')


class UploadCorporaView(LoginRequiredMixin, FormView):
    """
    User can upload personal corpora to COPENS.
    """
    login_url = 'account_login'
    template_name = 'createcorpora/index.html'
    form_class = UploadCorpusForm
    success_url = reverse_lazy('create:upload')

    def form_valid(self, form):
        print(list(form.cleaned_data.items()))
        file = form.cleaned_data['file']
        p_attrs = form.cleaned_data['positional_attrs']
        s_attrs = form.cleaned_data['structural_attrs']
        zh_name = form.cleaned_data['zh_name']
        en_name = form.cleaned_data['en_name']
        is_public = form.cleaned_data['is_public']

        copens_user = get_object_or_404(CopensUser, user=self.request.user)
        print(copens_user.user)
        raw_dir = Path(copens_user.raw_dir)
        data_dir = Path(copens_user.data_dir)
        registry_dir = Path(copens_user.registry_dir)

        print(raw_dir.joinpath(file.name))
        if raw_dir.joinpath(file.name).exists():
            messages.warning(self.request, 'This corpus already exists.')
            return redirect('create:upload')

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
        if is_public:
            os.link(registry_dir.joinpath(file.name.split('.')[0]),
                    Path(settings.CWB_PUBLIC_REG_DIR).joinpath(file.name.split('.')[0]),
                    )
        return super().form_valid(form)


class UserPanelView(LoginRequiredMixin, MultiFormsView):
    login_url = 'account_login'
    template_name = 'createcorpora/user_panel.html'

    form_classes = {
        'upload': UploadCorpusForm,
        'search': SearchForm
    }

    success_urls = {
        'upload': reverse_lazy('create:home'),
        'search': ''
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        copens_user = CopensUser.objects.get(user=self.request.user)
        corpora = [c for c in Corpus.objects.filter(Q(owner=copens_user))]
        context['no_corpus'] = True if len(corpora) == 0 else False
        return context

    def upload_form_valid(self, form):
        print(list(form.cleaned_data.items()))
        file = form.cleaned_data['file']
        p_attrs = form.cleaned_data['positional_attrs']
        s_attrs = form.cleaned_data['structural_attrs']
        zh_name = form.cleaned_data['zh_name']
        en_name = form.cleaned_data['en_name']
        is_public = form.cleaned_data['is_public']

        copens_user = get_object_or_404(CopensUser, user=self.request.user)
        print(copens_user.user)
        raw_dir = Path(copens_user.raw_dir)
        data_dir = Path(copens_user.data_dir)
        registry_dir = Path(copens_user.registry_dir)

        print(raw_dir.joinpath(file.name))
        if raw_dir.joinpath(file.name).exists():
            messages.warning(self.request, '您上傳的語料庫已存在！')
            return redirect('create:home')

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
        if is_public:
            os.link(registry_dir.joinpath(file.name.split('.')[0]),
                    Path(settings.CWB_PUBLIC_REG_DIR).joinpath(file.name.split('.')[0]),
                    )
        return super().upload_form_valid(form)

    def search_form_valid(self, form):
        print(form.cleaned_data.items())
