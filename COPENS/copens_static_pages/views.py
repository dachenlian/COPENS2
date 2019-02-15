from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from .forms import ConcordanceForm

from createcorpora import utils

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
    User chooses what databases to query from.
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
    Results after querying CWB are returned here.
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
        print('@@@')
        print(form.is_valid())
        print(form.cleaned_data)


        if form.is_valid():
            results_list = []
            if self.request.user.is_authenticated:
                user_registry = utils.get_user_registry(self.request)
                print(user_registry)
            else:
                user_registry = None
            results_dict = utils.cqp_query(user_registry=user_registry, **form.cleaned_data)
            print(results_dict)
            for corpus, path in results_dict.items():
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