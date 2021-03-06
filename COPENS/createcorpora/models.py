from django.db import models
from django.contrib.auth.models import User


class CopensUser(models.Model):
    class Meta:
        verbose_name_plural = 'COPENS users'
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='copens_user')
    raw_dir = models.CharField(max_length=255)
    data_dir = models.CharField(max_length=255)
    registry_dir = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Corpus(models.Model):
    class Meta:
        verbose_name_plural = 'Corpora'
    owner = models.ForeignKey(CopensUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='corpora')
    en_name = models.CharField(max_length=255)
    zh_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255, default="")
    is_public = models.BooleanField(default=False)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    tcsl_doc_id = models.CharField(max_length=255, default="")
    tcsl_corpus_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return f'{self.en_name} / {self.zh_name} / {self.owner.user.username}'

