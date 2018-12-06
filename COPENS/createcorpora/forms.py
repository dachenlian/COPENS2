from django import forms


class UploadCorpusForm(forms.Form):
    zh_name = forms.CharField(max_length=255, initial='噗浪')
    en_name = forms.CharField(max_length=255, initial='Plurk')
    file = forms.FileField(help_text='Filename must be the same as the English name.')
    positional_attrs = forms.CharField(max_length=255, help_text="Please prepend each attribute with a '-P'.",
                                       required=False, initial='-P pos')
    structural_attrs = forms.CharField(max_length=255, help_text="Please prepend each attribute with a '-S'.",
                                       required=False, initial='-S corpus -S text:id -S s')
    is_public = forms.BooleanField(required=False, help_text="Do you want this corpus to be available to the public?")

    def clean_positional_attrs(self):
        cleaned_data = self.cleaned_data['positional_attrs']
        if cleaned_data and not cleaned_data.startswith('-P'):
            raise forms.ValidationError("Positional attributes must begin with -P")

    def clean_structural_attrs(self):
        cleaned_data = self.cleaned_data['structural_attrs']
        if cleaned_data and not cleaned_data.startswith('-S'):
            raise forms.ValidationError("Structural attributes must begin with -S")
