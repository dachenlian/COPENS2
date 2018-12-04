"""
Helper functions to use while uploading a corpus file.
"""
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from pathlib import Path
import logging
import subprocess


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=Path(settings.BASE_DIR).joinpath('debug.log'),
                    filemode='w'
                    )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger(__name__).addHandler(console)


def save_file_to_drive(file: UploadedFile) -> None:
    """
    :param file: A Django UploadedFile file
    """
    name = file.name
    logging.info(f'Received: {name}, size: {file.size}')
    path = Path(settings.CWB_RAW_DIR) / name
    with open(path, 'wb+') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    logging.info(f'Writing to disk complete.')


def cwb_encode(vrt_file: Path, p_attrs: str, s_attrs: str) -> None:
    """
    Encode a verticalized XML file as a CWB corpus.
    :param vrt_file: A path to a verticalized XML file
    :param p_attrs: A string describing all positional attributes of the corpus
    :param s_attrs: A string describing all structural attributes of the corpus
    :return:
    """
    name = vrt_file.stem
    data_dir = Path(settings.CWB_DATA_DIR) / name
    reg_dir = Path(settings.CWB_REGISTRY_DIR) / name
    if not data_dir.exists():
        data_dir.mkdir()

    command = f"cwb-encode -d {data_dir} -f {vrt_file} -R {reg_dir} {p_attrs} {s_attrs} -c utf8"

    result = subprocess.run(command, shell=True, capture_output=True)
    if result.returncode != 0:
        logging.exception(f'cwb-encode exception occurred, ARGS: {result.args}\nSTDOUT:{result.stdout}\nERROR:{result.stderr}')
    else:
        logging.info('Successfully encoded .vrt file.')


def cwb_make(vrt_file: str) -> None:
    """
    Index and compress an encoded corpus.
    :param vrt_file: A path to a verticalized XML file.
    """
    name = vrt_file.upper()

    command = f"cwb-make --validate {name} --registry {settings.CWB_REGISTRY_DIR} --memory 500"

    result = subprocess.run(command, shell=True, capture_output=True)
    if result.returncode != 0:
        logging.exception(f'cwb-make exception occurred, ARGS: {result.args}\nSTDOUT:{result.stdout}\nERROR:{result.stderr}')
    else:
        logging.info('Successfully indexed and compressed corpus.')



