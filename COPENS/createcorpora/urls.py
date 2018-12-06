from django.urls import path
from .views import UploadCorporaView, Home, SearchView, ResultsView

app_name = 'upload'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('create/', UploadCorporaView.as_view(), name='upload'),
    path('search/', SearchView.as_view(), name='search'),
    path('results/', ResultsView.as_view(), name='results'),
]
