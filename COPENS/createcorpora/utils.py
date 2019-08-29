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
from threading import Thread
import math
import multiprocessing
from queue import Queue

import jseg
import pexpect
import requests
from chardet.universaldetector import UniversalDetector
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile
from django.http import request
from django.utils.text import slugify

from .models import CopensUser, Corpus
from .PyCQP import CQP

logger = logging.getLogger(__name__)


def create_text_file(name):
    f = {
        'file': SimpleUploadedFile(name=name, content=bytes('測試資料', encoding='utf8'))
    }
    return f

def does_file_already_exist(file: UploadedFile, raw_dir: Path) -> Optional[str]:
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
    else:
        return filename

def save_file_to_drive(file: UploadedFile, raw_dir: Path) -> Optional[str]:
    """
    :param file: A Django UploadedFile file
    :param raw_dir: A path to user uploaded unprocessed corpora files.
    """
    filename = Path(file.name)
    stem, suffix = slugify(filename.stem), filename.suffix
    filename = f'{stem}{suffix}'
    # logger.debug(f'Before: {file.name}, after: {filename}, type: {type(filename)}')

    # if raw_dir.joinpath(filename).exists():
    #     return None

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
    :param data_dir: A path to corpus binary files
    :param registry_dir: A path to a user's registry
    :param p_attrs: A string describing all positional attributes of the corpus
    :param s_attrs: A string describing all structural attributes of the corpus
    :return: None
    """
    name = vrt_file.stem  # filename without suffix
    name_without_special_char = name.split('.')[0]
    logging.info(f"!!!! name: {name}")
    logging.info(f"!!!! name_without: {name_without_special_char}")

    data_dir = data_dir / name
    registry_dir = registry_dir / name_without_special_char
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
    :param context: Context (window) size around the query.
    :param user_registry: A path to the user's personal registry.
    :return: A dictionary containing corpora as keys and filenames where query results can be read from as values.
    """
    print('@@@@@@')
    logger.debug(corpora)
    corpora_results = {}
    registry = f"{settings.CWB_PUBLIC_REG_DIR}"
    if user_registry:
        registry += f":{user_registry}"
    logger.debug(registry)

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
            f'{query_command}',
            f"cat > '{path}';",
        ]
        logger.debug(commands)

        if show_pos:
            commands.insert(-2, 'show +pos;')
        for c in commands:
            cqp.sendline(c)  # must send a linesep to work

        time.sleep(4)
        corpora_results[corpus] = path
    cqp.sendline('exit;')

    logging.info(corpora_results)

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


# 20190215 Update: query wordlist
def cqp_query_wordlist(corpus: str, user_registry=None, how_many_words=20):
    """
    Use pexpect to send queries to cwb-lexdecode and write to file. Then, open and read said file and return contents.
    :param corpus: A corpus for a query to be searched against.
    :param user_registry: A path to the user's personal registry.
    :return: A dictionary containing corpora as keys and filenames where query results can be read from as values.
    """
    logger.debug(corpus)
    wordlist_result = []
    filename = f'wordlist_{corpus}.txt'
    path = Path(settings.CWB_QUERY_RESULTS_DIR) / filename

    if path.exists():
        logger.debug('file exists!')
    else:
        registry = f"{settings.CWB_PUBLIC_REG_DIR}"
        if user_registry:
            registry += f":{user_registry}"

        # See chapter 7 of "CWB Encoding Tutorial Documentation"
        # shell_cmd = 'ls -l | grep LOG > logs.txt'
        # query_cmd = f'cwb-lexdecode -r {registry} -f {corpus.upper()} | sort -nr -k 1 | head -{how_many_words} > {path}'
        # query_cmd = f'cwb-lexdecode -r {registry} -f {corpus.upper()} | sort -nr -k 1 > {path}'
        # child = pexpect.spawn('/bin/bash', ['-c', query_cmd], encoding='utf8')
        # child.expect(pexpect.EOF)
        generate_wordlist(registry, corpus, path)

    with open(path, 'r') as f:
        # output = f.read()
        for nth_line, line in enumerate(f):
            if nth_line < how_many_words:
                wordlist_result.append(line)
            else:
                break
    # the output is just String, need transform to Python list or JSON

    # logging.info(f'Wordlist query: {query_cmd}')
    # logging.info(f'output: {output}')
    # wordlist_result = output.split('\n')

    return wordlist_result

def generate_wordlist(registry, corpus, wordlist_path):
    """
    呼叫 cwb-lexdecode 指令，產生詞頻表，並儲存成文件。

    """
    query_cmd = f'cwb-lexdecode -r {registry} -f {corpus.upper()} | sort -nr -k 1 > {wordlist_path}'
    child = pexpect.spawn('/bin/bash', ['-c', query_cmd], encoding='utf8')
    child.expect(pexpect.EOF)
    return

