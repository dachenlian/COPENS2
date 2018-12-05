from django.urls import path
from .views import UploadCorporaView, Home

app_name = 'upload'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('create/', UploadCorporaView.as_view(), name='upload')
]
