import csv

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.http import StreamingHttpResponse

from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

from createcorpora.models import Corpus, CopensUser


from .forms import ConcordanceForm, WordlistForm, WordSketchForm

from createcorpora import utils
from createcorpora.views import for_concordance_tag



# Create your views here.
class Home(TemplateView):
    template_name = 'copens_static_pages/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Home, self).get_context_data(*args, **kwargs)
        context['home'] = True
        return context

class About(TemplateView):
    template_name = 'copens_static_pages/about.html'


class TermOfUse(TemplateView):
    template_name = 'copens_static_pages/term_of_use.html'


class Contact(TemplateView):
    template_name = 'copens_static_pages/contact.html'


class ApiDoc(TemplateView):
    template_name = 'copens_static_pages/api_doc.html'


class Query(TemplateView):
    template_name = 'copens_static_pages/query.html'



class ConcordanceQueryView(FormView):
    """
    搜尋Concordance的頁面
    """

    template_name = 'copens_static_pages/query_concordance.html'
    form_class = ConcordanceForm

    def get_form_kwargs(self):
        """
        Add the current logged in user to the form's context.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        print(form.errors)


class ConcordanceResultView(View):
    """
    顯示搜尋Concordance的結果頁面。
    """
    template_name = 'copens_static_pages/result_concordance.html'

    def get(self, request):
        if not self.request.GET.getlist('corpora'):
            messages.warning(self.request, '請至少選擇一個語料庫')
            return redirect('static_pages:concordance')

        if self.request.GET.get('page'):
            results_list = self.request.session.get('results_list')
            paginator = Paginator(results_list, 20)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            results.total = len(results_list)
            results.object_list = list(map(for_concordance_tag, results.object_list))
            return render(request, self.template_name, {'results': results})

        form = ConcordanceForm(self.request.GET, user=self.request.user)

        if form.is_valid():
            results_list = []
            if self.request.user.is_authenticated:
                user_registry = utils.get_user_registry(self.request)
                print(user_registry)
            else:
                user_registry = None
            results_dict = utils.cqp_query(user_registry=user_registry, **form.cleaned_data)
            self.request.session['results_dict'] = results_dict
            print(results_dict)
            for corpus, path in results_dict.items():
                print(corpus, path)
                try:
                    results_list.extend(utils.read_results(path))
                except FileNotFoundError:
                    messages.error(request, '查詢語法有誤！')
                    return redirect('static_pages:concordance')

            paginator = Paginator(results_list, 50)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            results.total = len(results_list)
            results.object_list = list(map(for_concordance_tag, results.object_list))
            self.request.session['results_list'] = results_list
            print(results.object_list)
            return render(request, self.template_name, {'results': results})
        else:
            print(form.errors)
            return redirect('static_pages:concordance')

class WordListQueryView(FormView):
    """
    User chooses what databases to query from.
    """

    template_name = 'copens_static_pages/query_wordlist.html'
    form_class = WordlistForm

    def get_form_kwargs(self):
        """
        Add the current logged in user to the form's context.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        print(form.errors)

