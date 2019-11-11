#
#  bjbook.net 版权所有
#
# db_*开头的函数,对数据库进行操作
# html_*开头的函数， 输出html文件。
# svn_*开头的函数，操作svn
# git_*开头的函数，操作git
#
import os
import sys
import datetime
import sqlite3
import echarts

import xml.etree.ElementTree as ET


svn_url = ""
svn_revision = ""   #最新的版本号
g_line_count = 0
debug = True
revision_range = "{2017-1-1}:HEAD"

#文件名后缀
file_exts = [".java",".js", ".css" ".py", ".hpp", ".cpp", ".h", ".c", 
    ".conf", ".html", ".txt", ".sql", ".xml"]


class Stat:

    def __init__(self):
        self.mod_line = 0       #修改行数
        self.add_line = 0       #增加代码行数
        self.start_date = None  #开始提交代码时间
        self.end_date = None    #最后提交代码时间
        self.times = 0          #提交次数
    
    #代码行修改量
    def add_Modify(self, line):
        self.mod_line += line

    #代码行增加量
    def add_Add(self, line):
        self.add_line += line
        
    def add_time(self):
        self.times += 1

    #设置开始时间，和结束时间
    def update_time(self, time):
        date = datetime.datetime.strptime(time[0:19], "%Y-%m-%dT%H:%M:%S");
        if(self.start_date == None):
            self.start_date = date
        if(self.end_date == None):
            self.end_date = date
        
        if(date < self.start_date):
            self.start_date = date
        if(date>self.start_date):
            self.end_date = date

    def __str__(self):
        return ("add_line:"+str(self.add_line) +"mod_line:"+str(self.mod_line)
            + "start_date:" + str(self.start_date)+"end_date:" +str(self.end_date))




def stat_file_line_count(path):
    """统计文件个数和代码行数，空行不计入代码
    
    path: 目录路径
    return: (文件个数, 文件行数, {文件类型:个数}, {文件类型:代码行数})
    """
    print("work:",path)
    file_count = 0 #文件总数
    line_count = 0 #代码行总数
    file_exts_count = dict() #特定类型的文件个数统计
    file_exts_line = dict()  #特定类型文件行数统计
    for dirpath, dirname, filenames in os.walk(path):
        for f in filenames:
            full_name = os.path.join(dirpath, f)
            file_count += 1
            fline = 0
            with open(full_name, 'r', errors='ignore') as f:
                for raw_line in f:
                    str=raw_line.strip()
                    if(len(str)>=1):
                        fline += 1
            line_count += fline
            print("line_count=", line_count)
            found = False 
            for ext in file_exts:
                if(full_name.endswith(ext)):
                    file_exts_count[ext] = file_exts_count.get(ext, 0)+1
                    file_exts_line[ext]  = file_exts_line.get(ext, 0)+fline
                    found = True
                    break
            if(found==False ):
                file_exts_count["other"] = file_exts_count.get("other", 0)+1
                file_exts_line["other"]  = file_exts_line.get("other", 0)+fline
                
    return (file_count, line_count, file_exts_count, file_exts_line)

#统计各种文件类型及其代码行数，最后计算百分比
#例如java文件 50个，共5000行，文件占比40%， 代码行占比20%，每一个文件行数
#主要统计*.java,*.py, *.cpp *.cxx *.c  *.conf *.html *.xml

        
def html_out_author(stats, files):
    """输出项目人员贡献情况   """

    print('<h2>项目参与人员贡献情况</h2>', file=files)
    print('<table  rules="groups"', file=files)
    print('<thead> <tr><th>开发人员</th><th>代码行数</th><th>提交次数</th><th>每次代码行数</th>', file=files)
    print('<th>开始参与时间</th><th>最后提交时间</th></tr></thead>', file=files)
        
    for key, stat in stats.items():
        #print(key, file=files)
        print('<tr  class="odd">', file=files)
        print(f'<th><a href="user_{key}.html" class="author">{key}</a></th>', file=files)
        print(f'<td>{stat.add_line}</td>', file=files)
        print(f'<td>{stat.times}</td>', file=files)
        print(f'<td>{stat.add_line/stat.times:0.2f}</td>', file=files)
        print(f'<td>{stat.start_date}</td>', file=files)
        print(f'<td>{stat.end_date}</td>', file=files)
        print(f'</tr>', file=files)
  
    print('</table>', file=files)


