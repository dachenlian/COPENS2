import logging

from crispy_forms.helper import FormHelper
from django import forms
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

from createcorpora.models import Corpus, CopensUser



logger = logging.getLogger(__name__)


class ConcordanceForm(forms.Form):
    """
    Form to search databases. Choices are populated with public corpora and a user's corpora, if logged in.
    """

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.user = kwargs.pop('user', AnonymousUser())
        logging.debug('Authenticated!')

        # Generate DB_CHOICES based on AnonymousUser / Logined User
        if isinstance(self.user, AnonymousUser):
            self.DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name}')  # value, label
                           for c in Corpus.objects.filter(Q(is_public=True))]
        else:
            self.copens_user = CopensUser.objects.get(user=self.user)
            self.DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name} / {c.owner}')  # value, label
                           for c in Corpus.objects.filter(Q(owner=self.copens_user) | Q(is_public=True))]
        
        super().__init__(*args, **kwargs)  # must call super() to have access to fields

        # 要搜索的語料庫field
        try:
            self.fields['corpora'] = forms.MultipleChoiceField(
                label="選擇語料庫",
                choices=self.DB_CHOICES,
                widget=forms.CheckboxSelectMultiple,
                initial=self.DB_CHOICES[0]
            )

        except IndexError:
            self.fields['corpora'] = forms.MultipleChoiceField()

    # 要搜索的關鍵字field
    query = forms.CharField(
        max_length=255,
        initial='台北',
        help_text="""
            若要使用CQL，請您直接輸入CQL格式的索引，例 [pos = "V.*"][pos = "N.*"]
        """
    )

    # CHOICES = [(n, n) for n in range(1, 31)]
    # c = forms.ChoiceField(label="Window size", choices=[('a','v')])
    
    # 上下文視窗大小field
    context = forms.IntegerField(
        label='視窗大小',
        widget=forms.NumberInput(attrs={'type': 'range', 'min': 5, 'max': 30}),
        initial=10,
    ) 

    # 是否顯示詞性field
    show_pos = forms.BooleanField(
        label="顯示詞性(POS)",
        required=False
    )


class WordlistForm(forms.Form):
    """
    Form to answer which corpus to generate wordlist.
    """

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.user = kwargs.pop('user', AnonymousUser())
        logging.debug('Authenticated!')

        # Generate DB_CHOICES based on AnonymousUser / Logined User
        if isinstance(self.user, AnonymousUser):
            self.DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name}')  # value, label
                           for c in Corpus.objects.filter(Q(is_public=True))]
        else:
            self.copens_user = CopensUser.objects.get(user=self.user)
            self.DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name} / {c.owner}')  # value, label
                           for c in Corpus.objects.filter(Q(owner=self.copens_user) | Q(is_public=True))]
        
        super().__init__(*args, **kwargs)  # must call super() to have access to fields

        # 要搜索的語料庫field
        try:
            self.fields['corpus'] = forms.ChoiceField(
                label="選擇語料庫",
                choices=self.DB_CHOICES,
                # widget=forms.CheckboxSelectMultiple,
                widget=forms.RadioSelect,
                initial=self.DB_CHOICES[0]
            )

        except IndexError:
            self.fields['corpus'] = forms.ChoiceField()

    # query = forms.CharField(max_length=255, initial='台北',help_text="""若要使用CQL，請您直接輸入CQL格式的索引，例 [pos = "V.*"][pos = "N.*"]""")

    # number_of_words = [(100, 100), (200, 200), (300, 300)]

    # 要顯示幾個詞field
    how_many_words = forms.IntegerField(
        label='詞數',
        widget=forms.NumberInput(attrs={'type': 'range', 'min': 100, 'max': 500}),
        initial=100,
    ) 

class WordSketchForm(forms.Form):
    """
    Form to answer which corpus to generate wordlist.
    """

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.user = kwargs.pop('user', AnonymousUser())
        logging.debug('Authenticated!')

        # Generate DB_CHOICES based on AnonymousUser / Logined User
        if isinstance(self.user, AnonymousUser):
            self.DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name}')  # value, label
                           for c in Corpus.objects.filter(Q(is_public=True))]
        else:
            self.copens_user = CopensUser.objects.get(user=self.user)
            self.DB_CHOICES = [(c.file_name.split('.')[0], f'{c.zh_name} / {c.owner}')  # value, label
                           for c in Corpus.objects.filter(Q(owner=self.copens_user) | Q(is_public=True))]
        
        super().__init__(*args, **kwargs)  # must call super() to have access to fields

        # 要搜索的語料庫field
        try:
            self.fields['corpus'] = forms.ChoiceField(
                label="選擇語料庫",
                choices=self.DB_CHOICES,
                # widget=forms.CheckboxSelectMultiple,
                widget=forms.RadioSelect,
                initial=self.DB_CHOICES[0]
            )

        except IndexError:
            self.fields['corpus'] = forms.ChoiceField()

    # query = forms.CharField(max_length=255, initial='台北',help_text="""若要使用CQL，請您直接輸入CQL格式的索引，例 [pos = "V.*"][pos = "N.*"]""")

    # number_of_words = [(100, 100), (200, 200), (300, 300)]

    # 要搜索的關鍵字field
    query = forms.CharField(
        max_length=255,
        initial='台北',
        help_text="""
            請輸入欲搜尋的詞語
        """
    )