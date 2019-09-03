from django.urls import path
from . import views

app_name = 'copens_static_pages'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about', views.About.as_view(), name='about'),
    path('term_of_use', views.TermOfUse.as_view(), name='term_of_use'),
    path('contact', views.Contact.as_view(), name='contact'),
    path('api_doc', views.ApiDoc.as_view(), name='api_doc'),
    path('query', views.Query.as_view(), name='query'),
    path('result', views.ConcordanceResultView.as_view(), name='concordance_result'),
    path('concordance', views.ConcordanceQueryView.as_view(), name='concordance'),
    path('wordlist_result', views.WordlistResultView.as_view(), name='wordlist_result'),
    path('wordlist', views.WordListQueryView.as_view(), name='wordlist'),
    path('word_sketch', views.WordSketchQueryView.as_view(), name='word_sketch'),
    path('word_sketch_result', views.WordSketchResultView.as_view(), name='word_sketch_result'),
    path('collocation', views.CollocationQueryView.as_view(), name='collocation'),
    path('collocation_result', views.CollocationResultView.as_view(), name='collocation_result'),
    path('output_csv', views.output_csv, name='output_csv'),






    # path('create/', UploadCorporaView.as_view(), name='upload')
]