def html_out_head(files):
    print('<html xmlns="http://www.w3.org/1999/xhtml">', file=files)
    print('<head>', file=files)
    print('<script src="echarts.simple.min.js"></script>', file=files)
    print('<meta http-equiv="content-type" content="text/html; charset=UTF-8">', file=files)
    print('<title>PythonStatSVN - Development Statistics</title>', file=files)
    print('<link rel="stylesheet" href="objectlab-statcvs.css" type="text/css"/>', file=files)
    print('</head>', file=files)
    print("<body>", file=files)

def html_out_bottom(files):
    print('<h2></h2>', file=files)
    print('<div>由PythonStatSVN生成，版权所有 2018</div>', file=files)
    print('</body></html>', file=files)

def html_out_sum(file_count, line_count, files):
    """输出项目概况"""
    print('<h2>项目概况</h2>', file=files)
    print('<table  rules="groups">', file=files)
    print(f'<tr><td>报告产生时间:</td> <td>{datetime.datetime.today()}</td></tr>', file=files)
    print(f'<tr><td>统计时间段:</td> <td>所有</td></tr>', file=files)
    print(f'<tr><td>文件总数:</td><td>{file_count}</td></tr>', file=files)
    print(f'<tr><td>代码行数:</td><td>{line_count}</td></tr>', file=files)
    revision_count = db_get_revision_count()
    print(f'<tr><td>提交总次数:</td><td>{revision_count}</td></tr>', file=files)
    author_count = db_get_author_num()
    print(f'<tr><td>开发人员总数:</td><td>{author_count}</td></tr>', file=files)
    
    print('</table>', file=files)

def html_out_link(files):
    print('<div><a href="files.html">文件统计</a>', file=files)
    print('<a href="developer.html">开发人员统计</a>', file=files)
    print('</div>', file=files)
    
def html_out_tend(files):
    keys, code_list = db_get_tendency()
    code_len =len(code_list)
    print(keys)
    html_str = echarts.html_line_out(keys, code_list, name="main", width=600, height=400)
    print('<h2>项目代码趋势</h2>', file=files)
    print(html_str, file=files)
    
#todo1: 代码行数统计，文件总数统计，开发人员总数统计, 
#todo2： 统计指定时间段，默认不限制
#todo2: 开发人员周趋势统计

def db_init():
    """创建数据库表"""
    conn = sqlite3.connect('code.db')
    #创建连接完成之后，你可以创建一个游标对象(Curson), 然后调用execute方法来执行SQL语句。
    c = conn.cursor()
    # Create table code: 版本号，作者，日期，提交注释消息，修改行数
    c.execute('''CREATE TABLE IF NOT EXISTS code(
            revision text unique,    
            author text, 
            r_date text, 
            msg text, 
            line integer)''')
            
    # Create table files: 版本号，文件名，用于统计文件名的修订次数
    c.execute('''CREATE TABLE IF NOT EXISTS files(
            revision text,    
            file text)''')
    conn.commit()
    conn.close()
    
            
def db_revision_add(revision, author, date, msg, line):
    """将revision信息写入数据库"""
    conn = sqlite3.connect('code.db')
    #创建连接完成之后，你可以创建一个游标对象(Curson), 然后调用execute方法来执行SQL语句。
    c = conn.cursor()
    # Insert a row of data
    try:
        c.execute("INSERT INTO code VALUES (?,?,?,?,?)", [revision, author, date, msg, line])
    except:
        print("except")
    conn.commit()
    conn.close()

    
