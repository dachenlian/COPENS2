from django.urls import path
from .views import Home, About, TermOfUse, Contact, ApiDoc, Query

app_name = 'copens_static_pages'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about', About.as_view(), name='about'),
    path('term_of_use', TermOfUse.as_view(), name='term_of_use'),
    path('contact', Contact.as_view(), name='contact'),
    path('api_doc', ApiDoc.as_view(), name='api_doc'),
    path('query', Query.as_view(), name='query'),




    # path('create/', UploadCorporaView.as_view(), name='upload')
]
