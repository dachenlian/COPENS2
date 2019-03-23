"""
Forms to deal with creating corpora or searching within corpora.
"""

import logging

from django import forms
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

from .models import Corpus, CopensUser

logger = logging.getLogger(__name__)


class UploadCorpusForm(forms.Form):
    """Upload a corpus."""
    zh_name = forms.CharField(max_length=255, initial='中研院平衡語料庫', label='語料庫名稱(中文)')
    en_name = forms.CharField(max_length=255, initial='ASBC', label='語料庫名稱(英文)')
    file = forms.FileField(label='檔案', help_text='檔案名稱必須與語料庫名稱(英文)相同')
    needs_preprocessing = forms.BooleanField(required=False, help_text='我們可以幫您做前處理的部份',
                                             label='自動處理')
    is_public = forms.BooleanField(required=False, help_text="您是否希望公開這份語料庫嗎？",
                                   label='設為公開')
    positional_attrs = forms.CharField(max_length=255, help_text="Please prepend each attribute with a '-P'.",
                                       required=False, initial='-P pos',
                                       label='位置屬性(Positional attributes)')
    structural_attrs = forms.CharField(max_length=255, help_text="Please prepend each attribute with a '-S'.",
                                       required=False, initial='-S text+id -S s -0 corpus',
                                       label='結構屬性(Structural attributes)')

    def clean_positional_attrs(self):
        cleaned_data = self.cleaned_data['positional_attrs']
        if cleaned_data and not cleaned_data.startswith('-P'):
            raise forms.ValidationError("Positional attributes must begin with -P", code='invalid')
        return cleaned_data

    def clean_structural_attrs(self):
        cleaned_data = self.cleaned_data['structural_attrs']
        if cleaned_data and not cleaned_data.startswith('-S'):
            raise forms.ValidationError("Structural attributes must begin with -S", code='invalid')
        return cleaned_data

    def clean_file(self):
        cleaned_data = self.cleaned_data['file']
        if not cleaned_data.name.isascii():
            raise forms.ValidationError("You may only use the characters A to Z, 0 to 9, "
                                        "and simple punctuation in your password.")
        return cleaned_data


class SearchForm(forms.Form):
    """
    Form to search databases. Choices are populated with public corpora and a user's corpora, if logged in.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', AnonymousUser())
        logging.debug('Authenticated!')
        self.copens_user = CopensUser.objects.get(user=self.user)
        self.DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name} / {c.owner}')  # value, label
                           for c in Corpus.objects.filter(Q(owner=self.copens_user) | Q(is_public=True))]
        super().__init__(*args, **kwargs)  # must call super() to have access to fields
        print('self.DB_CHOICES')
        print(self.DB_CHOICES)
        try:
            self.fields['corpora'] = forms.MultipleChoiceField(
                label="選擇語料庫",
                choices=self.DB_CHOICES,
                widget=forms.CheckboxSelectMultiple,
                initial=self.DB_CHOICES[0]
            )
        except IndexError:
            self.fields['corpora'] = forms.MultipleChoiceField()

    query = forms.CharField(max_length=255, initial='台北',
                            help_text="""若要使用CQL，請您直接輸入CQL格式的索引，例 [pos = "V.*"][pos = "N.*"]""")

    CHOICES = [(n, n) for n in range(1, 31)]
 
    context = forms.ChoiceField(label="Window size", choices=CHOICES)
    show_pos = forms.BooleanField(label="顯示詞性(POS)", required=False)

