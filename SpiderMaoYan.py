# -*- coding:utf-8 -*-
#!/usr/bin/env python3
'''
data:2018-10-11
author:justong
goal: 爬取猫眼《无双》影评
'''

# 获取猫眼电影介绍url   http://maoyan.com/films/?id
import os,requests,json,csv,datetime,re,string
import pandas as pd
import time
from bs4 import BeautifulSoup

class SpiderMaoYan(object):

    def __init__(self,movieID):
        self.movieID = movieID
        self.path = './movieproject/{}'.format(movieID)
        self.file_name = self.path + '/{}.csv'.format(self.movieID)

    # 获得评论总数
    def get_total(self):
        header = self.get_header()
        # 猫眼电影短评接口
        comment_api = 'http://m.maoyan.com/mmdb/comments/movie/{0}.json?_v_=yes'.format(self.movieID)
        # 发送get请求
        response_comment = requests.get(comment_api, headers= header)
        json_comment_txt = json.loads(response_comment.text)
        json_resqonse = json_comment_txt["total"]
        # 获取的json_resqonse为list类型
        return int(json_resqonse)

    # 发送get请求获取响应
    def get_resqonse(self,offset,startTime):

        # 猫眼电影短评接口
        header = self.get_header()
        json_resqonse = {}
        while True:
            try:
                comment_api = 'http://m.maoyan.com/mmdb/comments/movie/{0}.json?_v_=yes&offset={1}&startTime={2}'.format(self.movieID,offset,startTime)
                # print(comment_api)
                # 发送get请求
                response_comment = requests.get(comment_api,headers = header)
                json_comment_txt = json.loads(response_comment.text)
                if int(json_comment_txt["total"]) == 0:
                    json_endflag = True
                    json_resqonse = {'json_comment': '', 'json_endflag': json_endflag}
                    break
                else:
                    json_endflag = False
                json_comment = json_comment_txt["cmts"]
                json_resqonse = {'json_comment':json_comment,'json_endflag':json_endflag}
                break
            except KeyError as e:
                print("发生错误，等待10秒！Error:",e)
                time.sleep(10)
        # 获取的json_resqonse为dict类型,其中的‘json_comment’为list类型
        return json_resqonse

    # 解析响应的数据，获取需要使用的内容
    def get_info(self,json_comment):
        list_info = []
        for data in json_comment:
            startTime = data['startTime']
            if 'cityName' in data:
                cityName = data['cityName']
            else:
                cityName = ''
            content = data['content'].replace('\n',' ')
            # 处理评论里换行的问题
            if 'gender' in data:
                gender = data['gender']
            else:
                gender = 0
            table = str.maketrans('','',string.punctuation)
            nickName = data['nickName'].translate(table)
            userLevel = data['userLevel']
            score = data['score']
            list_one = [startTime,cityName,gender,nickName,userLevel,score,content]
            list_info.append(list_one)
        return list_info

    # 将解析好的list存入文件
    def file_do(self,list_info):

        file_name = self.path + r'/{}.csv'.format(self.movieID)
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        if not os.path.exists(file_name):
            with open(file_name,'a',encoding='utf-8') as f:
                f.write('')

        file_size = os.path.getsize(file_name)
        if file_size == 0:
            # 建立文件格式dataframe对象
            name = ['时间','城市','性别','昵称','评论者等级','评分','评论内容']
            file_test = pd.DataFrame(data=list_info,columns=name)
            # 数据写入
            file_test.to_csv(file_name,encoding='utf-8',index=False)
        else:
            with open(file_name,'a+',encoding='utf-8',newline='') as file_test:
                # 追加到文件后面
                writer = csv.writer(file_test)
                writer.writerows(list_info)

    # 构建一个header
    def get_header(self):
        header = {
            "User-Agent": "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
            "Host": "m.maoyan.com",
            "Referer": "http://m.maoyan.com/movie/{}/comments?_v_=yes".format(self.movieID)
        }
        return header

    # 获取电影基本信息
    def movieinfo(self):
        movieID = self.movieID
        header = self.get_header()
        url = 'http://m.maoyan.com/movie/{}?_v_=yes'.format(movieID)
        response = requests.get(url,headers= header)
        soup = BeautifulSoup(response.text,'html.parser')
        # 获取电影名称
        moviename =''
        sp = soup.find('div',class_ = 'movie-name text-ellipsis')
        for str in sp.find_all('span'):
            s = str.string.strip()
            if s:
                moviename = moviename + s
        print('电影名称：%s' % moviename)
        # 获取电影名称评分
        moviescore = 0
        sp = soup.find('div',class_ = 'released-score')
        moviescore = sp.span.string
        print('电影评分：%s' % moviescore)
        # 获取电影名称
        moviepremiere =''
        sp = soup.find_all('div',class_ = 'movie-content-row')
        for str in sp:
            s = str.string
            if s:
                moviepremiere = moviepremiere + s
        moviepremiere = re.search(r'\d{4}\-\d{2}\-\d{2}',moviepremiere).group(0)
        print('首映时间：%s' % moviepremiere)
        movieinfo = {'moviename':moviename,
                     'moviescore':moviescore,
                     'moviepremiere':moviepremiere
                     }

        return movieinfo

    # 完成爬取工作
    def all_info(self):
        # 获取当前时间
        movieinfo = self.movieinfo()
        print('官方显示评论总数:%s' % self.get_total())
        now = datetime.datetime.now()
        nowdatetime = now.strftime('%Y-%m-%d %H:%M:%S')
        print('抓取开始时间:' + nowdatetime)
        flag_time = now
        # 判断是否继续之前的任务
        if os.path.exists(self.file_name) and os.path.getsize(self.file_name)>0:
            with open(self.file_name, 'r', encoding='utf-8',newline='') as f:
                reader= csv.reader(f)
                rows =list(reader)
                stime = rows[-1][0]
                flag_time = datetime.datetime.strptime(stime,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=-1)
                print('继续任务，当前评论时间%s' % flag_time)
        print('-' * 50)
        begin_time = movieinfo['moviepremiere'] + ' 00:00:00'
        begin_time = datetime.datetime.strptime(begin_time,'%Y-%m-%d %H:%M:%S')
        page = 0
        # 从当前时间开始，一直到上映时间为止
        while flag_time > begin_time:
            startTime = flag_time.strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20').replace(':','%3A')
            # 发送get请求，参数offset和startTime
            json_resqonse = self.get_resqonse(0,startTime)
            json_comment = json_resqonse['json_comment']
            # 解析需要的评论内容
            list_info = self.get_info(json_comment)
            # 获得第15位的评论时间
            flag_time_txt = list_info[14][0]
            # 第15位的时间再提前一秒，避免重复
            flag_time = datetime.datetime.strptime(flag_time_txt,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=-1)
            # 数据存储
            self.file_do(list_info)
            page += 1
            if page % 100 == 0:
                print('已获取评论数%s,当前评论时间%s' % (page*15,flag_time_txt))
                time.sleep(1)
        done_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('-'*50)
        print('抓取完成时间%s' % done_time)

if __name__ == '__main__':
    wushuang = SpiderMaoYan(1217141)
    wushuang.all_info()


