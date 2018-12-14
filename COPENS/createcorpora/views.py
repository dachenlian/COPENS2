import os
import logging

from pathlib import Path
from django.db.models import Q
from django.views.generic.edit import FormView
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings

from .forms import UploadCorpusForm, SearchForm, KeynessForm
from . import utils
from .models import Corpus, CopensUser
from .mixins import MultiFormMixin, MultiFormsView

logger = logging.getLogger('django')


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


class ResultsView(View):
    """
    Results after querying CWB are returned here.
    """
    template_name = 'createcorpora/results.html'

    def get(self, request):
        if not self.request.GET.getlist('corpora'):
            messages.warning(self.request, '請至少選擇一個語料庫')
            return redirect('create:home')

        if self.request.GET.get('page'):
            results_list = self.request.session.get('results_list')
            paginator = Paginator(results_list, 20)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            results.total = len(results_list)
            results.object_list = list(map(for_concordance_tag, results.object_list))
            return render(request, self.template_name, {'results': results})

        form = SearchForm(self.request.GET)
        if form.is_valid():
            results_list = []
            if self.request.user.is_authenticated:
                user_registry = utils.get_user_registry(self.request)
            # print(list(form.cleaned_data.items()))
            else:
                user_registry = None
            results_dict = utils.cqp_query(user_registry=user_registry, **form.cleaned_data)
            # print(results_dict)
            for corpus, path in results_dict.items():
                try:
                    results_list.extend(utils.read_results(path))
                except FileNotFoundError:
                    messages.error(request, '查詢語法有誤！')
                    redirect('create:home')

            paginator = Paginator(results_list, 50)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            results.total = len(results_list)
            results.object_list = list(map(for_concordance_tag, results.object_list))
            self.request.session['results_list'] = results_list

            return render(request, self.template_name, {'results': results})
        return redirect('create:home')


def for_concordance_tag(elm):
    import re
    p = re.compile('<B>(.*)</B>')
    query_word = p.search(elm).group(1)
    context_left = elm.split('<B>')[0].replace('<LI>', '')
    context_right = elm.split('</B>')[1].replace('</LI>', '')

    return {
        'context_left': context_left,
        'query_word': query_word,
        'context_right': context_right
    }


class UploadCorporaView(LoginRequiredMixin, FormView):
    """
    User can upload personal corpora to COPENS.
    """
    login_url = 'account_login'
    template_name = 'createcorpora/index.html'
    form_class = UploadCorpusForm
    success_url = reverse_lazy('create:home')

    def form_valid(self, form):
        print(list(form.cleaned_data.items()))
        file = form.cleaned_data['file']
        p_attrs = form.cleaned_data['positional_attrs']
        s_attrs = form.cleaned_data['structural_attrs']
        zh_name = form.cleaned_data['zh_name']
        en_name = form.cleaned_data['en_name']
        is_public = form.cleaned_data['is_public']
        needs_preprocessing = form.cleaned_data['needs_preprocessing']

        filename = file.name.split('.')[0].lower()
        if filename != en_name.lower():
            messages.warning(self.request, '上傳失敗：您檔名與語料庫英文名字不同！')
            return redirect('create:home')

        copens_user = get_object_or_404(CopensUser, user=self.request.user)
        print(copens_user.user)
        raw_dir = Path(copens_user.raw_dir)
        data_dir = Path(copens_user.data_dir)
        registry_dir = Path(copens_user.registry_dir)

        print(raw_dir.joinpath(file.name))
        if raw_dir.joinpath(file.name).exists():
            messages.warning(self.request, '上傳失敗：您上傳的語料庫已存在！')
            return redirect('create:home')

        # Upload a copy to TCSL
        # if success: save `tcsl.tcsl_doc_id` and `tcsl.tcsl_corpus_name` into Corpus model
        tcsl = utils.TCSL()
        tcsl_upload_success = tcsl.upload(file)

        utils.save_file_to_drive(file, raw_dir)
        if needs_preprocessing:
            s_attrs = ""
            p_attrs = "-P pos"
            utils.preprocess(raw_dir / file.name, raw_dir=raw_dir)
            file.name = f"{file.name.split('.')[0]}.vrt"

        utils.cwb_encode(vrt_file=raw_dir / file.name, data_dir=data_dir,
                         registry_dir=registry_dir, p_attrs=p_attrs, s_attrs=s_attrs)
        utils.cwb_make(Path(file.name).stem, registry_dir=registry_dir)

        # if the file is plain text (which means it's "needs_preprocessing" is True)
        # should upload to TSCL as well, in order to get more functions


        if tcsl_upload_success:
            Corpus.objects.create(
                owner=copens_user,
                zh_name=zh_name,
                en_name=en_name,
                is_public=is_public,
                file_name=file.name,
                tcsl_doc_id=tcsl.tcsl_doc_id,
                tcsl_corpus_name=tcsl.tcsl_corpus_name
            )

        else:
            Corpus.objects.create(
                owner=copens_user,
                zh_name=zh_name,
                en_name=en_name,
                is_public=is_public,
                file_name=file.name,
            )

        if is_public:
            os.link(registry_dir.joinpath(file.name.split('.')[0]),
                    Path(settings.CWB_PUBLIC_REG_DIR).joinpath(file.name.split('.')[0].lower()),
                    )
        messages.warning(self.request, '語料上傳成功！')
        return super().form_valid(form)


