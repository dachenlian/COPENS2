from django.urls import path
from .views import UploadCorporaView

app_name = 'upload'

urlpatterns = [
    path('', UploadCorporaView.as_view(), name='upload')
]
