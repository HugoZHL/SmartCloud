# for functions
import os
import re
import json
import time
import shutil
import hashlib

# System root directory
# make sure file operations needs no 'sudo' under this directory
# keep last character be '/'
ROOT_DIR = 'test/'    # FIXME : change this if necessary
UCONFIG_PATH = os.path.join(ROOT_DIR, 'uconfig.json')



####################################################################
#                       user login and register                    #
####################################################################

def valid_login(account: str, password: str) -> 'str' or None:
    """Validate login

    :param account: str. Account username.
    :param password: str. Account password.
    :return: None or str. None if valid else error message.
    """
    with open(UCONFIG_PATH, 'r') as f:
        uconfig = json.load(f)   # uconfig are username-hash(password) pairs

    # account name not found
    if account not in uconfig.keys():
        return 'Username or password not correct.'

    # password not correct
    hashstr = hashlib.md5()
    hashstr.update(password.encode('utf-8'))
    if uconfig[account] != hashstr.hexdigest():
        return 'Username or password not correct.'

    return None


def register(account: str, password: str) -> 'str' or None:
    """Register a new account. After registration, a home directory
    will be created for this user.

    :param account: str. Account username.
    :param password: str. Account password.
    :return: None or str. None if valid else error message.
    """
    if os.path.exists(UCONFIG_PATH):
        with open(UCONFIG_PATH, 'r') as fr:
            uconfig = json.load(fr)   # uconfig are username-hash(password) pairs
            # if account name conflict
            if account in uconfig.keys():
                return "Username has already been used."
            fr.close()
    else:
        uconfig = {}

    with open(UCONFIG_PATH, 'w') as fw:
        # set username-hash(password) pairs
        hashstr = hashlib.md5()
        hashstr.update(password.encode('utf-8'))
        uconfig[account] = hashstr.hexdigest()
        json.dump(uconfig, fw)
        fw.close()

    # create home directory 'ROOT_DIR/account'
    os.mkdir(os.path.join(ROOT_DIR, account))
    return None


####################################################################
#                       main file operations                       #
####################################################################

# dict.keys() = ['name', 'size', 'time', 'type', 'folder']
# value都是str
# size转化成合适的表示方式：B, KB, MB, GB, 前面加数字，字符串表示
# time为最后修改时间，'2019/04/13 14:07'
# type为文件类型，'dir'表示文件夹，其他的无所谓，但会显示
# folder为所属文件夹，结尾一定是'/'
def get_files(account: str, path: str) -> 'list':
    """Get information of all files under given path.

    :param account: str. Account username.
    :param path: str. File path (user-view).
    :return: list. A list of file information.
        files = [
        {
            'name': 'test',
            'size': '8.93 KB',
            'time': '2019/04/13 14:07',
            'type': 'dir',
            'folder': '/'
        },
        {
            'name': 'test.py',
            'size': '149 B',
            'time': '2018/02/03 07:03',
            'type': 'py',
            'folder': '/'
        }
        ]
    """
    abspath = userpath2abspath(account, path)
    filenames = sorted(os.listdir(abspath))

    files = []
    for name in filenames:
        fpath = os.path.join(abspath, name)
        info = get_file_info(fpath)
        files.append(info)

    return files


# 返回类型同上，用于搜索包含search的文件
def search_files(account: str, search: str) -> 'list':
    """Search for matching files given a search string.

    :param account: str. Account username.
    :param search: str. Search string.
    :return: list. A list of file information. If not found, empty list.
    """
    user_root = userpath2abspath(account, '/')


    result_files = []
    for root, dirs, files in os.walk(user_root):
        for name in dirs + files:
            if search in name:
                info = get_file_info(os.path.join(root, name))
                result_files.append(info)
    return result_files


def make_new_folder(account: str, filepath: str, new_folder: str) -> None or str:
    """ Make a new folder.

    :param account: str. Account username.
    :param filepath: str. Current file path (user-view).
    :param new_folder: str. New folder name.
    :return: None or str. None if succeed else error message.
    """
    abspath = userpath2abspath(account, filepath)
    new_path = os.path.join(abspath, new_folder)
    if os.path.exists(new_path):
        return 'Folder with the same name already exists.'

    os.mkdir(new_path)
    return None


