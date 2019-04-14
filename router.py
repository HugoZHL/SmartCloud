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





#
# @app.route("/sections", methods=['POST', 'GET'])
# def show_all_sections():
#     if request.method == 'POST':
#         searching = request.form['searching']
#         return redirect('/searchresult/%s' % searching)
#     try:
#         username = request.cookies["username"]
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         is_master = list(map(int, request.cookies["is_master"].split(","))) if request.cookies["is_master"] else []
#         sections = get_sections()
#         return render_template("allsections.html", username=username, sections=sections, admin=is_admin, master=is_master)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/section/<int:section_id>", methods=['POST', 'GET'])
# def show_section(section_id):
#     try:
#         username = request.cookies["username"]
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         is_master = list(map(int, request.cookies["is_master"].split(","))) if request.cookies["is_master"] else []
#         master = section_id in is_master
#         if request.method == 'POST':
#             return result_page(request.form["searching"])
#         make_section_xml(section_id)
#         return render_template("section.html", username=username, section_id=section_id, admin=is_admin, master=master)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/add_post", methods=['POST'])
# def add_post():
#     title = request.form['title']
#     content = request.form['content']
#     section_id = request.form['blockID']
#     try:
#         userID = request.cookies["userID"]
#         add_postTo(userID, section_id, title, content)
#         return redirect('/section/%s' % section_id)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
#
#
#
# @app.route("/edit_section/<int:section_id>", methods=['POST', 'GET'])
# def edit_section(section_id):
#     error = None
#     try:
#         username = request.cookies["username"]
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         is_master = list(map(int, request.cookies["is_master"].split(","))) if request.cookies["is_master"] else []
#         if not is_admin and section_id not in is_master:
#             print("Not authorized!")
#             return redirect('/')
#         if request.method == 'POST':
#             sec = {}
#             sec['name'] = request.form['section_name']
#             sec['description'] = request.form['description']
#             if "master" in request.form: sec['master'] = request.form['master']
#             error = update_section(section_id, sec)
#             if error:
#                 render_template("editsection.html", username=username, id=section_id, admin=is_admin, sec=sec,
#                                 error=error)
#             else:
#                 return redirect('/section/%s' % section_id)
#         sec = sec_information(section_id)
#         return render_template("editsection.html", username=username, id=section_id, admin=is_admin, sec=sec, error=error)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/add_section", methods=['POST', 'GET'])
# def add_section():
#     error = None
#     try:
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         if not is_admin:
#             print("Not authorized!")
#             return redirect('/sections')
#         if request.method == 'POST':
#             sec = {}
#             sec['name'] = request.form['section_name']
#             sec['description'] = request.form['description']
#             sec['master'] = request.form['master']
#             section_id, error = add_sectionTo(sec)
#             if error:
#                 render_template("add_section.html", error=error)
#             else:
#                 return redirect('/section/%s' % section_id)
#         return render_template("add_section.html", error=error)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/delete_section/<int:section_id>", methods=['POST', 'GET'])
# def delete_section(section_id):
#     try:
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         if not is_admin:
#             print("Not authorized!")
#             return redirect('/sections')
#         delete_sectionFromDB(section_id)
#         return redirect('/sections')
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
#
# @app.route("/post", methods=['POST'])
# @app.route("/post/<int:post_id>", methods=['GET', 'POST'])
# def show_post(post_id=0):
#     try:
#         if request.method == 'POST' and "searching" in request.form:
#             return result_page(request.form['searching'])
#         if post_id==0:
#             post_id = request.form['real_id']
#         username = request.cookies["username"]
#         admin = True if request.cookies["is_admin"] == 'True' else False
#         add_click(post_id)
#         make_post_xml(post_id)
#         section_id = getSectionFromPost(post_id)
#         return render_template("post.html", sectionid=section_id, username=username, post_id=post_id, admin=admin)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/add_reply", methods=['POST'])
# def add_reply():
#     post_id = request.form['postingID']
#     replyContent = request.form['reply']
#     try:
#         userID = request.cookies["userID"]
#         add_replyTo(userID, post_id, replyContent)
#         return redirect("/post/%s" % post_id)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
#
#
# @app.route("/add_praise", methods=['POST'])
# def add_praise():
#     reply_id = request.form['praising']
#     add_praiseTo(reply_id)
#     try:
#         post_id = get_postFromReply(reply_id)
#         return redirect('/post/%s' % post_id)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/profile", methods=['POST', 'GET'])
# @app.route("/profile/<int:user_id>", methods=['POST', 'GET'])
# def show_profile(user_id=0):
#     try:
#         if request.method == 'POST':
#             searching = request.form['searching']
#             return redirect('/searchresult/%s' % searching)
#         if user_id == 0: user_id = int(request.cookies['userID'])
#         username = request.cookies['username']
#         target_username = get_usernameFromID(user_id)
#         admin = True if request.cookies["is_admin"] == 'True' else False
#         authorized = True if int(request.cookies["userID"]) == user_id else False
#         make_user_xml(user_id)
#         return render_template("profile.html", username=username,target_username=target_username, admin=admin, authorized=authorized)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/edit_profile", methods=['POST','GET'])
# def edit_profile():
#     error = None
#     try:
#         userID = request.cookies["userID"]
#         user = get_user_info(userID)
#         if request.method == 'POST':
#             error = update_user(request, userID)
#             if error:
#                 render_template("edit_profile.html", user=user, error=error)
#             else:
#                 return redirect('/profile/%s' % userID)
#         return render_template("edit_profile.html", user=user, error=error)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
#
# @app.route("/delete_post/<int:from_cite>", methods=['POST'])
# def delete_post(from_cite):
#     post_id = request.form['real_id']
#     section_id = getSectionFromPost(post_id)
#     delete_postOf(post_id)
#     if from_cite == 1: return redirect('/profile')
#     else: return redirect('/section/%s' % section_id)
#
#
# @app.route("/search", methods=['POST', 'GET'])
# def search():
#     error = None;
#     if request.method == 'POST':
#             searching = request.form['searching']
#             return redirect('/searchresult/%s' % searching)
#     try:
#         username = request.cookies["username"]
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         is_master = list(map(int, request.cookies["is_master"].split(","))) if request.cookies["is_master"] else []
#         clicks_post = get_top10clicks_post()
#         replies_post = get_top10replies_post()
#         return render_template("search.html", username=username, clicks_post=clicks_post, replies_post = replies_post, admin=is_admin, master=is_master, error=error)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/searchresult/")
# @app.route("/searchresult/<string:searching>", methods=['POST', 'GET'])
# def result_page(searching=""):
#     if not searching or request.method=='POST':
#         searching = request.form['searching']
#     try:
#         username = request.cookies["username"]
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         is_master = list(map(int, request.cookies["is_master"].split(","))) if request.cookies["is_master"] else []
#         result = search_in_db(searching)
#         return render_template("searchresult.html", username=username, searching=searching, result=result, admin=is_admin, master=is_master)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/manage_user", methods=['POST', 'GET'])
# @app.route("/manage_user/<int:id>", methods=['POST', 'GET'])
# def manage_user(id=None):
#     if id:
#         error = delete_user(id)
#     else: error = None
#     if request.method == 'POST':
#             searching = request.form['searching']
#             return redirect('/searchresult/%s' % searching)
#     try:
#         username = request.cookies["username"]
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         all_users = get_all_users()
#         return render_template("manage_user.html", username=username, admin=is_admin, all_users=all_users, error=error)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/add_user", methods=['POST', 'GET'])
# def add_user():
#     is_admin = True if request.cookies["is_admin"] == 'True' else False
#     if not is_admin:
#         print("Not authorized!")
#         return redirect('/sections')
#     error = None
#     if request.method == 'POST':
#         userID, account, error = valid_register(request)
#         if not error:
#             return redirect('/manage_user')
#         else:
#             print(error)
#             return render_template("/add_user.html", error=error)
#     return render_template("/add_user.html", error=error)
#
#
# @app.route("/compare", methods=['POST'])
# @app.route("/compare/<string:seca>/<string:secb>")
# def compare(seca="", secb=""):
#     if request.method == 'POST' and "searching" in request.form:
#         searching = request.form['searching']
#         return redirect('/searchresult/%s' % searching)
#     try:
#         username = request.cookies["username"]
#         is_admin = True if request.cookies["is_admin"] == 'True' else False
#         is_master = list(map(int, request.cookies["is_master"].split(","))) if request.cookies["is_master"] else []
#
#         seca = request.form['secA']
#         secb = request.form['secB']
#         users, error = moreposts(seca, secb)
#
#         return render_template("compare.html", username=username, users = users, seca=seca, secb=secb, admin=is_admin, master=is_master, error=error)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/active_users/<int:sectionid>/<int:posts>", methods=['POST','GET'])
# def active_users(sectionid, posts=1):
#     if request.method == 'POST' and "searching" in request.form:
#         searching = request.form['searching']
#         return redirect('/searchresult/%s' % searching)
#     try:
#         username = request.cookies["username"]
#         admin = True if request.cookies["is_admin"] == 'True' else False
#         sortedByPosts = True if posts==1 else False
#         sectionName, active_users = get_active_users(sectionid, sortedByPosts)
#         return render_template("active_users.html", sectionid=sectionid, username=username, admin=admin,
#                                sortedByPosts=sortedByPosts, sectionName=sectionName, active_users=active_users)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/hot_post/<int:sectionid>", methods=['POST','GET'])
# def hot_post(sectionid):
#     if request.method == 'POST' and "searching" in request.form:
#         searching = request.form['searching']
#         return redirect('/searchresult/%s' % searching)
#     try:
#         username = request.cookies["username"]
#         admin = True if request.cookies["is_admin"] == 'True' else False
#         sectionName, hotpost = get_hot_post(sectionid)
#         return render_template("hot_post.html", sectionid=sectionid, username=username, admin=admin,
#                                sectionName=sectionName, hotpost=hotpost)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
#
# @app.route("/clicks_replies/<int:sectionid>/<int:clicks>", methods=['POST', 'GET'])
# def clicks_replies(sectionid, clicks=1):
#     if request.method == 'POST' and "searching" in request.form:
#         searching = request.form['searching']
#         return redirect('/searchresult/%s' % searching)
#     try:
#         username = request.cookies["username"]
#         admin = True if request.cookies["is_admin"] == 'True' else False
#         sectionName, avginfo, infos = get_target_posts(sectionid, clicks)
#         return render_template("clicks_replies.html", sectionid=sectionid, username=username, admin=admin,
#                                clicks=clicks, sectionName=sectionName, infos=infos, avginfo=avginfo)
#     except KeyError:
#         print(KeyError, " keyerror for username")
#         return redirect('/')