def db_get_author_num():
    """获取开发人员数量"""
    conn = sqlite3.connect('code.db')
    #创建连接完成之后，你可以创建一个游标对象(Curson), 然后调用execute方法来执行SQL语句。
    c = conn.cursor()
    c.execute("SELECT count(DISTINCT author) FROM code")
    rets = c.fetchone()
    conn.commit()
    conn.close()
    return rets[0]
    
#获取提交总次数    
def db_get_revision_count():
    """获取提交总次数"""
    conn = sqlite3.connect('code.db')
    #创建连接完成之后，你可以创建一个游标对象(Curson), 然后调用execute方法来执行SQL语句。
    c = conn.cursor()
    c.execute("SELECT count(revision) FROM code")
    rets = c.fetchone()
    conn.commit()
    conn.close()
    return rets[0]

def db_get_author():
    """获取作者列表"""
    conn = sqlite3.connect('code.db')
    #创建连接完成之后，你可以创建一个游标对象(Curson), 然后调用execute方法来执行SQL语句。
    c = conn.cursor()
    c.execute("SELECT DISTINCT author FROM code")
    r = c.fetchall()
    t = [(member[0]) for member in r]
    conn.commit()
    conn.close()
    return t


#select strftime('%H',r_date)  from code  #取小时
#localtime 取本地时区
#获取用户每小时时间点的提交次数。 主要关注用户在每天的工作时间。
#select count(revision), strftime('%H', r_date, 'localtime')  from code where author='zhang' group by strftime('%H', r_date, 'localtime')  
def db_get_hours(author=None):
    """获取用户每小时时间点的提交次数。 主要关注用户在每天的工作时间。
    
    如果为None，就表示所有用户
    
    """
    conn = sqlite3.connect('code.db')
    c = conn.cursor()

    sql = "select strftime('%H', r_date, 'localtime'), count(revision) from code "
    if(author!=None):
        sql += f" where author='{author}' "
    sql += " group by strftime('%H', r_date, 'localtime')"
    #本地时间
    c.execute(sql)
    r = c.fetchall()
    t = [(member[0], member[1]) for member in r]
    #[('07', 1), ('16', 2), ('17', 1), ('18', 1), ('20', 3), ('21', 4), ('22', 6)]
    #将没有的小时时间点值填充0
    #t为查询得出的一天中的小时记录数，如果为没有值，表示为零，把没有值的补充为0
    t2 = [(str(i).zfill(2) , 0) for i in range(24)]  #构造每个小时都为0的队列
    
    #填充有值的小时
    for(n, m) in t:
        t2[int(n)] = (n,m)

    conn.close()
    return t2

#获取指定用户的星期中每一天提交次数
def db_get_day(author=None):
    conn = sqlite3.connect('code.db')
    c = conn.cursor()

    #本地时间
    sql = "select strftime('%w',r_date, 'localtime'), count(revision) from code "
    if(author != None):
        sql += f" where author='{author}' "
    sql += " group by strftime('%w', r_date, 'localtime')"
    c.execute(sql)
    if(debug==True):
        print(sql)
    r = c.fetchall()
    t = [(member[0], member[1]) for member in r]
    #[('0', 10), ('2', 4), ('3', 1), ('5', 1), ('6', 2)]
    
    #t为查询得出的一星期中每天提交数，如果为没有值，表示为零，把没有值的补充为0
    t2 = [(str(i), 0) for i in range(7)]  #构造每天(星期中)都为0的队列
    #填充有值的天
    for(n, m) in t:
        t2[int(n)] = (n,m)

    conn.close()
    return t2

#统计星期中每天的提交次数
#select count(revision),  strftime('%w',r_date)   from code group by strftime('%w',r_date)  
#按作者和星期
#select count(revision),  strftime('%w',r_date), author from code 
#group by strftime('%w',r_date), author

    
#时间日期计算
#select sum(line) from code where r_date > "2018-05-06"
#SELECT date('now', "-10 days") 当前时间前十天
#SELECT sum(line) from code where r_date > date('now', "-4 days") 
#select julianday('2017-10-03') - julianday('2016-06-01');   时间差值(天)
#select julianday(max(r_date))-julianday(min(r_date)) from code  时间差值(天)

