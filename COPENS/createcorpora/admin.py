from django.contrib import admin
from .models import CopensUser, Corpus

# Register your models here.


class CorpusInline(admin.TabularInline):
    model = Corpus


class CopensUserAdmin(admin.ModelAdmin):
    inlines = [
        CorpusInline
    ]


admin.site.register(CopensUser, CopensUserAdmin)
admin.site.register(Corpus)
