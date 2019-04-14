from flask import *
from util import *
import os

app = Flask(__name__)


def join_path(root, file):
    return root.rstrip('/')+'/'+file


@app.route("/", methods=['GET', 'POST'])
def homepage():
    error = None
    if request.method == 'POST':
        error = valid_login(request.form['account'], request.form['password'])
        if not error:
            resp = make_response(redirect('/dropbox'))
            resp.set_cookie('account', request.form['account'], max_age=3600)
            resp.set_cookie('filepath', '/')
            return resp
    resp = make_response(render_template('homepage.html', error=error))
    resp.set_cookie('account', '', max_age=0)
    resp.set_cookie('filepath', '')
    return resp


@app.route("/dropbox", methods=['GET', 'POST'])
@app.route("/dropbox/", methods=['GET', 'POST'])
@app.route("/dropbox/<path>", methods=['GET', 'POST'])
def dropbox(path=None):
    searching = None
    account = request.cookies['account']
    if request.method == 'POST':
        searching = request.form['searching']
        files = search_files(account, searching)
        filepath = '/'
    else:
        filepath = request.cookies['filepath']
        if path:
            filepath = '/' if path == ':root' else join_path(filepath, path)
        files = get_files(account, filepath)
    resp = make_response(render_template('dropbox.html', account=account, filepath=filepath,\
                                         files=files, searching=searching))
    resp.set_cookie('filepath', filepath)
    print(account, filepath)
    return resp


@app.route("/new_folder", methods=['POST'])
def new_folder():
    folder_name = request.form['naming']
    print('Make new folder: '+folder_name)
    make_new_folder(request.cookies['account'], request.cookies['filepath'], folder_name)
    return redirect('/dropbox')


@app.route("/upload_file", methods=['POST'])
def upload_file():
    path = request.cookies['filepath']
    files = request.files.getlist('file')
    save_files(request.cookies['account'], path, files)
    print('new file: ')
    return redirect('/dropbox')


@app.route("/download_file/<path>", methods=['POST'])
def download_file(path):
    filename = path
    filedir = get_dir(request.cookies['account'], request.cookies['filepath'])
    print('downloading from: '+filedir+' '+filename)
    return send_from_directory(filedir, filename, as_attachment=True)


@app.route("/rename_file/<path>", methods=['POST'])
def rename_file(path):
    path = join_path(request.cookies['filepath'], path)
    target = request.form['naming']
    print('rename '+path+' to '+target)
    rename_at_server(request.cookies['account'], path, target)
    return redirect('/dropbox')


@app.route("/delete_file/<path>", methods=['POST'])
def delete_file(path):
    path = join_path(request.cookies['filepath'], path)
    print('delete '+path)
    delete_from_server(request.cookies['account'], path)
    return redirect('/dropbox')
