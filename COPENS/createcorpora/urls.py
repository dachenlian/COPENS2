from django.urls import path
from .views import UploadCorporaView, UserPanelView

app_name = 'upload'

urlpatterns = [
    path('', UserPanelView.as_view(), name='home'),
    path('upload/', UploadCorporaView.as_view(), name='upload'),
]