#select sum(line) from code where julianday(r_date) > julianday("2018-05-11T14:20:23.780295Z") -2
def db_get_tendency():
    ''' 总代码趋势计算,返回代码趋势列表
 
    1, 获取最大时间，
    2, 获取时间差值，
    如果差值小于30天，则获取每天修改的代码量，然后获取时间序列
    如果大于365天，则获取每月1号的代码量'''
    conn = sqlite3.connect('code.db')
    c = conn.cursor()
    #1
    c.execute("select max(r_date) from code")
    rets = c.fetchone()
    max_date = rets[0]
    
    #2时间差值
    c.execute("SELECT julianday(max(r_date))-julianday(min(r_date)) FROM code")
    rets = c.fetchone()
    days = int(float(rets[0]))
    
    #3 获取时间序列
    "2018-05-13T13:41:50.772218Z"
    date_seq = get_date_seq(max_date[0:10], days)
    print(date_seq)

    if(days<30):    #获取每天的数据
        i=days
        days_code =[]
        while(i>0):
            sql_str=f"select sum(line) from code where julianday(r_date) > julianday('{max_date}') - {i}"
            print(sql_str)
            c.execute(sql_str)
            rets = c.fetchone()
            days_code.append(rets[0])
            i -= 1
        print("days_code:", days_code)
    conn.commit()
    conn.close()
    code_tend = [g_line_count-i for i in days_code]
    return (date_seq, code_tend)
   
def get_date_seq(end, days):
    """获取时间序列  例如:
    end : "2018-05-20"
    day :  3
    ret : ["2018-05-17", "2018-05-18","2018-05-19","2018-05-20"]
    """
    rets = []
    date_time_end = datetime.datetime.strptime(end, "%Y-%m-%d")   
    date_end = date_time_end.date()     
    for i in range(days):
        delta = datetime.timedelta(days=(days-i))
        rets.append(str(date_end-delta))
    a=rets.append(end)
    return rets
 
exts_file = {} #{文件类型:个数}
exts_line = {} #{文件类型:代码行数}

stats = {}  ##{"作者":stat}
 
#个人提交代码排行，共六项， 作者，代码行数, 提交次数，平均每次行数、最早开始时间，最后结束时间
def svn_stat(src_path):
    print("1, 获取SVN的log xml")
    os.system(f"svn log {svn_url} -r {revision_range} -v --xml > svnlog.xml")
    tree = ET.parse('svnlog.xml')
    root = tree.getroot()
    authors = {}
    global stats
    print("2, 获取每一个提交的差异行数,并写入数据库")
    for child in root.findall('logentry'):
        author = child.find('author').text
        authors[author]= authors.get(author, 0) +1
        date  = child.find('date').text
        revision = child.get('revision')
        msg = child.get('msg')
        add_line, mod_line = svn_get_diff(svn_url, revision)
        print(revision, author, date)
        print(add_line, mod_line)
        stats[author] = stats.get(author, None)
        if(stats[author]==None):
            stats[author]= Stat()
        stat = stats[author]
        stat.update_time(date)
        stat.add_Modify(mod_line)
        stat.add_Add(add_line)
        stat.add_time()
        db_revision_add(revision, author, date, msg, add_line)
        
    print("3, 计算")
    
    f = zip(authors.values(), authors.keys())
    f2 = sorted(f, reverse=True)
    for value in f2:
        print(value)
    print(type(stats))
    
    global exts_file, exts_line
    file_count, line_count, exts_file, exts_line = stat_file_line_count(src_path)
    global g_line_count
    g_line_count = line_count
    print("type(exts_file):", type(exts_file))
    for key in exts_file:
        print("key:", key, " value:", exts_file[key], " line", exts_line[key] )
    files = open("index.html", mode='w', encoding='utf-8')
    html_out_head(files)
    html_out_sum(file_count,line_count, files)
    html_out_link(files)
    html_out_tend(files)
    html_out_author(stats, files)
    html_out_bottom(files)
    files.close()
    
