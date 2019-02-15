from django.urls import path
from .views import UploadCorporaView, UploadedView, SearchView, ResultsView, DeleteCorpusView


app_name = 'upload'

urlpatterns = [
    path('', UploadCorporaView.as_view(), name='home'),
    path('upload/', UploadCorporaView.as_view(), name='upload'),
    path('uploaded/', UploadedView.as_view(), name='uploaded'),
    path('concordance/', SearchView.as_view(), name='concordance'),
    path('results/', ResultsView.as_view(), name='results'),
    path('delete/<int:pk>', DeleteCorpusView.as_view(), name='delete')
]