class DeleteCorpusView(LoginRequiredMixin, DeleteView):
    """Delete user uploaded corpora."""
    login_url = 'account_login'
    model = Corpus
    success_url = reverse_lazy('create:home')

    def delete(self, request, *args, **kwargs):
        copens_user = get_object_or_404(CopensUser, user=self.request.user)
        corpus = self.get_object()
        if copens_user == corpus.owner:
            utils.delete_files_from_drive(copens_user, corpus)
            messages.success(request, '刪除語料庫成功！')
            return super().delete(request, *args, **kwargs)
        else:
            return redirect('create:home')


class UserPanelView(LoginRequiredMixin, MultiFormsView):
    login_url = 'account_login'
    template_name = 'createcorpora/user_panel.html'

    form_classes = {
        'upload': UploadCorpusForm,
        'search': SearchForm,
        'keyness': KeynessForm
    }

    success_urls = {
        'upload': reverse_lazy('create:home'),
        'search': ''
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        copens_user = CopensUser.objects.get(user=self.request.user)
        private_corpora = Corpus.objects.filter(owner=copens_user)
        public_corpora = Corpus.objects.filter(is_public=True)
        context['no_corpus'] = True if len(private_corpora) == 0 and len(public_corpora) == 0 else False
        context['private_corpora'] = private_corpora
        return context

    def get_form_kwargs(self, form_name, bind_form=False):
        kwargs = super().get_form_kwargs(form_name, bind_form)
        kwargs['user'] = self.request.user
        return kwargs

    def search_form_valid(self, form):
        print(form.cleaned_data.items())


class KeynessResultView(View):
    """
    Results for keyness.
    """
    template_name = 'createcorpora/results.html'

    def get(self, request):
        if not self.request.GET.getlist('corpora'):
            messages.warning(self.request, '請至少選擇一個語料庫')
            return redirect('create:home')

        if self.request.GET.get('page'):
            results_list = self.request.session.get('results_list')
            paginator = Paginator(results_list, 20)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            results.total = len(results_list)
            results.object_list = list(map(for_concordance_tag, results.object_list))
            return render(request, self.template_name, {'results': results})

        form = SearchForm(self.request.GET)

        if form.is_valid():
            results_list = []
            user_registry = utils.get_user_registry(self.request)
            # print(list(form.cleaned_data.items()))
            results_dict = utils.cqp_query(user_registry=user_registry, **form.cleaned_data)
            # print(results_dict)
            for corpus, path in results_dict.items():
                results_list.extend(utils.read_results(path))

            paginator = Paginator(results_list, 50)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            results.total = len(results_list)
            results.object_list = list(map(for_concordance_tag, results.object_list))
            self.request.session['results_list'] = results_list

            return render(request, self.template_name, {'results': results})

        return redirect('create:home')
