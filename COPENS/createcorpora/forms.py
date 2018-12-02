from django import forms


class UploadCorpusForm(forms.Form):
    zh_name = forms.CharField(max_length=255)
    en_name = forms.CharField(max_length=255)
    file = forms.FileField(help_text='Filename must be the same as the English name.')