# 20190215 Update: query wordsketch
def cqp_query_word_sketch(query: str, corpus: str, user_registry=None, how_many_words=20):
    """
    Use pexpect to send queries to cwb-lexdecode and write to file. Then, open and read said file and return contents.
    :param corpus: A corpus for a query to be searched against.
    :param user_registry: A path to the user's personal registry.
    :return:
        query_word_freq (int): 查詢關鍵字在語料中的總詞頻
        r (dict): {
            "and_or": 
        } 
    """
    logger.info(corpus)
    start_time = time.time()

    all_relevent_words = set()
    r = {}

    registry = f"{settings.CWB_PUBLIC_REG_DIR}"
    if user_registry:
        registry += f":{user_registry}"
    
    wordlist_result = []
    wordlist_filename = f'wordlist_{corpus}.txt'
    wordlist_path = Path(settings.CWB_QUERY_RESULTS_DIR) / wordlist_filename

    rand = random.randint(1, 1000000000)


    sketch_dict = {
        "N": [
            "measure",
            "and_or",
            "possession_of",
            "possessor_of",
            "n_modifies",
            "n_modifier",
            "a_modifier"
        ]
    }


    codist_path = Path(settings.CWB_QUERY_RESULTS_DIR) / f'{rand}_codist_{query}.txt'
    logging.debug(codist_path)

    # 確認該語料庫是否已經存在wordlist
    if wordlist_path.exists():
        logger.debug('wordlist exists!')
    else:
        logger.debug('wordlist not exists!')
        logger.debug('generate one!')
        generate_wordlist(registry, corpus, wordlist_path)
        
    registry = f"{settings.CWB_PUBLIC_REG_DIR}"
    if user_registry:
        registry += f":{user_registry}"

    cqp = CQP(bin='cqp', options=f'-c -r {registry}')

    ini_commands = [
        'set AutoShow off;',
        f'{corpus.upper()};',
        'show -cpos;',  # corpus position
        'define macro < "/app/COPENS/cwb/macros/macro.txt"',
    ]

    for c in ini_commands:
        # cqp.sendline(c)
        cqp.Exec(c)


    # 先看query的詞，在語料庫中有哪些詞性
    cqp.Exec(f'ALL = [word = "{query}"];')
    cqp.Exec(f'count ALL by pos > "{codist_path}";')
    cqp.Terminate()
    # time.sleep(0.3)

    # parse 該詞的所有詞性的文字檔，並把該詞的每個詞性存進pos
    with open(f"{codist_path}", "r") as f:
        t = f.read()
        parsed_t = [p.split('\t') for p in t.split('\n') if p != '']
        logging.debug(t)

    pos = [p[-1] for p in parsed_t]

    query_word_freq = sum([int(p[0]) for p in parsed_t])

    # 該詞最頻繁的pos
    most_common_pos = pos[0]

    logging.debug(f'所有該詞的詞性：{pos}')
    logging.debug(f'最高頻的詞性：{most_common_pos}')
    logging.debug(f'該詞的總頻率：{query_word_freq}')


    qqq = time.time()

    # 根據不同詞性呼叫不同的word sketch，並分別寫入到不同檔案
    # 應該是花最多時間的地方
    q = multiprocessing.Queue()
    if most_common_pos[0] == 'N':

        for i, sketch in enumerate(sketch_dict['N']):
            # threads = [WordSketchGetter(query, sketch, rand, registry, corpus) for sketch in sketch_dict['N']]
            # def word_sketch_subprocess(query, registry, corpus, sketch, rand):
            processes = [multiprocessing.Process(target=word_sketch_subprocess, args=(query, registry, corpus, sketch, rand, q)) for sketch in sketch_dict['N']]
        
        # for thread in threads:
        #     thread.start()

        # for thread in threads:
        #     thread.join()
        for process in processes:
            process.start()

        for process in processes:
            process.join()

    elif most_common_pos[0] == 'V':
        pass
    else:
        pass

    qqqq = time.time()

    logging.debug("HOLY QUEUE!!!")
    while not q.empty():
        _sketch, _result = q.get()
        if len(_result) != 0:
            relation_freq, result = parse_txt_generated_by_cqp_2(_result)
            r[_sketch] = {
                "freq": relation_freq,
                "result": result
            }
            all_relevent_words.update(result.keys())
        
        # logging.debug(q.get())
        logging.debug(_sketch)
        logging.debug(_result)

    logging.debug(f"r: {r}")


    # 讀取所有產生的檔案
    # p = Path(settings.CWB_QUERY_RESULTS_DIR)
    
    # for path in p.glob(f"{rand}_[!c]*.txt"):
    #     file_name = f"{rand}_([\w_]+)_{query}"
    #     ptn = re.compile(file_name)
    #     sketch = re.search(ptn, str(path)).group(1)

    #     with open(path, 'r') as f:
    #         lines = f.readlines()
            
    #         # parse each text
    #         relation_freq, result = parse_txt_generated_by_cqp(lines)

    #         if result is not None:
    #             r[sketch] = {
    #                 "freq": relation_freq,
    #                 "result": result
    #             }
    #             all_relevent_words.update(result.keys())

    #         logging.debug(result)
    #         logging.debug(all_relevent_words)

    b = time.time()
    logging.debug(all_relevent_words)
    logging.debug(f"整個函式花掉的時間: {str(b - start_time)}")
    logging.debug(f"一一執行cqp的時間: {qqqq-qqq}")
    
    # 將讀好的 result 與詞頻表作對照，得出檢定量 
    wordlist_freq_table = {}
    with open(wordlist_path, 'r') as f:
        for line in f:
            l = line.split()
            if len(l) > 0 and l[1] in all_relevent_words:
                wordlist_freq_table[l[1]] = int(l[0])

    logging.debug(f"詞頻表中的頻率: {wordlist_freq_table}")

    a = {}

    # for sketch_name, word_dict in r.items():
    #     for word, freq in word_dict.items():
    #         r[sketch_name]['result'][word] = (freq, wordlist_freq_table[word])

    for sketch_name in r:
        w1_r = r[sketch_name]["freq"]
        for word in r[sketch_name]["result"]:
            w2 = wordlist_freq_table[word]
            r[sketch_name]["result"][word] = {
                "freq": r[sketch_name]["result"][word],
                "log_dice": log_dice(r[sketch_name]["result"][word], w1_r, w2)
            }

        r[sketch_name]["result"] = sorted(r[sketch_name]["result"].items(), key = lambda x: x[1]["log_dice"], reverse=True)

    logging.debug(r)
    return query_word_freq, r

