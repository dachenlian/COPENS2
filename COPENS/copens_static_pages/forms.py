import logging

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