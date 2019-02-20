"""
Helper functions to use while uploading a corpus file or making queries.
"""
import json
import logging
import os
import random
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Generator, Optional

import jseg
import pexpect
import requests
from chardet.universaldetector import UniversalDetector
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile
from django.http import request
from django.utils.text import slugify

from .models import CopensUser, Corpus

logger = logging.getLogger(__name__)


def create_text_file(name):
    f = {
        'file': SimpleUploadedFile(name=name, content=bytes('測試資料', encoding='utf8'))
    }
    return f


def save_file_to_drive(file: UploadedFile, raw_dir: Path) -> Optional[str]:
    """
    :param file: A Django UploadedFile file
    :param raw_dir: A path to user uploaded unprocessed corpora files.
    """
    filename = Path(file.name)
    stem, suffix = slugify(filename.stem), filename.suffix
    filename = f'{stem}{suffix}'
    logger.debug(f'Before: {file.name}, after: {filename}, type: {type(filename)}')

    if raw_dir.joinpath(filename).exists():
        return None

    logging.info(f'Received: {filename}, size: {file.size}')
    path = raw_dir / filename
    with open(path, 'wb+') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    logging.info(f'Writing to disk complete.')

    return filename


def delete_files_from_drive(copens_user: CopensUser, corpus: Corpus) -> None:
    """
    Delete a user uploaded corpus
    :param copens_user: An instance of CopensUser
    :param corpus: An instance of Corpus
    :return: None
    """
    raw_path = Path(copens_user.raw_dir) / corpus.file_name
    reg_path = Path(copens_user.registry_dir) / corpus.file_name.split('.')[0]
    data_path = Path(copens_user.data_dir) / corpus.file_name.split('.')[0]

    if corpus.is_public:
        os.unlink(Path(settings.CWB_PUBLIC_REG_DIR) / corpus.en_name.lower())
    try:
        os.remove(raw_path)
        os.remove(reg_path)
        shutil.rmtree(data_path)
    except FileNotFoundError as e:
        logging.warning(f'Cannot find files: {e}')
    else:
        logging.info('Successfully deleted files.')


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
    logger.debug(corpora)
    corpora_results = {}
    registry = f"{settings.CWB_PUBLIC_REG_DIR}"
    if user_registry:
        registry += f":{user_registry}"
    cqp = pexpect.spawn(f'cqp -e -r {registry}', encoding='utf8')
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
    """Read CQP query results from a path"""
    with open(path, errors='ignore') as fp:
        return fp.readlines()[1:-2]  # remove <ul> tags


def get_user_registry(http_request: request) -> str:
    """Get a logged in user's registry directory."""
    user = http_request.user
    if user.is_authenticated:
        registry_dir = CopensUser.objects.get(user=user).registry_dir
        return registry_dir


def detect_encoding(file: Path) -> str:
    """Detect a file's encoding and return it."""

    detector = UniversalDetector()

    with open(file, 'rb') as fp:
        for line in fp:
            detector.feed(line)
            if detector.done:
                break
    detector.close()
    return detector.result.get('encoding')


def read_file_gen(file: Path, encoding: str) -> str:
    """A generator to read a large file lazily."""
    with open(file, encoding=encoding) as fp:
        while True:
            data = fp.readline()
            if not data:
                break
            else:
                yield data


def flatten_list(lst: Generator) -> str:
    """A generator to flatten nested lists."""
    for item in lst:
        if isinstance(item, list):
            for i in item:
                yield i
        else:
            yield item


def segment_and_tag(text: Generator) -> tuple:
    """Use Jieba to segment and tag a text."""
    j = jseg.Jieba()
    for t in text:
        yield j.seg(t, pos=True)


def verticalize_and_save_to_file(text: Generator, input_file: Path, raw_dir: Path) -> str:
    """
    Takes a tokenized list of sentences and outputs to a file in a vertical format.
    This deletes the original raw text and saves a .vrt formatted version in its place.
    :param text: A generator containing a list of tokenized sentences
    :param input_file: A path to the original raw text file
    :param raw_dir: A path to the user's raw directory
    :return:
    """
    logging.debug('Tagging and verticalizing.')
    output_file = f'{input_file.stem}.vrt'
    with open(f'{raw_dir.joinpath(output_file)}', 'w') as fp:
        for sent in text:
            print('<s>', file=fp)
            for token, pos in sent:
                print(f'{token}\t{pos}', file=fp)
            print('</s>', file=fp)
    logging.debug('Save complete.')
    os.remove(input_file)
    logging.debug('Deleted old file.')
    return output_file


