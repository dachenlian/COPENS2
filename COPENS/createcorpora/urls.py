from django.urls import path
from .views import UploadCorporaView, Home, SearchView, ResultsView, UserPanelView


app_name = 'upload'

urlpatterns = [
    path('', UserPanelView.as_view(), name='home'),
    path('upload/', UploadCorporaView.as_view(), name='upload'),
    path('search/', SearchView.as_view(), name='search'),
    path('results/', ResultsView.as_view(), name='results'),
]
