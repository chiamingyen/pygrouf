# coding: utf-8
from flask import Flask, send_from_directory, request, redirect, \
    render_template, session, make_response, url_for, flash
import random
import math
import os
# init.py 為自行建立的起始物件
import init
# for authomatic
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
# from config.py 導入 CONFIG
from config import CONFIG
# 利用 nocache.py 建立 @nocache decorator, 讓頁面不會留下 cache
from nocache import nocache
### from PyGroup start
import os
### for logincheck
import smtplib
from email.mime.text import MIMEText  
from email.header import Header
### 取得目前時區時間
from time import strftime, localtime
import datetime, pytz
### for pagination
import math
# for mako
from mako.template import Template
from mako.lookup import TemplateLookup
# for bs4
from bs4 import BeautifulSoup, Comment
# 計算執行時間
import time
# for mysql
import pymysql
# for skylark
#from skylark import Database, Model, Field, PrimaryKey, ForeignKey
# use cgi.escape() to resemble php htmlspecialchars()
# use cgi.escape() or html.escape to generate data for textarea tag, otherwise Editor can not deal with some Javascript code.
import cgi
# for logincheck and parse_config methods
import hashlib
# for unescape content
import html.parser
# for logging
import logging
# for strip_tags
import re
# for sqlite
import sqlite3
# 再 try peewee
from peewee import SqliteDatabase, Model, CharField, TextField, IntegerField, MySQLDatabase
# 確定程式檔案所在目錄, 在 Windows 有最後的反斜線
_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
# 設定在雲端與近端的資料儲存目錄
if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
    # 表示程式在雲端執行
    download_root_dir = os.environ['OPENSHIFT_DATA_DIR']
    data_dir = os.environ['OPENSHIFT_DATA_DIR']
    template_root_dir = os.environ['OPENSHIFT_REPO_DIR']+"/templates"
else:
    # 表示程式在近端執行
    download_root_dir = _curdir + "/local_data/"
    data_dir = _curdir + "/local_data/"
    template_root_dir = _curdir + "/templates"
# 資料庫選用
# 內建使用 sqlite3
ormdb = "sqlite"
#ormdb = "mysql"
#ormdb = "postgresql"
if ormdb == "sqlite":
    # 針對 sqlite3 指定資料庫檔案
    db = SqliteDatabase(data_dir+"task.db", check_same_thread=False)

elif ormdb == "mysql":
    # 選用 MySQL
    # 注意 port 必須為整數, 而非字串
    if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
        db = MySQLDatabase(database='cadp', host=os.environ[str('OPENSHIFT_MYSQL_DB_HOST')],  \
            port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT']), \
            user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'], \
            passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'], charset='utf8')
    else:
        # peewee 版本
        db = MySQLDatabase(database='yourdb', host='yourhost', \
             port=3306, user='youruser', passwd='yourpassword', charset='utf8')