def preprocess(input_file: Path, raw_dir: Path) -> None:
    """Takes raw text file, preprocesses it, and saves a verticalized version to disk.
    :param input_file: A raw text file
    :param raw_dir: The path to the user's raw files
    """
    whitespace_regex = re.compile(r'\s')
    sentence_regex = re.compile(r'[！？，。．?!]+')
    encoding = detect_encoding(input_file)
    text = read_file_gen(input_file, encoding=encoding)
    text = filter(bool, (whitespace_regex.sub('', t) for t in text))
    text = (sentence_regex.split(n) for n in text)
    text = filter(bool, flatten_list(text))
    text = segment_and_tag(text)
    verticalize_and_save_to_file(text, input_file, raw_dir=raw_dir)


def create_corpus(copens_user, zh_name, en_name, is_public,
                  file_name: str, registry_dir):  # , tcsl_doc_id, tcsl_corpus_name, tcsl_upload_success):
    """Create a corpus. To be used asynchronously."""
    logging.debug('Creating corpus entry...')
    # if tcsl_upload_success:
    Corpus.objects.create(
        owner=copens_user,
        zh_name=zh_name,
        en_name=en_name,
        is_public=is_public,
        file_name=file_name,
        # tcsl_doc_id=tcsl_doc_id,
        # tcsl_corpus_name=tcsl_corpus_name
    )
    # else:
    #     Corpus.objects.create(
    #         owner=copens_user,
    #         zh_name=zh_name,
    #         en_name=en_name,
    #         is_public=is_public,
    #         file_name=file_name,
    #     )
    if is_public:
        print('Making public...')
        os.link(registry_dir.joinpath(file_name.split('.')[0]),
                Path(settings.CWB_PUBLIC_REG_DIR).joinpath(file_name.split('.')[0].lower()),
                )


class TCSL:
    LOGIN_PATH = 'user/login'
    UPLOAD_PATH = 'document'
    CREATE_CORPUS_PATH = 'corpus'

    def __init__(self):
        # Login at initial step
        self.session = requests.Session()
        self.tcsl_doc_id = ''
        self.tcsl_corpus_name = ''
        headers = {'Content-Type': 'application/json'}
        request_body_for_login = {
            'uname': settings.TCSL_USERNAME,
            'passwd': settings.TCSL_PASSWORD
        }
        res = self.session.post(settings.TCSL_ENDPOINT + TCSL.LOGIN_PATH, headers=headers,
                                data=json.dumps(request_body_for_login))

    def upload(self, file, file_path):
        encoding = detect_encoding(file_path)

        data = {
            'text': file.read().decode(encoding),
            'metadata': {
                'hashtags': ''
            }
        }

        file.seek(0)
        headers = {'Content-Type': 'application/json'}

        try:
            logging.info('Start uploading to TCSL ...')
            r = self.session.post(settings.TCSL_ENDPOINT + TCSL.UPLOAD_PATH, headers=headers, data=json.dumps(data))
            json_result = r.json()

            if json_result['status'] == 'ok' and json_result['textid'] is not None:
                self.tcsl_doc_id = json_result['textid']['json']
                self.tcsl_corpus_name = f'{file.name}_{str(int(time.time()))}'
                create_corpus_success = self._create_corpus(self.tcsl_doc_id, self.tcsl_corpus_name)
                if not create_corpus_success:
                    logging.info('Failed to create a corpus in TCSL')

                    return False
        except Exception as e:
            logging.info(f'An Exception is raised during uploading to TCSL: {e}')
            return False

        return True

    def _create_corpus(self, doc_id, corpus_name):
        headers = {'Content-Type': 'application/json'}
        data = {
            "corpusname": corpus_name,
            "documents": [doc_id]
        }
        r = self.session.post(settings.TCSL_ENDPOINT + TCSL.CREATE_CORPUS_PATH, headers=headers, data=json.dumps(data))
        json_result = r.json()
        if json_result['status'] == 'ok':
            return True
        else:
            return False
