from django.shortcuts import render
from django.views.generic import TemplateView

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