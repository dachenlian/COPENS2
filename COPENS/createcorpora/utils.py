"""
Helper functions to use while uploading a corpus file or making queries.
"""
from pathlib import Path
import logging
import subprocess
import random
import sys
import os
import shutil

from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.http import request
import pexpect

from .models import CopensUser, Corpus


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


def save_file_to_drive(file: UploadedFile, raw_dir: Path) -> None:
    """
    :param file: A Django UploadedFile file
    :param raw_dir: A path to user uploaded unprocessed corpora files.
    """
    name = file.name
    logging.info(f'Received: {name}, size: {file.size}')
    path = raw_dir / name
    with open(path, 'wb+') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    logging.info(f'Writing to disk complete.')


def delete_files_from_drive(copens_user: CopensUser, corpus: Corpus) -> None:
    """
    Delete a user uploaded corpus
    :param copens_user: An instance of CopensUser
    :param corpus: An instance of Corpus
    :return: None
    """
    raw_path = Path(copens_user.raw_dir) / corpus.file_name
    reg_path = Path(copens_user.registry_dir) / corpus.en_name.lower()
    data_path = Path(copens_user.data_dir) / corpus.en_name.lower()

    if corpus.is_public:
        os.unlink(Path(settings.CWB_PUBLIC_REG_DIR) / corpus.en_name.lower())
    try:
        os.remove(raw_path)
        os.remove(reg_path)
        shutil.rmtree(data_path)
    except FileNotFoundError as e:
        logging.warning(f'Cannot find files: {e}')


def cwb_encode(vrt_file: Path, data_dir: Path, registry_dir: Path, p_attrs: str, s_attrs: str) -> None:
    """
    Encode a verticalized XML file as a CWB corpus.
    :param vrt_file: A path to a verticalized XML file
    :param data_dir: A path to corpus binary files.
    :param registry_dir: A path to a user's registry.
    :param p_attrs: A string describing all positional attributes of the corpus
    :param s_attrs: A string describing all structural attributes of the corpus
    :return: None
    """
    name = vrt_file.stem  # filename without suffix
    data_dir = data_dir / name
    registry_dir = registry_dir / name
    if not data_dir.exists():
        data_dir.mkdir()

    command = f"cwb-encode -d {data_dir} -f {vrt_file} -R {registry_dir} -xsB {p_attrs} {s_attrs} -c utf8"
    print(f'Command: {command}')

    result = subprocess.run(command, shell=True, capture_output=True)
    if result.returncode != 0:
        logging.exception(
            f'cwb-encode exception occurred, ARGS: {result.args}\nSTDOUT:{result.stdout}\nERROR:{result.stderr}')
    else:
        logging.info('Successfully encoded .vrt file.')


def cwb_make(vrt_file: str, registry_dir: Path) -> None:
    """
    Index and compress an encoded corpus.
    :param vrt_file: A path to a verticalized XML file.
    :param registry_dir: A path to the user's registry.
    """
    name = vrt_file.upper()

    command = f"cwb-make --validate {name} --registry {registry_dir} --memory 500"

    result = subprocess.run(command, shell=True, capture_output=True)
    if result.returncode != 0:
        logging.exception(
            f'cwb-make exception occurred, ARGS: {result.args}\nSTDOUT:{result.stdout}\nERROR:{result.stderr}')
    else:
        logging.info('Successfully indexed and compressed corpus.')


def cqp_query(query: str, corpora: list, show_pos=False, context=None, user_registry=None) -> dict:
    """
    Use pexpect to send queries to cqp and write to file. Then, open and read said file and return contents.
    :param query: A query to be entered into the cqp program.
    :param corpora: A list of corpora for a query to be searched against.
    :param show_pos: Show part of speech for each token.
    :param context: Context size around the query.
    :param user_registry: A path to the user's personal registry.
    :return: A dictionary containing corpora as keys and filenames where query results can be read from as values.
    """
    corpora_results = {}
    registry = f"{settings.CWB_PUBLIC_REG_DIR}"
    if user_registry:
        registry += f":{user_registry}"
    cqp = pexpect.spawn(f'cqp -e -r {registry}', encoding='utf8')
    cqp.logfile_read = sys.stdout
    if context:
        cqp.write(f'set CONTEXT {context};')
    if '[' not in query:
        query_command = f"'{query}';"
    else:
        query_command = f"""{query};"""  # cqp search
    logging.info(f'Query received: {query}')

    for corpus in corpora:
        filename = f'{random.randint(1, 1000000000)}.txt'
        path = Path(settings.CWB_QUERY_RESULTS_DIR) / filename

        commands = [
            'set AutoShow off;',
            'set PrintMode html;'
            f'{corpus.upper()};',
            f'show -cpos;',  # corpus position
            query_command,
            f"cat > '{path}';",
        ]
        if show_pos:
            commands.insert(-2, 'show +pos;')
        for c in commands:
            cqp.sendline(c)  # must send a linesep to work

        corpora_results[corpus] = path
    cqp.sendline('exit;')
    return corpora_results


def read_results(path: str):
    with open(path) as fp:
        return fp.readlines()[1:-2]  # remove <ul> tags


def get_user_registry(http_request: request):
    user = http_request.user
    if user.is_authenticated:
        registry_dir = CopensUser.objects.get(user=user).registry_dir
        return registry_dir
