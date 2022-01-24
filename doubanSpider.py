import re
import urllib.request,urllib.error
import bs4
import xlwt
import sqlite3


PAGE=25
find_link=re.compile(r'<a href="(.*?)">')
find_title=re.compile(r'<em>(.*?)</em>')
find_rating=re.compile(r'<span class="rating(.*?)-t"></span>')
find_comment=re.compile(r'<span class="comment">(.*?)</span>',re.S)
find_date=re.compile(r'<span class="date">(.*?)</span>')
dbpath='DoubanMovie4.db'

def main():
    baseurl = 'https://movie.douban.com/people/71178159/collect?start='

    datalist=getData(baseurl)
    print('数据读取完毕......')

#    saveData(datalist)    #save in EXCEL

    saveDB(datalist)
    print('数据存储完毕......')

#edit Cookie!
def askURL(url):
    html=''
    headers={
        'Cookie':'xxxxxxxxxx'
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    req=urllib.request.Request(url,headers=headers)
    try:
        response=urllib.request.urlopen(req)
        html=response.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e,'code'):
            print('Error code:%s'%e.code)
        elif hasattr(e,'reason'):
            print('Error Message:%s'%e.reason)
    return html



def getData(baseurl):

    datalist=[]
    print("读取中......")

    for i in range(0,PAGE):
        url=baseurl+str(i*15)

        html=askURL(url)

        soup=bs4.BeautifulSoup(html,'html.parser')
        for item in soup.find_all('div',class_='item'):
            item=str(item)
            data=[]
            target_title = re.findall(find_title, item)[0]
            data.append(target_title)

            if len(re.findall(find_rating, item))!=0:
                target_rating = re.findall(find_rating, item)[0]
            else:
                target_rating ='Not Rating'
            data.append(target_rating)

            if len(re.findall(find_comment, item)) != 0:
                target_comment = re.findall(find_comment, item)[0]
            else:
                target_comment = 'No comments'
            data.append(target_comment)

            target_date = re.findall(find_date, item)[0]
            data.append(target_date)

            datalist.append(data)
    print('读取完毕，项目数:%d'%len(datalist))
    return datalist

def saveData(datalist,path='.'):

    workbook=xlwt.Workbook()
    worksheet=workbook.add_sheet('豆瓣电影')
    col=('Title','Rating','Comments','Date')
    print("开始保存......")
    for i in range(0,len(col)):
        worksheet.write(0,i,col[i])
    for i in range(0,len(datalist)):
        data=datalist[i]
        for j in range(0,4):
            worksheet.write(i+1,j,data[j])
        print("保存第%d条" % (i + 1))
    workbook.save('豆瓣爬虫.xls')


def saveDB(datalist,dbpath=dbpath):

    initDB(dbpath)
    connect=sqlite3.connect(dbpath)
    print("打开数据库......")
    cursor=connect.cursor()
    for data in datalist:
        for i in range(0,len(data)):
            data[i]=str(data[i]).replace('"',' ')
            data[i]='"'+data[i]+'"'
        sql='''
        insert into movies (Name, Rating, Comment, Date)
        values (%s)
        '''%','.join(data)
        print (data)
        cursor.execute(sql)
        connect.commit()
    cursor.close()
    connect.close()



def initDB(dbpath):
    connect=sqlite3.connect(dbpath)
    cursor=connect.cursor()
    sql='''
    create table movies
    (Id integer primary key autoincrement not null,
    Name text not null,
    Rating text,
    Comment text, 
    Date text);
    '''
    cursor.execute(sql)
    connect.commit()
    connect.close()


if __name__=="__main__":
    main()
    print("结束！")