else:
    # 選用 PostgreSQL
    # 注意 port 必須為整數, 而非字串
    if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
        db = PostgreSQLDatabase(database='cadp', host=os.environ[str('OPENSHIFT_POSTGRESQL_DB_HOST')],  \
            port=int(os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']), \
            user=os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME'], \
            passwd=os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD'], charset='utf8')
    else:
        # peewee 版本
        db = PostgreSQLDatabase(database='cadp', host='localhost', \
             port=3306, user='root', passwd='root', charset='utf8')

# 確定程式檔案所在目錄, 在 Windows 有最後的反斜線
_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
# 設定在雲端與近端的資料儲存目錄
if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
    # 表示程式在雲端執行
    data_dir = os.environ['OPENSHIFT_DATA_DIR']
    static_dir = os.environ['OPENSHIFT_REPO_DIR']+"/static"
    download_dir = os.environ['OPENSHIFT_DATA_DIR']+"/downloads"
    CALLBACK_URL = "http://cdw2-ladisai.rhcloud.com/menu"
else:
    # 表示程式在近端執行
    data_dir = _curdir + "/local_data/"
    static_dir = _curdir + "/static"
    download_dir = _curdir + "/local_data/downloads/"
    CALLBACK_URL = "http://localhost:5000/menu"

# 利用 init.py 啟動, 建立所需的相關檔案
initobj = init.Init()

# 必須先將 download_dir 設為 static_folder, 然後才可以用於 download 方法中的 app.static_folder 的呼叫
app = Flask(__name__)

# 設置隨後要在 blueprint 應用程式中引用的 global 變數
app.config['data_dir'] = data_dir
app.config['static_dir'] = static_dir
app.config['download_dir'] = download_dir

# Instantiate Authomatic.
authomatic = Authomatic(CONFIG, 'A0Zr9@8j/3yX R~XHH!jmN]LWX/,?R@T', report_errors=False)

# 使用 session 必須要設定 secret_key
# In order to use sessions you have to set a secret key
# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr9@8j/3yX R~XHH!jmN]LWX/,?R@T'
# 在此建立資料表欄位
    
class Task(Model):
    # peewee 內定 id 為 PrimaryKey
    #id = PrimaryKey()
    follow = IntegerField()
    owner = CharField()
    name = CharField()
    type = CharField()
    time = CharField()
    content = TextField()
    ip = CharField()

    class Meta:
        database = db # This model uses the data_dir+"task.db" database.
def printuser():
    session["user"] = "anonymous"
    if not session.get("user"):
        user = "anonymous"
    else:
        user = session.get("user")
    return user
def parse_config(filename):
    #filename = "pygroup_config"
    if not os.path.isfile(data_dir+filename):
        # create config file if there is no config file
        file = open(data_dir+filename, "w", encoding="utf-8")
        # 若無設定檔案, 則逐一寫入 default 值
        # default password is admin
        password="admin"
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        # adsense 為 yes 表示要放廣告, 內建 adsense 為 no
        # anonymouse 為 yes 表示允許無登入者可以檢視內容, 內建 anonymous 為 no
        file.write("password:"+hashed_password+"\n \
            adsense:no\n \
            anonymous:no\n \
            user_mail_suffix:\n \
            site_closed:no\n \
            read_only:no\n")
        file.close()
    # 取出設定值後, 傳回
    with open(data_dir+filename, encoding="utf-8") as file:
        config = file.read()
    config_data = config.split("\n")
    password = config_data[0].split(":")[1]
    adsense = config_data[1].split(":")[1]
    anonymous = config_data[2].split(":")[1]
    mail_suffix = config_data[3].split(":")[1]
    site_closed = config_data[4].split(":")[1]
    read_only = config_data[5].split(":")[1]
    return password, adsense, anonymous, mail_suffix, site_closed, read_only
@app.route("/", methods=['GET'])
def index(page=1, item_per_page=5, id=0, flat=0, desc=0, keyword=None):
    if not request.args.get('page'):
        page = 1
    else:
        page = request.args.get('page')
    if not request.args.get('item_per_page'):
        item_per_page = 5
    else:
        item_per_page = request.args.get('item_per_page')
    if not request.args.get('id'):
        id = 0
    else:
        id = request.args.get('id')
    if not request.args.get('flat'):
        flat = 0
    else:
        flat = request.args.get('flat')
    if not request.args.get('desc'):
        desc= 0
    else:
        desc= request.args.get('desc')
    if not request.args.get('keyword'):
        keyword = None
    else:
        keyword = request.args.get('keyword')
    user = printuser()
    # 這裡不用 allow_pass 原因在於需要 adsense 變數
    saved_password, adsense, anonymous, mail_suffix, site_closed, read_only = parse_config(filename="pygroup_config")
    if user == "anonymous" and anonymous != "yes":
        if id != 0:
            return redirect("/login?id="+id)
        else:
            return redirect("/login")
    if adsense == "yes":
        filename = data_dir+"adsense_content"
        with open(filename, encoding="utf-8") as file:
            adsense_content = file.read()
    else:
        adsense_content = ""
    template_lookup = TemplateLookup(directories=[template_root_dir])
    # 必須要從 templates 目錄取出 tasklist.html
    mytemplate = template_lookup.get_template("tasklist.html")
    # 這裡要加入單獨根據 id 號, 列出某一特定資料緒的分支
    # 若 id 為 0 表示非指定列出各別主緒資料, 而是列出全部資料
    # 這時可再根據各筆資料列印時找出各主緒資料的附屬資料筆數
    # 加入 flat = 1 時, 列出所有資料
    # 請注意這裡直接從 tasksearchform.html 中的關鍵字查詢, 指定以 tasklist 執行, 但是無法單獨列出具有關鍵字的 task 資料, 而是子緒有關鍵字時, 也是列出主緒資料
    # 單獨 db 連結與結束
    db.connect()
    if keyword == None:
        if id == 0:
            if flat == 0:
                # 只列出主資料緒
                # desc 為 0 表示要 id 由小到大排序列出資料
                if desc == 0:
                    method = "?"
                    data = Task.select().where(Task.follow==0)
                else:
                    # desc 為 1 表示 id 反向排序
                    method = "?desc=1"
                    data = Task.select().where(Task.follow==0).order_by(Task.id.desc())
            else:
                # flat 為 1 表示要列出所有資料
                # 原先沒有反向排序, 內建使用正向排序
                if desc == 0:
                    method = "?flat=1"
                    data = Task.select()
                else:
                    method = "?flat=1&desc=1"
                    data = Task.select().order_by(Task.id.desc())
        else:
            method = "?id="+str(id)
            # 設法列出主資料與其下屬資料緒, 這裡是否可以改為 recursive 追蹤多緒資料
            # 只列出主緒與下一層子緒資料
            data = Task.select().where((Task.id == id) | (Task.follow == id))
    else:
        # 有關鍵字查詢時(只查 owner, content, type 與 name), 只列出主資料緒
        #flat = 1
        method = "?keyword="+keyword+"&flat="+str(flat)
        data = Task.select().where((Task.content ** ('%%%s%%' % (keyword))) | (Task.name ** ('%%%s%%' % (keyword))) | \
        (Task.owner ** ('%%%s%%' % (keyword))) | \
        (Task.type ** ('%%%s%%' % (keyword))) \
            )
    follow = []
    for task in data:
        follow_data = Task.select().where(Task.follow == task.id).count()
        follow.append(follow_data)
    db.close()
    #
    # 送出 user, id, flat, method 與 data
    #
    # 增加傳送 read_only, 若 read_only = yes 則不列出 taskform, 而且所有新增編輯刪除功能均失效
    #
    return mytemplate.render(user=user, id=id, flat=flat, method=method, data=data,  \
        page=page, item_per_page=item_per_page, follow=follow, keyword=keyword, \
        adsense_content=adsense_content, adsense=adsense, anonymous=anonymous, \
        site_closed=site_closed, read_only=read_only)
    # 其餘分頁 logic 在 mako template tasklist.html 中完成
@app.route("/usermenu")
def usermenu():
    # 這裡包括列出用戶以及列印表單
    user = printuser()
    menu = ["login", "logout", "usermenu", "cmsimply", \
                 "tasklist"]
    template_lookup = TemplateLookup(directories=[template_root_dir])
    # 必須要從 templates 目錄取出 usermenu.html
    mytemplate = template_lookup.get_template("usermenu.html")
    return mytemplate.render(user=user, menu=menu)
# 不允許使用者直接呼叫 taskform
def taskform(id=0):
    user = printuser()
    template_lookup = TemplateLookup(directories=[template_root_dir])
    # 必須要從 templates 目錄取出 tasklist.html
    # 針對 id != 0 時, 表示要回應主資料緒, 希望取出與 id 對應的資料標頭, 然後加上 Re:
    mytemplate = template_lookup.get_template("taskform.html")
    return mytemplate.render(user=user, id=id)
@app.route("/taskaction", methods=["POST"])
def taskaction():
    content = request.form["content"]
    type = request.form["type"]
    name = request.form["name"]
    follow = request.form["follow"]
    if content == None or name == "":
        return "標題與內容都不可空白!<br /><a href='/'>Go to main page</a><br />"
    else:
        start_time = time.time()
        owner = printuser()
        if allow_pass(owner) == "no":
            return redirect("/login")
        now = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
        '''
        # 因為登入後就將 @ 代換為 _at_, 所以此地不用再換
        # user 若帶有 @ 則用 at 代替
        if "@" in owner:
            owner = owner.replace('@', '_at_')
        '''
        content = content.replace('\n', '')
        valid_tags = ['a', 'br', 'h1', 'h2', 'h3', 'p', 'div', 'hr', 'img', 'iframe', 'li', 'ul', 'b', 'ol', 'pre']
        tags = ''
        for tag in valid_tags:
            tags += tag
        content = strip_tags(content, tags)
        # 這裡要除掉 </br> 關閉 break 的標註, 否則在部分瀏覽器會產生額外的跳行
        content = str(content).replace('</br>', '')
        time_elapsed = round(time.time() - start_time, 5)
        # last insert id 為 data.id
        db.connect()
        # peewee 版本
        ip = ""
        data = Task.create(owner=owner, name=str(name), type=type, time=str(now), follow=follow, content=content, ip=str(ip))
        data.save()
        # 這裡要與 taskedit 相同, 提供回到首頁或繼續編輯按鈕
        output = "<a href='/'>Go to main page</a><br />"
        output +="<a href='/taskeditform?id="+str(data.id)+"'>繼續編輯</a><br /><br />"
        output += '''以下資料已經更新:<br /><br />
        owner:'''+owner+'''<br />
        name:'''+name+'''<br />
        type:'''+type+'''<br />
        time:'''+str(now)+'''<br />
        content:'''+str(content)+'''<br /><br />
        <a href='/'>Go to main page</a><br />
    '''
        output +="<a href='/taskeditform?id="+str(data.id)+"'>繼續編輯</a><br /><br />"
        db.close()
        return output

def allow_pass(user="anonymous"):
    password, adsense, anonymous, mail_suffix, site_closed, read_only = parse_config(filename="pygroup_config")
    if user == "anonymous" and anonymous != "yes":
        return "no"
    else:
        return "yes"
## Remove xml style tags from an input string.
#
#  @param string The input string.
#  @param allowed_tags A string to specify tags which should not be removed.
def strip_tags(string, allowed_tags=''):
  if allowed_tags != '':
    # Get a list of all allowed tag names.
    allowed_tags_list = re.sub(r'[\\/<> ]+', '', allowed_tags).split(',')
    allowed_pattern = ''
    for s in allowed_tags_list:
      if s == '':
       continue;
      # Add all possible patterns for this tag to the regex.
      if allowed_pattern != '':
        allowed_pattern += '|'
      allowed_pattern += '<' + s + ' [^><]*>$|<' + s + '>|<!--' + s + '-->'
    # Get all tags included in the string.
    all_tags = re.findall(r'<!--?[^--><]+>', string, re.I)
    for tag in all_tags:
      # If not allowed, replace it.
      if not re.match(allowed_pattern, tag, re.I):
        string = string.replace(tag, '')
  else:
    # If no allowed tags, remove all.
    string = re.sub(r'<[^>]*?>', '', string)
 
  return string
@app.route("/editconfig")
def editconfig(password=None, password2=None, adsense=None, anonymous=None, \
                mail_suffix=None, site_closed=None, read_only=None):
    filename = "pygroup_config"
    user = printuser()
    # 只有系統管理者可以編輯 config 設定檔案
    if user != "admin":
        return redirect("/login")
    if password == None or adsense == None or anonymous == None:
        return error_log("no content to save!")
    # 取出目前的設定值
    old_password, old_adsense, old_anonymous, old_mail_suffix, old_site_closed, old_read_only = parse_config(filename=filename)
    if adsense == None or password == None or password2 != old_password or password == '':
        # 傳回錯誤畫面
        return "error<br /><a href='/'>Go to main page</a><br />"
    else:
        if password == password2 and password == old_password:
            hashed_password = old_password
        else:
            hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        # 將新的設定值寫入檔案
        file = open(data_dir+filename, "w", encoding="utf-8")
        #  將新的設定值逐一寫入設定檔案中
        file.write("password:"+hashed_password+"\n \
            adsense:"+adsense+"\n \
            anonymous:"+anonymous+"\n \
            mail_suffix:"+mail_suffix+"\n \
            site_closed:"+site_closed+"\n \
            read_only:"+read_only+"\n")
        file.close()
        # 傳回設定檔案已經儲存
        return "config file saved<br /><a href='/'>Go to main page</a><br />"
@app.route("/editconfigform")
def editconfigform():
    user = printuser()
    # 只有系統管理者可以編輯 config 設定檔案
    if user != "admin":
        return redirect("/login")
    # 以下設法列出 config 編輯表單
    # 取出目前的設定值
    saved_password, adsense, anonymous, mail_suffix, site_closed, read_only = parse_config(filename="pygroup_config")
    template_lookup = TemplateLookup(directories=[template_root_dir])
    mytemplate = template_lookup.get_template("editconfigform.html")
    return mytemplate.render(user=user, saved_password=saved_password, adsense=adsense, anonymous=anonymous, mail_suffix=mail_suffix, site_closed=site_closed, read_only=read_only)
@app.route("/editadsense")
def editadsense(adsense_content=None):
    filename = "adsense_content"
    user = printuser()
    # 只有系統管理者可以編輯 config 設定檔案
    if user != "admin":
        return redirect("/login")
    # 將新的設定值寫入檔案
    file = open(data_dir+filename, "w", encoding="utf-8")
    #  將新的設定值逐一寫入設定檔案中
    file.write(adsense_content+"\n")
    file.close()
    # 傳回設定檔案已經儲存
    return "adsense_content file saved"
@app.route("/editadsenseform")
def editadsenseform():
    user = printuser()
    # 只有系統管理者可以編輯 adsense_content 檔案
    if user != "admin":
        return redirect("/login")
    # 以下設法列出 adsense_content 編輯表單
    # 取出目前的設定值
    filename="adsense_content"
    # 取出 adsense_content 後, 傳回
    with open(data_dir+filename, encoding="utf-8") as file:
        saved_adsense = file.read()
    template_lookup = TemplateLookup(directories=[template_root_dir+"/templates"])
    mytemplate = template_lookup.get_template("editadsenseform.html")
    return mytemplate.render(user=user, saved_adsense=saved_adsense)
@app.route("/taskeditform")
def taskeditform(id=None):
    user = printuser()
    password, adsense, anonymous, mail_suffix, site_closed, read_only = parse_config(filename="pygroup_config")
    if read_only == "yes" and user != "admin":
        return "<a href='/'>Go to main page</a><br /><br />error, site is read only!"
    if user == "anonymous" and anonymous != "yes":
        return redirect("/login")
    else:
        try:
            db.connect()
            # 用 get() 取單筆資料
            data = Task.select().where(Task.id==int(id)).get()
            output = "user:"+user+", owner:"+data.owner+"<br /><br />"
            if user != data.owner:
                if user != "admin":
                    db.close()
                    return output + "error! Not authorized!"
                else:
                    template_lookup = TemplateLookup(directories=[template_root_dir])
                    mytemplate = template_lookup.get_template("taskeditform.html")
                    db.close()
                    return mytemplate.render(user=user, id=id, data=data)
            else:
                template_lookup = TemplateLookup(directories=[template_root_dir])
                mytemplate = template_lookup.get_template("taskeditform.html")
                db.close()
                return mytemplate.render(user=user, id=id, data=data)
        except:
            db.close()
            return "error! Not authorized!"
@app.route("/taskedit")
def taskedit(id=None, type=None, name=None, content=None):
    # check user and data owner
    if id == None:
        return "error<br /><br /><a href='/'>Go to main page</a><br />"
    user = printuser()
    password, adsense, anonymous, mail_suffix, site_closed, read_only = parse_config(filename="pygroup_config")
    if read_only == "yes" and user != "admin":
        return "<a href='/'>Go to main page</a><br /><br />error, site is read only!"
    if user == "anonymous" and anonymous != "yes":
        return redirect("/login")
    try:
        db.connect()
    except:
        time.sleep(0.300)
        db.connect()
    data = Task.select().where(Task.id==int(id)).get()
    now = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
    # 過濾資料
    content = content.replace('\n', '')
    valid_tags = ['a', 'br', 'h1', 'h2', 'h3', 'p', 'div', 'hr', 'img', 'iframe', 'li', 'ul', 'b', 'ol', 'pre']
    tags = ''
    for tag in valid_tags:
        tags += tag
    content = strip_tags(content, tags)
    # 這裡要除掉 </br> 關閉 break 的標註, 否則在部分瀏覽器會產生額外的跳行
    content = str(content).replace('</br>', '')
    output = "user:"+user+", owner:"+data.owner+"<br /><br />"
    if user != data.owner:
        if  user != "admin":
            db.close()
            return "error! Not authorized!"
        else:
            # 請注意這裡曾經犯了 where(id==int(id) 的重大錯誤, 讓所有資料在 update 時只留下一筆資料
            query = Task.update(type=type, name=name, content=str(content), time=str(now)).where(Task.id==int(id))
            query.execute()
            output += "<a href='/'>Go to main page</a><br />"
            output +="<a href='/taskeditform?id="+str(id)+"'>繼續編輯</a><br /><br />"
            output += '''以下資料已經更新:<br /><br />
            owner:'''+data.owner+'''<br />
            name:'''+name+'''<br />
            type:'''+type+'''<br />
            time:'''+str(now)+'''<br />
            content:'''+str(content)+'''<br /><br />
            <a href='/'>Go to main page</a><br />
'''
            output +="<a href='/taskeditform?id="+str(id)+"'>繼續編輯</a><br />"
    else:
        query = Task.update(type=type, name=name, content=str(content), time=str(now)).where(Task.id==int(id))
        query.execute()
        output += "<a href='/'>Go to main page</a><br />"
        output +="<a href='/taskeditform?id="+str(id)+"'>繼續編輯</a><br /><br />"
        output += '''以下資料已經更新:<br /><br />
        owner:'''+data.owner+'''<br />
        name:'''+name+'''<br />
        type:'''+type+'''<br />
        time:'''+str(now)+'''<br />
        content:'''+str(content)+'''<br /><br />
        <a href='/'>Go to main page</a><br />
'''
        output +="<a href='/taskeditform?id="+str(id)+"'>繼續編輯</a><br />"
    db.close()
    return output
@app.route("/taskdeleteform")
def taskdeleteform(id=None):
    user = printuser()
    password, adsense, anonymous, mail_suffix, site_closed, read_only = parse_config(filename="pygroup_config")
    if read_only == "yes" and user != "admin":
        return "<a href='/'>Go to main page</a><br /><br />error, site is read only!"
    if user == "anonymous" and anonymous != "yes":
        return redirect("/login")
    else:
        try:
            # 這裡要區分刪除子緒或主緒資料
            # 若刪除子緒, 則 data 只包含子緒資料, 若為主緒, 則 data 必須包含所有資料
            # 先找出資料, 判定是否為主緒
            # 用 get() 取單筆資料
            db.connect()
            data= Task.select().where(Task.id==int(id)).get()
            owner = data.owner
            if user != data.owner:
                if user != "admin":
                    db.close()
                    return output + "error! 非資料擁有者, Not authorized!"
                else:
                    if data.follow == 0:
                        # 表示該資料為主緒資料
                        # 資料要重新搜尋, 納入子資料
                        data = Task.select().where((Task.id == id) | (Task.follow == id))
                        output = "資料為主緒資料<br />"
                        # 增加一個資料類型判斷, main 表資料為主緒
                        type = "main"
                    else:
                        # 表示該資料為子緒資料
                        # 直接採用 data 資料送到 taskdeleteform.html
                        output = "資料為子緒資料<br />"
                        # 增加一個資料類型判斷, alone 表資料為子緒
                        type = "alone"
                    output += "user:"+user+", owner:"+owner+"<br /><br />"
                    template_lookup = TemplateLookup(directories=[template_root_dir])
                    mytemplate = template_lookup.get_template("taskdeleteform.html")
                    # 這裡的 type 為所要刪除資料的類型, 為 main 或為 alone
                    db.close()
                    return mytemplate.render(user=user, id=id, data=data, type=type)
            else:
                if data.follow == 0:
                    # 表示該資料為主緒資料
                    # 資料要重新搜尋, 納入子資料
                    data = Task.select().where((Task.id == id) | (Task.follow == id))
                    output = "資料為主緒資料<br />"
                    # 增加一個資料類型判斷, main 表資料為主緒
                    type = "main"
                else:
                    # 表示該資料為子緒資料
                    # 直接採用 data 資料送到 taskdeleteform.html
                    output = "資料為子緒資料<br />"
                    # 增加一個資料類型判斷, alone 表資料為子緒
                    type = "alone"
                output += "user:"+user+", owner:"+owner+"<br /><br />"
                template_lookup = TemplateLookup(directories=[template_root_dir])
                mytemplate = template_lookup.get_template("taskdeleteform.html")
                # 這裡的 type 為所要刪除資料的類型, 為 main 或為 alone
                db.close()
                return mytemplate.render(user=user, id=id, data=data, type=type)
        except:
            db.close()
            return "error! 無法正確查詢資料, Not authorized!"
@app.route("/taskdelete")
def taskdelete(id=None, type=None, name=None, content=None):
    # check user and data owner
    user = printuser()
    password, adsense, anonymous, mail_suffix, site_closed, read_only = parse_config(filename="pygroup_config")
    if read_only == "yes" and user != "admin":
        return "<a href='/'>Go to main page</a><br /><br />error, site is read only!"
    if user == "anonymous" and anonymous != "yes":
        return redirect("/login")
    # 用 get() 取單筆資料
    db.connect()
    data = Task.select().where(Task.id==int(id)).get()
    now = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
    output = "user:"+user+", owner:"+data.owner+"<br /><br />"
    if user != data.owner:
        if user != "admin":
            db.close()
            return "error! Not authorized!"
        else:
            # 若資料為主緒則一併刪除子緒, 若為子緒, 則只刪除該子緒
            if data.follow == 0:
                # 表示資料為主緒
                # 先刪除主緒
                query = Task.at(int(id)).delete()
                query.execute()
                # 再刪除所有對應子緒
                query = Task.delete().where(follow=int(id))
                query.execute()
                output += "所有序列資料已經刪除!<br />"
            else:
                # 表示資料為子緒
                query = Task.delete().where(Task.id==int(id))
                query.execute()
                output += "資料已經刪除!<br />"
    else:
        # 若資料為主緒則一併刪除子緒, 若為子緒, 則只刪除該子緒
        if data.follow == 0:
            # 表示資料為主緒
            # 先刪除主緒
            query = Task.delete().where(Task.id==int(id))
            query.execute()
            # 再刪除所有對應子緒
            query = Task.delete().where(Task.follow==int(id))
            query.execute()
            output += '''所有序列資料已經刪除!<br /><br />
            <a href='/'>Go to main page</a><br />
'''
        else:
            # 表示資料為子緒
            query = Task.delete().where(Task.id==int(id))
            query.execute()
            output += '''資料已經刪除!<br /><br />
            <a href='/'>Go to main page</a><br />
'''
    db.close()
    return output
# 不允許使用者直接呼叫 tasksearchform
def tasksearchform():
    user = printuser()
    template_lookup = TemplateLookup(directories=[template_root_dir])
    # 必須要從 templates 目錄取出 tasksearchform.html
    mytemplate = template_lookup.get_template("tasksearchform.html")
    return mytemplate.render(user=user)
@app.route('/option', methods=["GET", "POST"])
def option():
    # 各組選出組長的方式, 若採遞增, 則各組內學號最小者為組長
    option_list1 = ["遞增", "遞減"]
    # 各組組長間的排序定組序, 若採遞增, 則學號最小的組長為第1組
    option_list2 = ["遞增", "遞減"]
    # 電腦教室共有 9 排電腦
    column = 9
    # 加上班級選擇
    option_list3 = ["2a", "2b"]
    # 根據班級的總人數, 以 9 去除, 算出需要排幾列才能夠容納的下, 而且若列數超過 7
    # 表示這些學員必須與其他同組學員共用電腦

    return render_template('option.html', option_list1=option_list1, option_list2=option_list2, option_list3=option_list3, column=column)
@app.route('/optionaction', methods=['POST'])
def optionaction():
    # 最後傳回的字串為 out_string
    out_string = ""
    # 程式內需要暫時使用的 tmp_string
    tmp_string = ""
    # 傳回字串中, 用來說明排序原則的 desc_string
    desc_string = ""
    result = []
    group_sorted = []
    num_of_stud = 0
    # 每組至多 7 人
    max_num_in_one_group = 7
    # 電腦教室配置, 共有 9 排
    total_column = 9
    # 上面為相關變數的初始值設定, 以下開始取出 data_a 或 data_b 進行處理, 由 option3 傳回值決定
    if request.form["option3"]  == "2a":
        content = request.form["data_a"]
    else:
        content = request.form["data_b"]
    #result = content.splitlines()
    for line in content.splitlines():
        result.append(list(line.split(",")))
    # i 為行序
    for i in range(len(result)):
        # j 為組員序
        for j in range(len(result[i])):
            tmp_string += result[i][j] + ", "
        out_string += "第" + str(i+1) + "排資料:"+ tmp_string + "<br />"
        tmp_string = ""
    for i in range(len(result)):
        # 開始進入組內排序, 根據 request.form["option1"]  的值決定遞增或遞減
        if request.form["option1"]  == "遞增":
            group_list = sorted(list(filter(None, result[i])))
        else:
            group_list = sorted(list(filter(None, result[i])), reverse=True)
        group_sorted.append(group_list)
    if request.form["option1"]  == "遞增":
        desc_string += "組內學號最小者為組長."
    else:
         desc_string += "組內學號最大者為組長."
    # 開始進入組間組長學號排序, 根據 request.form["option2"] 的值決定遞增或遞減
    if request.form["option2"]  == "遞增":
        desc_string += "各組長中學號最小者為第1組."
        final_result = sorted(group_sorted)
    else:
        desc_string += "各組長中學號最大者為第1組."
        final_result = sorted(group_sorted, reverse=True)
    out_string += "<br />" + desc_string + "<br />"
    # i 為行序
    for i in range(len(final_result)):
        # j 為組員序
        for j in range(len(final_result[i])):
            num_of_stud += 1
            tmp_string += final_result[i][j] + ","
        out_string += "第" + str(i+1) + "組:"+ tmp_string + "<br />"
        tmp_string = ""
    #return "總共有" + str(i+) + "組"
    # group_num 為總組數
    group_num = i + 1
    # 截至這裡, 已經完成選組長, 以及定組序的工作 ,接下來要排座位, 並且印出座位表
    # 先算每班的總人數
    #return "總共有"+ str(num_of_stud) + "人"
    seat_by_column = []
    for row in range(max_num_in_one_group):
    # 每組最多 7 人
    #for row in range(7):
        # 這裡的 11 為總組數
        #for column in range(11):
        for column in range(group_num):
            # 因為各分組數列的長度並不相同, 但是最長的有 7 位組員, 因此若無法取得的資料 (因為索引超值), 就補上空字串
            try:
                seat_by_column.append(final_result[column][row])
            except:
                seat_by_column.append("")
    # seat_by_column 為去除空白字串前的座位數列
    # 然後利用 filter(None, seat_by_column) 去除空白字串, 就可以得到以 column 為主的座位排序
    seat_by_column = list(filter(None, seat_by_column))
    # 然後每 N 個取為 1 排, 即可得到以排為主的座位序列, 而 N 則視全班人數除以 9, 也就是 total_column 進位決定, 因為共有 9 排
    N = math.ceil(num_of_stud/total_column)
    # for debug
    #return str(num_of_stud) + ":" + str(total_column) + ":" + str(N)
    column_list = [seat_by_column[n:n+N] for n in range(0, len(seat_by_column), N)]
    # 列出每 N 個組員一排的數列 column_list
    # 接下來要納入以排為主的座位
    # 根據 column_list, 建立一個 dictionary, 其中學號為 index, 座位號為對應值
    seat_dict = {}
    for column in range(len(column_list)):
        for i in range(N):
            try:
                seat_dict.update({column_list[column][i]: (column, i)})
            except:
                seat_dict.update({"": ""})
                
    # 開始準備用順序列出學員座號
    # 根據學號, 排序 dictionary 的方法
    import operator
    seat_dict_sort = sorted(seat_dict.items(), key = operator.itemgetter(0), reverse = False)
    # 依照學號順序, 列出座位表
    out_string += "<br />按照學號次序列出座位表:<br /><br />"
    for i in range(1, len(seat_dict_sort)):
        out_string +=  str(i) + ":"+ str(seat_dict_sort[i]) + "<br />"
    # 結束準備用順序列出學員座號
    # dont know why .reverse() did not work, 只有 [::-1] 可以 reverse list elements
    #g.es(column_list[::-1])

    # 因為經由 zip 逐一重新 transpose 的列資料, 必須配合最大 (也就是總共有 7 列, 也就是 N 的值) 列數補上空白字串 (也就是空位)
    # 所以不能使用 zip, 而必須導入 zip_longest 模組方法
    from itertools import zip_longest
    final_seat = list(zip_longest(*column_list[::-1], fillvalue=""))
    # 列出最後的座位表
    #g.es(final_seat)
    # 最後轉成 html table 標註格式
    out_string += "<br /> <br />"
    out_string += "<table border='1' width='100%'>"
    out_string += "<tr><td colspan='9' style='text-align:center'>講台</td></tr>"
    for row in range(len(final_seat)):
        out_string += "<tr>"
        # 因為每一 row 有 9, 也就是 total_column 個位子
        for i in range(total_column):
            try:
                if i%2 != 0:
                    out_string += "<td style='text-align:center'  bgcolor='#FFD78C' height='30'>" + str(final_seat[row][i]) + "</td>"
                else:
                    out_string += "<td style='text-align:center' height='30'>" + str(final_seat[row][i]) + "</td>"
            except:
                out_string += "<td>&nbsp;</td>"
        out_string += "</tr>"
    out_string += "</table><br /><br /><br />"
    return out_string
    # 等運算或資料處理結束後, 再將相關值送到對應的 template 進行資料的展示
    #return render_template('optionaction.html', option_list1=option_list1, option_list2=option_list2)
    

@app.route('/fileaxupload', methods=['POST'])
# ajax jquery chunked file upload for flask
def fileaxupload():
    '''
    if not session.get('logged_in'):
        #abort(401)
        return redirect(url_for('login'))
    '''
    # need to consider if the uploaded filename already existed.
    # right now all existed files will be replaced with the new files
    filename = request.args.get("ax-file-name")
    flag = request.args.get("start")
    if flag == "0":
        file = open(data_dir+"downloads/"+filename, "wb")
    else:
        file = open(data_dir+"downloads/"+filename, "ab")
    file.write(request.stream.read())
    file.close()
    return "files uploaded!"

    
    
@app.route('/fileuploadform')
def fileuploadform():
    # 先檢查使用者是否處於登入狀態, 若尚未登入則跳轉到登入畫面
    if not session.get('login_email'):
        #abort(401)
        return redirect(url_for('login'))
    return "<h1>file upload</h1><a href='menu'>menu</a><br /><br /><br />"+'''
  <script src="/static/jquery.js" type="text/javascript"></script>
  <script src="/static/axuploader.js" type="text/javascript"></script>
  <script>
  $(document).ready(function(){
  $('.prova').axuploader({url:'fileaxupload', allowExt:['jpg','png','gif','7z','pdf','zip','flv','stl','swf'],
  finish:function(x,files)
{
    alert('All files have been uploaded: '+files);
},
  enable:true,
  remotePath:function(){
  return 'downloads/';
  }
  });
  });
  </script>
  <div class="prova"></div>
  <input type="button" onclick="$('.prova').axuploader('disable')" value="asd" />
  <input type="button" onclick="$('.prova').axuploader('enable')" value="ok" />
  </section></body></html>
  '''
@app.route('/imageaxupload', methods=['POST'])
# ajax jquery chunked file upload for flask
def imageaxupload():
    # 先檢查使用者是否處於登入狀態, 若尚未登入則跳轉到登入畫面
    if not session.get('login_email'):
        #abort(401)
        return redirect(url_for('login'))
    # need to consider if the uploaded filename already existed.
    # right now all existed files will be replaced with the new files
    filename = request.args.get("ax-file-name")
    flag = request.args.get("start")
    if flag == "0":
        file = open(data_dir+"images/"+filename, "wb")
    else:
        file = open(data_dir+"images/"+filename, "ab")
    file.write(request.stream.read())
    file.close()
    return "image file uploaded!"

    
    
@app.route('/imageuploadform')
def imageuploadform():
    # 先檢查使用者是否處於登入狀態, 若尚未登入則跳轉到登入畫面
    if not session.get('login_email'):
        #abort(401)
        return redirect(url_for('login'))
    return "<h1>file upload</h1><a href='menu'>menu</a><br /><br /><br />"+'''
  <script src="/static/jquery.js" type="text/javascript"></script>
  <script src="/static/axuploader.js" type="text/javascript"></script>
  <script>
  $(document).ready(function(){
  $('.prova').axuploader({url:'imageaxupload', allowExt:['jpg','png','gif','7z','pdf','zip','flv','stl','swf'],
  finish:function(x,files)
{
    alert('All files have been uploaded: '+files);
},
  enable:true,
  remotePath:function(){
  return 'images/';
  }
  });
  });
  </script>
  <div class="prova"></div>
  <input type="button" onclick="$('.prova').axuploader('disable')" value="asd" />
  <input type="button" onclick="$('.prova').axuploader('enable')" value="ok" />
  </section></body></html>
  '''
@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    #return send_from_directory(download_dir, filename=filename, as_attachment=True)
    return send_from_directory(download_dir, filename=filename)
    


# setup static directory
@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory(data_dir+"/images/", path)
# setup static directory
@app.route('/static/')
def send_static():
  return app.send_static_file('index.html')

# setup static directory
@app.route('/static/blog/')
def send_blog():
  return app.send_static_file('blog/index.html')

# setup static directory
@app.route('/static/<path:path>')
def send_file(path):
  return app.send_static_file(static_dir+path)

@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'], defaults={'provider_name':'google'})
def login(provider_name):
    
    callbackurl = CALLBACK_URL
    
    # We need response object for the WerkzeugAdapter.
    response = make_response()
    
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    
    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
            
        # 利用 session 登記登入者的 email
        session['login_email'] = result.user.email
        
        # 這裡必須分近端與雲端, 因為 google logout redirect 的 url 不同
        if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
            # 表示程式在雲端執行
            local = False
        else:
            # 表示在近端執行
            local = True
        # The rest happens inside the template.
        return render_template('login.html', result=result, local=local, callbackurl=callbackurl)
    
    # Don't forget to return the response.
    return response
@app.route('/logout')
def logout():
    session.pop('login_email' , None)
    flash('已經登出!')
    #return redirect(url_for('menu'))
    return redirect(url_for('login'))
@app.route('/menu')
@app.route('/index')
@nocache
def menu():
    # 先檢查使用者是否處於登入狀態, 若尚未登入則跳轉到登入畫面
    if not session.get('login_email'):
        #abort(401)
        return redirect(url_for('login'))
    # 進入使用者已經登入的流程設計
    user = session.get('login_email')
    return render_template('menu.html', user=user)
@app.route('/alogin' , methods=['GET' , 'POST'])
def alogin():
    # 在 OpenShift 執行要啟動 SSL 跳轉
    if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
    # 表示程式在雲端執行
        openshift = True
    else:
        openshift = False
    
    return render_template('alogin.html', openshift=openshift)
@app.route('/alogin_check' , methods=['GET' , 'POST'])
def alogin_check():
    spassword = "secret"
    username = request.form["username"]
    password = request.form["password"]
    if username != None and password != None:
        # 這裡要加入用戶名稱為 admin 的管理者登入模式
        if username == "admin":
            # 進入 admin 密碼查驗流程
            if password == spassword:
                # 利用 session 登記登入者的 email
                session['login_email'] = "admin"
                return redirect(url_for('menu'))
            else:
                return redirect(url_for('login'))
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run()