# 给一个account可见的filepath（一个文件夹），返回该文件夹的绝对路径
def get_dir(account: str, filepath: str) -> 'str':
    return userpath2abspath(account, filepath)


# files 是个list，每个元素有filename属性和save(path)方法
# 具体详见https://www.jb51.net/article/62606.htm
def save_files(account: str, filepath: str, files) -> 'None':
    """ Save files under a given folder.

    :param account: str. Account username.
    :param filepath: str. Current file path (user-view).
    :param files: list. A list of saving files.
    :return: None or str. None if succeed else error message.
    """
    abspath = userpath2abspath(account, filepath)
    error = None
    for f in files:
        save_path = os.path.join(abspath, secure_filename(f.filename))
        if os.path.exists(save_path):
            error = 'Covering original files with the same name.'
        f.save(save_path)
    return error


# 将filepath的文件（夹）名字改成target
def rename_at_server(account: str, filepath: str, target: str) -> None or str:
    """ Rename a file or dir.

    :param account: str. Account username.
    :param filepath: str. Source file path (user-view).
    :param target: str. New name.
    :return: None or str. None if succeed else error message.
    """
    abspath = userpath2abspath(account, filepath)

    # check conflict
    pardir = os.path.dirname(abspath)
    filenames = os.listdir(pardir)
    if target in filenames:
        return 'File with the same name already exists in this directory.'

    # check validity
    if '/' in target:
        return "Filename cannot contain special characters."

    new_path = os.path.join(pardir, target)
    os.rename(abspath, new_path)
    return None


def delete_from_server(account: str, filepath: str) -> None or str:
    """ Delete a file or dir.

    :param account: str. Account username.
    :param filepath: str. Target file path (user-view).
    :return: None or str. None if succeed else error message.
    """
    abspath = userpath2abspath(account, filepath)

    if not os.path.exists(abspath):
        return 'Target file not exists.'

    if not os.path.isdir(abspath):
        os.remove(abspath)
    else:
        shutil.rmtree(abspath)
    return None


####################################################################
#                          help functions                          #
####################################################################

def abspath2userpath(fpath: str) -> str:
    """converting absolute path to user-view path
    'ROOT_DIR/username/xxx' ---> '/xxx'
    """
    fpath = fpath[len(ROOT_DIR):].lstrip('/')
    fpath = '/'.join(fpath.split('/')[1:])
    return '/' + fpath


def userpath2abspath(account: str, fpath: str) -> str:
    """converting user-view path to absolute path
    '/xxx' ---> 'ROOT_DIR/username/xxx'
    """
    return ROOT_DIR.rstrip('/') + '/' + account + fpath


def get_dir_size(fdir: str) -> str:
    """get directory true size (summing up all files under it)"""
    size = 0
    for root, dirs, files in os.walk(fdir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


def timestamp2time(timestamp: float) -> str:
    """convert time stamp to formatted time"""
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


def get_file_info(fpath: str) -> dict:
    """Get formatted file information"""
    # get file name
    name = fpath.split('/')[-1]

    # get file size
    fsize = os.path.getsize(fpath) # directory size will always be 4K
    if fsize < 1024:
        fsize = str(fsize)+' B'
    elif fsize < 1024*1024:
        fsize = str(round(fsize/1024, 2))+' KB'
    elif fsize < 1024**3:
        fsize = str(round(fsize/1024**2, 2))+' MB'
    else:
        fsize = str(round(fsize/1024**3, 2))+' GB'

    # get file modify time
    ftime = timestamp2time(os.path.getmtime(fpath))

    # get file type
    if os.path.isdir(fpath):
        ftype = 'dir'
    else:

        ftype = name.split('.')[-1] if '.' in name else ''

    # get file folder (user-view)
    ffolder = abspath2userpath(os.path.dirname(fpath))

    info = {
        'name': name,
        'size': fsize,
        'time': ftime,
        'type': ftype,
        'folder': ffolder
    }
    return info


def secure_filename(filename):
    text_type = str
    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('utf-8', 'ignore')
        filename = filename.decode('utf-8')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9\u4E00-\u9FA5_.-]')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(
                   filename.split()))).strip('._')

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                             'LPT2', 'LPT3', 'PRN', 'NUL')
    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename
    return filename
