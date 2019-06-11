from flask import *
from util import *

app = Flask(__name__)


# 按照linux路径命名规则编写

# helper 用于路径的join
def join_path(root, file):
    return root.rstrip('/')+'/'+file


# 首页，用于登陆
@app.route("/", methods=['GET', 'POST'])
def homepage():
    error = None
    if request.method == 'POST':
        error = valid_login(request.form['account'], request.form['password'])
        if not error:
            # print("Start synchronization...")
            # synchronize(request.form['account'])
            # print("Synchronization finished.")
            resp = make_response(redirect('/dropbox'))
            resp.set_cookie('account', request.form['account'], max_age=3600)
            resp.set_cookie('filepath', '/')
            return resp
    resp = make_response(render_template('homepage.html', error=error))
    resp.set_cookie('account', '', max_age=0)
    resp.set_cookie('filepath', '')
    print('Visiting homepage of SmartCloud.')
    return resp


# 主要显示页面，后续所有的显示页面都在这里
@app.route("/dropbox", methods=['GET', 'POST'])
@app.route("/dropbox/", methods=['GET', 'POST'])
@app.route("/dropbox/<path>", methods=['GET', 'POST'])
def dropbox(path=None):
    searching = None
    account = request.cookies['account']
    if request.method == 'POST':
        searching = request.form['searching']
        files = search_files(account, str(searching))
        print('Searching: '+searching)
        filepath = '/'
    else:
        filepath = request.cookies['filepath']
        if path:
            if path == ':root':
                filepath = '/'
            elif path == ':upper':
                filepath = '/'.join(str(filepath).split('/')[:-1]) if filepath != '/' else '/'
                if filepath == '':
                    filepath = '/'
            else:
                path = str(path).replace(':', '/')
                filepath = join_path(filepath, path)
        files = get_files(account, filepath)
    resp = make_response(render_template('dropbox.html', account=account, filepath=filepath,\
                                         files=files, searching=searching))
    resp.set_cookie('filepath', filepath)
    print('Visiting user: '+account+', filepath: '+filepath)
    return resp


# 创建文件夹的功能性url，之后会返回dropbox
@app.route("/new_folder", methods=['POST'])
def new_folder():
    folder_name = request.form['naming']
    print('Make new folder: '+folder_name)
    error = make_new_folder(request.cookies['account'], request.cookies['filepath'], folder_name)
    return redirect('/dropbox')


# 上传文件的功能性url，之后会返回dropbox
@app.route("/upload_file", methods=['POST'])
def upload_file():
    path = request.cookies['filepath']
    files = request.files.getlist('file')
    error = save_files(request.cookies['account'], path, files)
    print('Upload new file.')
    return redirect('/dropbox')


# 下载文件的功能性url，之后会返回dropbox
@app.route("/download_file/<path>", methods=['POST'])
def download_file(path):
    filename = path
    filedir = get_dir(request.cookies['account'], request.cookies['filepath'])
    print('Downloading from: '+filedir+' '+filename)
    return send_from_directory(filedir, filename, as_attachment=True)


# 重命名文件的功能性url，之后会返回dropbox
@app.route("/rename_file/<path>", methods=['POST'])
def rename_file(path):
    path = join_path(request.cookies['filepath'], path)
    target = request.form['naming']
    print('Rename '+path+' to '+target)
    error = rename_at_server(request.cookies['account'], path, target)
    return redirect('/dropbox')


# 删除文件的功能性url，之后会返回dropbox
@app.route("/delete_file/<path>", methods=['POST'])
def delete_file(path):
    path = join_path(request.cookies['filepath'], path)
    print('Delete '+path)
    error = delete_from_server(request.cookies['account'], path)
    return redirect('/dropbox')