def parse_txt_generated_by_cqp(lines):
    result = {}
    freq = 0

    if len(lines) == 0:
        return None, None

    for line in lines:
        if line == '':
            continue

        l = line.split('\t')
        result[l[0].strip()] = int(l[1].strip())
        freq += int(l[1].strip())

    return freq, result

def parse_txt_generated_by_cqp_2(string):
    """
    input: "醫學院\t12\n工學院\t8\n市長\t7\n地區\t6\n縣市\t5\n都會區\t5"
    """
    result = {}
    freq = 0

    pairs = [pair.split('\t') for pair in string.split('\n')]

    for pair in pairs:
        word = pair[0].strip()
        word_freq = int(pair[1].strip())
        result[word] = word_freq
        freq += word_freq

    return freq, result

def log_dice(w1_r_w2, w1_r, w2):
    return round(14 + math.log(2 * w1_r_w2 / (w1_r + w2), 2), 2)

class WordSketchGetter(Thread):
    def __init__(self, query, sketch, rand, registry, corpus):
        super().__init__()
        self.query = query
        self.rand = rand
        self.sketch = sketch
        self.registry = registry
        self.corpus = corpus

    def run(self):
        path = Path(settings.CWB_QUERY_RESULTS_DIR) / f'{self.rand}_{self.sketch}_{self.query}.txt'

        logging.debug(path)
        r = random.randint(1, 100000)

        logging.debug(self.registry)
        logging.debug(self.corpus)

        # 啟動 cqp + initial cmd
        cqp = CQP(bin='cqp', options=f'-c -r {self.registry}')

        ini_commands = [
            f'{self.corpus.upper()};',
            'show -cpos;',  # corpus position
            'define macro < "/app/COPENS/cwb/macros/macro.txt"',
        ]

        for c in ini_commands:
            cqp.Exec(c)

        cqp.Exec(f'A{r} = /{self.sketch}["{self.query}"]')
        cqp.Exec(f'group A{r} target word cut 5 > "{path}";')
        cqp.Terminate()

def word_sketch_subprocess(query, registry, corpus, sketch, rand, q):
    path = Path(settings.CWB_QUERY_RESULTS_DIR) / f'{rand}_{sketch}_{query}.txt'

    logging.debug(path)
    r = random.randint(1, 100000)

    logging.debug(registry)
    logging.debug(corpus)

    # 啟動 cqp + initial cmd
    cqp = CQP(bin='cqp', options=f'-c -r {registry}')

    ini_commands = [
        f'{corpus.upper()};',
        'show -cpos;',  # corpus position
        'define macro < "/app/COPENS/macros/macro.txt"',
    ]

    for c in ini_commands:
        cqp.Exec(c)

    # cqp.Exec(f'A{r} = /{sketch}["{query}"]')
    # cqp.Exec(f'group A{r} target word cut 5 > "{path}";')
    cqp.Exec(f'/{sketch}["{query}"]')
    result = cqp.Group(subcorpus='Last', cutoff='5', spec1='target.word')
    cqp.Terminate()
    q.put((sketch, result))
    # return result