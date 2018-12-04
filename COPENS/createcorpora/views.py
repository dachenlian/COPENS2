from pathlib import Path
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.conf import settings

from .forms import UploadCorpusForm
from . import utils


class UploadCorporaView(FormView):
    template_name = 'createcorpora/index.html'
    form_class = UploadCorpusForm
    success_url = reverse_lazy('create:upload')

    def form_valid(self, form):
        file = self.request.FILES['file']
        p_attrs = self.request.POST['positional_attrs']
        s_attrs = self.request.POST['structural_attrs']
        utils.save_file_to_drive(file)
        utils.cwb_encode(Path(settings.CWB_RAW_DIR) / file.name, p_attrs=p_attrs, s_attrs=s_attrs)
        utils.cwb_make(Path(file.name).stem)
        return super().form_valid(form)


