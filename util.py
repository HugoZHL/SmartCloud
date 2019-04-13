# for functions


def valid_login(account: str, password: str) -> 'str':
    return None


# dict.keys() = ['name', 'size', 'time', 'type', 'folder']
# value都是str
# size转化成合适的表示方式：B, KB, MB, GB, 前面加数字，字符串表示
# time为最后修改时间，'2019/04/13 14:07'
# type为文件类型，'dir'表示文件夹，其他的无所谓，但会显示
# folder为所属文件夹，结尾一定是'/'
def get_files(account: str, path: str) -> 'list[dict{}]':
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
    return files


# 返回类型同上，用于搜索包含search的文件
def search_files(account: str, search: str) -> 'list[dict{}]':
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
    return files


def delete_from_server(filepath: str) -> 'None':
    # do some deletion
    pass