"""
Path: .
Working Copy Root Path: C:\statsvn\zookeeper
URL: https://svn.apache.org/repos/asf/zookeeper/trunk
Relative URL: ^/zookeeper/trunk
Repository Root: https://svn.apache.org/repos/asf
Repository UUID: 13f79535-47bb-0310-9956-ffa450edef68
Revision: 1830915
Node Kind: directory
Schedule: normal
Last Changed Author: phunt
Last Changed Rev: 1759917
Last Changed Date: 2016-09-09 06:10:09 +0800 (周五, 09 9月 2016)
"""
def get_svn_info(str_dir):
    svn_info = dict()
    print(f"project:{str_dir}")
    f = os.popen(f"svn info {str_dir}", mode='r')
    for line in f:
        #print(line)
        words = line.split()
        if(len(words)>=2):
            if(words[0]=="URL:"):
                svn_info["URL"]=words[1]
            elif(words[0]=="Revision:"):
                svn_info["Revision"]=int(words[1])
            elif((len(words)>4) and words[2]=="Date:"):
                svn_info["Date"] = words[3];
    print(svn_info)
    return svn_info

"""
svn diff https://svn.apache.org/repos/asf/zookeeper/trunk -c 1759917
return: add_line, mod_line
"""
def svn_get_diff(svn_url, revision):
    cmd = f"svn diff {svn_url} -c {revision} > svn_diff.log"
    print(cmd)
    line_plus = 0
    line_minus = 0
    os.system(cmd)
    f = open("svn_diff.log", mode='r', errors='ignore')
    #all_line = f.read().decode('utf-8', 'ignore')
    
    for line in f:
        line = line.strip()
        if((len(line)>3) and (line[0]=="+" or line[0]=="-") and line[2] != "+" and line[2] != "-"):
            if(line[0]=="+"):
                line_plus += 1
            else:
                line_minus += 1
    #增加行有可能为负值，例如删除了一些没有的代码
    #修改行直接为diff文件中的“-”行
    add_line = line_plus - line_minus
    mod_line = line_minus
    return (add_line, mod_line)

#>svn cat python001.rst -r 2
def get_svn_file_line(svn_url, revision):
    cmd = f"svn cat {svn_url} -r {revision} > svn_cat.log"
    print(cmd)
    line_count = 0
    f = open("svn_cat.log", mode='r', errors='ignore')
    for line in f:
        line_count += line
    return line_count;
    
#输入为列表，列表元素为元祖
def html_out_author_hours(k_v, auth_name, files):

   keys = [i for (i, j) in k_v]
   values = [j for (i, j) in k_v]
   html_str = echarts.html_bar_out(keys, values, name="main_hours", width=600, height=400)
   print(f'<h2>{auth_name} 一天中的每小时活跃度量</h2>', file=files)
   print(html_str, file=files)

#输入为列表，列表元素为元祖
def html_out_author_days(k_v, auth_name, files):

   keys = [i for (i, j) in k_v]
   values = [j for (i, j) in k_v]
   html_str = echarts.html_bar_out(keys, values, name="main_day", width=600, height=400)
   print(f'<h2>{auth_name} 一周中的每天活跃度量</h2>', file=files)
   print(html_str, file=files)


#按开发人员输出
def html_out_develop():