class WordlistResultView(View):
    """
    顯示搜尋Word list的結果頁面。
    """
    template_name = 'copens_static_pages/result_wordlist.html'

    def get(self, request):
        if not self.request.GET.getlist('corpus'):
            messages.warning(self.request, '請至少選擇一個語料庫')
            return redirect('static_pages:wordlist')

        # if self.request.GET.get('page'):
        #     results_list = self.request.session.get('results_list')
        #     paginator = Paginator(results_list, 20)
        #     page = request.GET.get('page')
        #     results = paginator.get_page(page)
        #     results.total = len(results_list)
        #     results.object_list = list(map(for_concordance_tag, results.object_list))
        #     return render(request, self.template_name, {'results': results})

        form = WordlistForm(self.request.GET, user=self.request.user)
        # print(form.is_valid())
        if form.is_valid():
            results_list = []
            if self.request.user.is_authenticated:
                user_registry = utils.get_user_registry(self.request)
                print(user_registry)
            else:
                user_registry = None
            list_of_words = utils.cqp_query_wordlist(user_registry=user_registry, **form.cleaned_data)
            # print(type(list_of_words))
            # print(list_of_words)
            results = (word.strip().split('\t') for word in list_of_words)
            # print(results)
            # self.request.session['results_dict'] = results_dict
            # print(results_dict)
            # for corpus, path in results_dict.items():
            #     print(corpus, path)
            #     try:
            #         results_list.extend(utils.read_results(path))
            #     except FileNotFoundError:
            #         messages.error(request, '查詢語法有誤！')
            #         return redirect('static_pages:concordance')

            # paginator = Paginator(results_list, 50)
            # page = request.GET.get('page')
            # results = paginator.get_page(page)
            # results.total = len(results_list)
            # results.object_list = list(map(for_concordance_tag, results.object_list))
            # self.request.session['results_list'] = results_list
            # print(results.object_list)
            return render(request, self.template_name, {'results': results})
        else:
            print(form.errors)
            return redirect('static_pages:wordlist')


    # def get_context_data(self, *args, **kwargs):
    #     context = super(Home, self).get_context_data(*args, **kwargs)
    #     # Generate DB_CHOICES based on AnonymousUser / Logined User

    #     if self.request.user.is_authenticated:
    #         DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name} / {c.owner}')  # value, label
    #                        for c in Corpus.objects.filter(Q(owner=self.copens_user) | Q(is_public=True))]
    #     else:
    #         DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name}')  # value, label
    #                        for c in Corpus.objects.filter(Q(is_public=True))]
            
        
    #     super().__init__(*args, **kwargs)  # must call super() to have access to fields
    #     return context

    # def get_form_kwargs(self):
    #     """
    #     Add the current logged in user to the form's context.
    #     """
    #     kwargs = super().get_form_kwargs()

    #     kwargs['user'] = self.request.user
    #     return kwargs

    # def form_invalid(self, form):
    #     print(form.errors)

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def output_csv(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    rows = []
    for (corpus_name, file_path) in request.session['results_dict'].items():
        with open(file_path) as f:
            for line in f:
                if '<HR>' in line or 'UL>' in line:
                    continue
                else:
                    line_dict = for_concordance_tag(line)
                    rows.append([corpus_name, line_dict['context_left'], line_dict['query_word'], line_dict['context_right']])
    # rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="copens_concordance_output.csv"'
    return response


# 2019-08-09: Word sketch
class WordSketchQueryView(FormView):
    """
    User chooses what databases to query from.
    """

    template_name = 'copens_static_pages/query_word_sketch.html'
    form_class = WordSketchForm

    def get_form_kwargs(self):
        """
        Add the current logged in user to the form's context.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        print(form.errors)

class WordSketchResultView(View):
    """
    顯示搜尋Word list的結果頁面。
    """
    template_name = 'copens_static_pages/result_word_sketch.html'

    def get(self, request):
        if not self.request.GET.getlist('corpus'):
            messages.warning(self.request, '請至少選擇一個語料庫')
            return redirect('static_pages:word_sketch')

        form = WordSketchForm(self.request.GET, user=self.request.user)
        # print(form.is_valid())
        if form.is_valid():
            # results_list = []
            if self.request.user.is_authenticated:
                user_registry = utils.get_user_registry(self.request)
                print(user_registry)
            else:
                user_registry = None
            query_word_freq, results = utils.cqp_query_word_sketch(user_registry=user_registry, **form.cleaned_data)

            # results = (word.strip().split('\t') for word in list_of_words)
            # results = list_of_words
            return render(
                request,
                self.template_name,
                {
                    'results': results,
                    'query_word_freq': query_word_freq
                }
            )
        else:
            print(form.errors)
            return redirect('static_pages:word_sketch')
