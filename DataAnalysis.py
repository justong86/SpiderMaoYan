# -*- coding:utf-8 -*-
#!/usr/bin/env python3

from pyecharts import Bar,Pie,Geo,Line
from pyecharts import Grid,Page
import csv,json,datetime
from collections import Counter
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS

class DataAnlysis():

    def __init__(self,movieID):
        self.movieID = movieID
        self.path = './movieproject/{}'.format(movieID)

    # 处理城市名称不一致问题
    # 猫眼的城市名不带有‘市’‘县’字样，而地图数据是带的，例如烟台市在猫眼显示为‘烟台’
    def city_handles(self,cities):
        with open(r'./venv/lib/python3.6/site-packages/pyecharts/datasets/city_coordinates.json','r',
                  encoding='utf-8') as f:
            data = json.loads(f.read())
        data_new = data.copy()
        for city in cities:
            # 处理城市为空的数据
            if city == '香格里拉':
                print(city)
            if city == '':
                cities.remove(city)
                break
            for k in data:
                if k == city:
                    break
                if k.startswith(city):
                    # print('k=%s,city=%s'%(k,city))
                    data_new[city] = data[k]
                    # print('新增地图数据%s' % city)
                    break
                if k.startswith(city[0:-1]) and len(city)>2:
                    data_new[city] = data[k]
                    # print('新增地图数据%s' % city)
                    break
            #处理不存在于地图库的地名
            if city not in data_new:
                # print('%s不在地图库里' % city)
                cities.remove(city)
        print('地图库数据%s条'% len(data_new))
        # 覆盖到地图库的数据文件
        with open(r'./venv/lib/python3.6/site-packages/pyecharts/datasets/city_coordinates.json','w',
                  encoding='utf-8') as f:
            f.write(json.dumps(data_new,ensure_ascii=False))

        return cities

    # 从文件读取数据,返回dict类型
    def read_csv(self,path='default'):
        if path == 'default':
            path = self.path + r'/{}.csv'.format(self.movieID)
        time = []
        city = []
        gender = []
        nickname = []
        userlevel = []
        score = []
        content = []
        data_dict={
            'time':time,
            'city':city,
            'gender':gender,
            'nickname':nickname,
            'userlevel':userlevel,
            'score':score,
            'content':content
            }
        with open(path,'r',encoding='utf-8',newline='') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if i != 0:
                    time.append(row[0])
                    city.append(row[1])
                    gender.append(row[2])
                    nickname.append(row[3])
                    userlevel.append(row[4])
                    score.append(row[5])
                    content.append(row[6])
                i +=1
            print('共导入评论数据%s条' % i)
        return data_dict

    # 分析等级 和 评分，生成饼中饼图 和 玫瑰饼图
    def score_distribution(self,levels,scores):
        pie_l = Pie('评论者等级饼图')
        attr_l = ['一级','二级','三级','四级','五级']
        v_l = []
        v_l.append(levels.count('1'))
        v_l.append(levels.count('2'))
        v_l.append(levels.count('3'))
        v_l.append(levels.count('4'))
        v_l.append(levels.count('5'))
        pie_l.add(
            "",
            attr_l,
            v_l,
            radius=[60, 75],
            is_random=True,
            is_label_show=True
        )
        pie_l.add(
            "",
            attr_l,
            v_l,
            radius=[0, 55],
            rosetype="area",
        )
        # pie_l.render(self.path +'/level_pie.html')

        scores_coun = Counter(scores)
        scores_list = sorted(scores_coun.items(), key=lambda x: x[0], reverse=False)
        # print(scores_list)
        attr_s = []
        v_s =[]
        for score in scores_list:
            attr_s.append(score[0] + '分')
            v_s.append(score[1])
        pie_s = Pie('评论者评分饼图')
        pie_s.add(
                "",
                attr_s,
                v_s,
                is_random=True,
                radius=[30, 78],
                rosetype="area",
                is_label_show=True,
                legend_orient='vertical',
                legend_pos='left',
                legend_top='center'
        )
        page = Page()
        page.add(pie_l)
        page.add(pie_s)
        page.render(self.path +'/levelscore_pie.html')

    # 分析性别，生成饼状图
    def gender_distribution(self,gender):
        list_num = []
        list_num.append(gender.count('0'))
        list_num.append(gender.count('1'))   #男数量和
        list_num.append(gender.count('2'))   #女数量和
        attr = ['未知','男','女']
        pie = Pie('性别比例图')
        pie.add('',attr,list_num,is_label_show =True)
        pie.render(self.path + r'/gender_pie.html')

    # 分析评论时间，生成时间折线图
    def time_distribution(self, times):
        # 计算v1，按小时统计,计算V2,按天统计
        date_hour = []
        date_day = []
        for time in times:
            dtime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            date_hour.append(dtime.strftime('%m-%d|%H'))
            date_day.append(dtime.strftime('%m-%d'))

        # 按时间升序排序
        date_hour.sort()
        date_day.sort()
        # 不能用counter类，因为他会排序
        date_hour_dict = {}
        for date in date_hour:
            if date not in date_hour_dict:
                date_hour_dict[date] = 1
            else:
                date_hour_dict[date] += 1
        # print(date_hour_dict)
        # 每日总数
        date_day_dict = {}
        for date in date_day:
            if date not in date_day_dict:
                date_day_dict[date] = 1
            else:
                date_day_dict[date] += 1
        # print(date_day_dict)

        line_top = Line("评论时间(小时)折线图")
        attr1, v1 = line_top.cast(date_hour_dict)
        # print(attr)
        # print(v)
        line_top.add(
            "时间(小时)",
            attr1,
            v1,
            mark_point=['max'],
            mark_line=['average'],
            is_fill=True,
            area_color="#FFCCCC",
            area_opacity=0.3,
            is_smooth=True,
            is_datazoom_show=True,
            datazoom_type="both",
            datazoom_xaxis_index=[0, 1]
        )
        # line.render(self.path + r'/time_line.html')
        line_bottom = Line("")
        attr2, v2 = line_bottom.cast(date_day_dict)
        line_bottom.add(
            "时间(天)",
            attr2,
            v2,
            legend_pos="60%",
            mark_point=["max", "min"],
            mark_line=["average"],
            # is_yaxis_inverse=True,
            xaxis_pos="top",
            is_datazoom_show=True
        )

        grid = Grid(width=1200, height=800)
        grid.add(line_top, grid_bottom='60%')
        grid.add(line_bottom, grid_top='50%')
        grid.render(self.path + r'/time_line.html')

    # 分析城市，生成可视化地图分布
    def city_distribution_bar(self, cities):
        # 统计城市名称,该城市出现的次数
        # for city in cities:
        #     if city not in city_dict:
        #         city_dict[city] = cities.count(city)
        # 按照次数大小排序
        city_dict = Counter(cities)
        sort_list = sorted(city_dict.items(),key=lambda x:x[1],reverse=True)
        city_name = []
        city_num = []
        for i in range(len(sort_list)):
            city_name.append(sort_list[i][0])
            city_num.append(sort_list[i][1])

        bar = Bar('评论者城市图示')
        bar.add('',city_name,city_num,
                is_datazoom_show=True,
                datazoom_type='both',
                is_label_show=True,
                )
        bar.render(self.path + r'/city_bar.html')

    def city_distribution_geo(self, cities):
        # 统计城市名称,该城市出现的次数
        for city in cities:
            if city == '':
                cities.remove(city)

        coun = Counter(cities)
        # 处理地图库数据
        city_name = self.city_handles(list(coun))
        city_dict = dict(coun)
        city_num = []
        for city in city_name:
            city_num.append(city_dict[city])
        # print('%s : %s' %(len(city_name), city_name))
        # print('%s : %s' %(len(city_num), city_num))
        city_max = max(city_num)

        geo = Geo('评论者城市分布情况',
                  "data from maoyan",
                  title_color="#fff",
                  title_pos="center",
                  width=1200,
                  height=600,
                  background_color="#404a59"
                  )

        geo.add('',city_name,city_num,
                type='scatter',
                maptype='china',
                visual_range=[0, city_max],
                visual_text_color="#fff",
                symbol_size=15,
                is_visualmap=True
                # is_piecewise=True
                # visual_split_number=10
                )
        geo.render(self.path + r'/city_geo.html')

    # 利用评论内容，生成词云图
    def content_distribution(self,contents):
        jieba.load_userdict('userdict.txt')
        content_cut = jieba.cut(str(contents),cut_all=False)
        words = ' '.join(content_cut)
        # 设置屏蔽词
        # stopwords = STOPWORDS.copy()
        # stopwords.add('电影')
        stopwords = set()
        with open('stopwords.txt','r',encoding='utf-8') as f:
            rows = f.readlines()
            for row in rows:
                stopwords.add(row.replace('\n',''))
        # print(stopwords)
        #导入背景图
        bg_image = plt.imread('bgimage.jpg')
        # 设置词云参数，参数分别表示：画布宽高、背景颜色、背景图形状、字体、屏蔽词、最大词的字体大小
        wc = WordCloud(width=1200,height=800,background_color='white',mask=bg_image,
                       font_path='STKAITI.ttf',stopwords=stopwords,max_font_size=300,
                       random_state=40)
        # 分词传入云图
        wc.generate_from_text(words)
        plt.imshow(wc)
        # 不显示坐标轴
        plt.axis('off')
        plt.show()
        wc.to_file(self.path+r'/wordcloud.jpg')

    def all_distribution(self):
        # 加载评论数据
        data_dict = self.read_csv(path='default')
        # 性别饼图
        self.gender_distribution(data_dict['gender'])
        # 城市柱状图
        self.city_distribution_bar(data_dict['city'])
        # 地理坐标系
        self.city_distribution_geo(data_dict['city'])
        # 评论时间折线图
        self.time_distribution(data_dict['time'])
        # 生成评论等级和评分饼图
        self.score_distribution(data_dict['userlevel'], data_dict['score'])
        # 评论内容生成词云图
        self.content_distribution(data_dict['content'])

if __name__ == '__main__':
    da = DataAnlysis(1217141)
    # 所有动作的合集
    da.all_distribution()
    # 加载评论数据
    # data_dict = da.read_csv(path='default')
    # # 性别饼图
    # da.gender_distribution(data_dict['gender'])
    # # 城市柱状图
    # da.city_distribution_bar(data_dict['city'])
    # # 地理坐标系
    # da.city_distribution_geo(data_dict['city'])
    # # 评论时间折线图
    # da.time_distribution(data_dict['time'])
    # # 生成评论等级和评分饼图
    # da.score_distribution(data_dict['userlevel'],data_dict['score'])
    # # 评论内容生成词云图
    # da.content_distribution(data_dict['content'])