#输出开发人员概述信息。
    filename = "developer.html"
    files = open(filename, mode='w', encoding='utf-8')
    html_out_head(files)
    print(f'<div> <a href="index.html">开发人员状态统计PythonStatSVN</a> &gt;&gt; </div>', file=files)
    print('</br>', file=files)
    
    html_out_author(stats, files)
    
    #整个项目的活跃提交小时时间，如果是18点以后通常是加班时间。
    s1 = db_get_hours()
    html_out_author_hours(s1, "", files)
    
    #整个项目的星期中的每天活跃时间，可以看出是工作日还是周末，周末就是业余项目
    s2 = db_get_day()
    html_out_author_days(s2, "", files)

    html_out_bottom(files)
    files.close()
    
    #按开发人员输出，每人一个文件
    t = db_get_author()
    for author in t:
        filename = f"user_{author}.html"
        files = open(filename, mode='w', encoding='utf-8')
        html_out_head(files)
        print(f'<div> <a href="index.html">{author} 开发状态统计PythonStatSVN</a> &gt;&gt; </div>', file=files)
        print('</br>', file=files)
        s1 = db_get_hours(author)
        html_out_author_hours(s1, author, files)
        
        s2 = db_get_day(author)
        html_out_author_days(s2, author, files)

        html_out_bottom(files)
        files.close()

#files.html
def html_out_files():
    """输出文件的统计信息
    
    1，文件类型，个数，行数，平均每文件行数
    todo:2，大文件top10，按代码排序，文件名，行数，最后修改时间，修订次数
    todo:3，修订次数top10, 按修订次数排序，文件名，修订次数，最后修改时间。
    """
    #exts_file, exts_line
    #排序，按代码行数进行排序，找出最大的文件类型。
    t = [(j, i) for i, j in exts_line.items()]
    t.sort(reverse=True)
    print(t)
    for line, ext in t:
       print(ext, line, exts_file[ext], line/exts_file[ext])
    
    filename = "files.html"
    files = open(filename, mode='w', encoding='utf-8')
    html_out_head(files)
    print('<div> <a href="index.html">文件统计PythonStatSVN</a> &gt;&gt; </div>', file=files)
    print('</br>', file=files)
       
    print('<h2>文件类型统计</h2>', file=files)
    print('<table  rules="groups"', file=files)
    print('<thead> <tr><th>文件类型</th><th>文件个数</th><th>代码行</th><th>平均每文件代码行数</th>', file=files)
    print('</thead>', file=files)
    all_line = 0  #行总数
    all_file = 0  #文件总数
    for line, ext in t:
        file_count=exts_file[ext]
        line_perfile=line/file_count
        all_line += line
        all_file += file_count 
        #print(ext, line, exts_file[ext], line/exts_file[ext])
        print('<tr  class="odd">', file=files)
        print(f'<td>{ext}</td>', file=files)
        print(f'<td>{file_count}</td>', file=files)
        print(f'<td>{line}</td>', file=files)
        print(f'<td>{line_perfile:0.2f}</td>', file=files)
        print(f'</tr>', file=files)
  
    #输出总计
    print('<tr  class="odd">', file=files)
    print('<td>总计</td>', file=files)
    print(f'<td>{all_file}</td>', file=files)
    print(f'<td>{all_line}</td>', file=files)
    print(f'<td>{all_line/all_file:0.2f}</td>', file=files)
    print(f'</tr>', file=files)
     
    print('</table>', file=files)
        
    html_out_bottom(files)
    files.close()

#todo 设置输出目录
def usage():
    print("svnstat.py [your project] V" )
    sys.exit(0)

#1，统计开发人员数量，代码行数，总共的文件数，统计时间。
#1，开发人员提交统计，分别为提交次数，提交总行数，修改行数， 平均每次提交行数。排名以及占比
#2, 过去12月开发人员提交占比。为0，不显示。12月以前按年计算。
#3， 每个人代码趋势图，可以看出每个人的参与时间。
#4，数据库来存储，便于分析。

def main(src_path):
    db_init()
    svn_info = get_svn_info(src_path)
    global svn_url,svn_revision
    svn_url = svn_info["URL"]
    svn_revision = svn_info["Revision"]
    svn_stat(src_path)
    html_out_develop()
    html_out_files()
  
if __name__ == "__main__":
    src_path = "."
    if(len(sys.argv)>1):
       src_path = sys.argv[1]
    main(src_path)
