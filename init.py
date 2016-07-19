import os
import sqlite3
import pymysql

# 確定程式檔案所在目錄, 在 Windows 有最後的反斜線
_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
# 設定在雲端與近端的資料儲存目錄
if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
    # 表示程式在雲端執行
    data_dir = os.environ['OPENSHIFT_DATA_DIR']
    static_dir = os.environ['OPENSHIFT_REPO_DIR']+"/static"
else:
    # 表示程式在近端執行
    data_dir = _curdir + "/local_data/"
    static_dir = _curdir + "/static"
class Init(object):
    def __init__(self):
        # hope to create downloads and images directories　
        if not os.path.isdir(data_dir+"downloads"):
            try:
                os.makedirs(data_dir+"downloads")
            except:
                print("mkdir error")
        if not os.path.isdir(data_dir+"images"):
            try:
                os.makedirs(data_dir+"images")
            except:
                print("mkdir error")
        if not os.path.isdir(data_dir+"tmp"):
            try:
                os.makedirs(data_dir+"tmp")
            except:
                print("mkdir error")

        # 假如沒有 adsense_content 則建立一個空白檔案
        if not os.path.isfile(data_dir+"adsense_content"):
            try:
                file = open(data_dir+"adsense_content", "w", encoding="utf-8")
                #  寫入內建的 adsense_content 內容
                adsense_content = '''
    <script type="text/javascript"><!--
            google_ad_client = "pub-2140091590744860";
            google_ad_width = 300;
            google_ad_height = 250;
            google_ad_format = "300x250_as";
            google_ad_type = "image";
            google_ad_channel ="";
            google_color_border = "000000";
            google_color_link = "0000FF";
            google_color_bg = "FFFFFF";
            google_color_text = "000000";
            google_color_url = "008000";
            google_ui_features = "rc:0";
            //--></script>
            <script type="text/javascript"
            src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
            </script>
    
    <script type="text/javascript"><!--
            google_ad_client = "pub-2140091590744860";
            google_ad_width = 300;
            google_ad_height = 250;
            google_ad_format = "300x250_as";
            google_ad_type = "image";
            google_ad_channel ="";
            google_color_border = "000000";
            google_color_link = "0000FF";
            google_color_bg = "FFFFFF";
            google_color_text = "000000";
            google_color_url = "008000";
            google_ui_features = "rc:0";
            //--></script>
            <script type="text/javascript"
            src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
            </script><br />
    '''
                file.write(adsense_content+"\n")
                file.close()
            except:
                print("mkdir error")

        # 資料庫選用
        # 內建使用 sqlite3                
        ormdb = "sqlite"
        #ormdb = "mysql"
        #ormdb = "postgresql"

        if ormdb == "sqlite":
            # 資料庫使用 SQLite
            # 這裡應該要使用 peewee 建立資料庫與表格
            try:
                conn = sqlite3.connect(data_dir+"task.db")
                cur = conn.cursor()
                # 建立資料表
                cur.execute("CREATE TABLE IF NOT EXISTS task( \
                        id INTEGER PRIMARY KEY AUTOINCREMENT, \
                        name TEXT, \
                        owner TEXT, \
                        type TEXT, \
                        time TEXT, \
                        content TEXT, \
                        ip TEXT, \
                        follow INTEGER);")
                cur.close()
                conn.close()
            except:
                print("can not create db and table")
        elif ormdb == "mysql":
            # 嘗試建立資料庫與資料表
            # 這裡應該要使用 peewee 建立資料庫與表格
            if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
                host=str(os.environ[str('OPENSHIFT_MYSQL_DB_HOST')])
                port=int(os.environ[str('OPENSHIFT_MYSQL_DB_PORT')])
                db='cadp'
                user=str(os.environ[str('OPENSHIFT_MYSQL_DB_USERNAME')])
                passwd=str(os.environ[str('OPENSHIFT_MYSQL_DB_PASSWORD')])
            else:
                host="yourhost"
                port=3306
                db='yourdb'
                user='youruser'
                passwd='yourpassword'
            charset='utf8'
            # 案例建立時, 就嘗試建立資料庫與資料表
            try:
                conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, charset=charset)
                # 建立資料庫
                cur = conn.cursor()
                cur.execute("CREATE DATABASE IF NOT EXISTS "+db+" CHARACTER SET UTF8;")
                # 建立資料表
                cur.execute("USE "+db+";")
                cur.execute("CREATE TABLE IF NOT EXISTS `task` ( \
                    `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT, \
                    `name` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci', \
                    `owner` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci', \
                    `type` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci', \
                    `time` DATETIME NOT NULL COLLATE 'utf8_unicode_ci', \
                    `content` LONGTEXT COLLATE 'utf8_unicode_ci', \
                    `ip` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci', \
                    `follow` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0', \
                    PRIMARY KEY (`id`)) \
                    COLLATE='utf8_general_ci' default charset=utf8 ENGINE=InnoDB;")
                cur.close()
                conn.close()
            except:
                print("can not create db and table")
        else:
            # 使用 PostgreSQL
            # 嘗試建立資料庫與資料表
            # 這裡應該要使用 peewee 建立資料庫與表格
            if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
                host=str(os.environ[str('OPENSHIFT_POSTGRESQL_DB_HOST')])
                port=int(os.environ[str('OPENSHIFT_POSTGRESQL_DB_PORT')])
                db='cadp'
                user=str(os.environ[str('OPENSHIFT_POSTGRESQL_DB_USERNAME')])
                passwd=str(os.environ[str('OPENSHIFT_POSTGRESQL_DB_PASSWORD')])
            else:
                host="localhost"
                port=3306
                db='cadp'
                user='root'
                passwd='root'
            charset='utf8'
            # 案例建立時, 就嘗試建立資料庫與資料表
            try:
                conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, charset=charset)
                # 建立資料庫
                cur = conn.cursor()
                cur.execute("CREATE DATABASE IF NOT EXISTS "+db+";")
                # 建立資料表
                cur.execute("USE "+db+";")
                cur.execute("CREATE TABLE IF NOT EXISTS `task` ( \
                    `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT, \
                    `name` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci', \
                    `owner` VARCHAR(255) NOT NULL COLLATE 'utf8_unicode_ci', \
                    `type` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci', \
                    `time` DATETIME NOT NULL COLLATE 'utf8_unicode_ci', \
                    `content` LONGTEXT COLLATE 'utf8_unicode_ci', \
                    `ip` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci', \
                    `follow` BIGINT(20) UNSIGNED NOT NULL DEFAULT '0', \
                    PRIMARY KEY (`id`)) \
                    COLLATE='utf8_general_ci' default charset=utf8 ENGINE=InnoDB;")
                cur.close()
                conn.close()
            except:
                print("can not create db and table")



