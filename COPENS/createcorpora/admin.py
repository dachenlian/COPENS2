from django.contrib import admin
from .models import CopensUser, Corpus

# Register your models here.

admin.site.register(CopensUser)
admin.site.register(Corpus)
