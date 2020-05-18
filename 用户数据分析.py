# -*- coding: utf-8 -*-
"""
Created on Sat May 16 07:23:42 2020

@author: lenovo
"""
'''
本次数据分析基于阿里云天池数据集(用户行为数据集)，使用转化漏斗，对常见电商分析指标，
包括转化率，PV，UV，复购率等进行分析，分析过程中使用Python进行数据的清洗，
清洗后的数据导入MySQL数据库，运用MySQL进行数据提取，使用Excel进行数据可视化。
'''

'''----------------------一、数据清洗----------------------------'''
#数据处理包
import pandas as pd
import numpy as np

#数据可视化
import matplotlib.pyplot as plt  
import seaborn as sns
import pandas as pd
import pyecharts as pec
from pyecharts.charts import Bar,Pie
%matplotlib inline
#时间处理包
import datetime
import time

#字体设置
plt.rcParams['font.sans-serif']=['SimHei']
#字体设置
plt.rcParams['font.sans-serif']=['SimHei']


#导入原始数据
data=pd.read_csv(r'./UserBehavior.csv',encoding='utf-8',header=None,index_col=None)

#更新列名
columns=['User_Id','Item_Id','Category_Id','Behavior_type','Timestamp']
data.columns=columns

#查看数据的整体情况
data.info()
data.index #查看样本量
des=data.describe()  #对数据进行描述性统计#
################查询缺失值情况####################################
data.isnull().sum()
#时间戳列有1个缺失值，查看缺失值列
data[data.iloc[:,4].isnull()]
#3835330行数据缺失
#时间戳缺失值列，用户行为为'P'，这个数据也是异常。查看数据集中用户行为种类
data.iloc[:,3].unique()

#用户行为每个种类有多少数据
data.iloc[:,3].value_counts()

#缺失值只有1列，直接删除。并重置索引
data.dropna(axis=0,inplace=True)
data.reset_index(drop=True,inplace=True)

#时间戳列转换为日期、时间数据。并把日期和时间分为两列
#直接转时间格式失效，需要借助lambda
data.loc[:,'Timestamp']=data['Timestamp'].apply(lambda x:time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(x)))
data.loc[:,'Date']=data['Timestamp'].apply(lambda x:x.split(' ')[0])  #日期列
data.loc[:,'Time']=data['Timestamp'].apply(lambda x:x.split(' ')[1])  #时间列
#将数据转换成时间格式
data['Date']=pd.to_datetime(data['Date'])  #将Date列，由str转换为时间格式
data['Time']=pd.to_datetime(data['Time'])  #将Date列，由str转换为时间格式

#提取周，小时
data['hour']=data['Time'].dt.hour   #小时列
#把时间戳列删除
data=data.drop(columns='Timestamp',axis=1)

########################异常值处理##########################
#原始数据日期区间为2017-11-25到2017-12-03，这个时间区间外认为是异常数据。查看一下具体情况
data[data['Date']<'2017-11-25'].shape
data[data['Date']<'2017-11-25']['Date'].value_counts()
data[data['Date']>'2017-12-03'].shape
data[data['Date']>'2017-12-03']['Date'].value_counts()
data['Date'].head()
#时间区间外的日期数据剔除
data=data[(data['Date']>='2017-11-25')&(data['Date']<='2017-12-03')]

###################重复数据处理##############################
#查看重复数据
data[data.duplicated()]
#删除重复数据
data.drop_duplicates(inplace=True)
#充值索引
data.reset_index(drop=True,inplace=True)

userlogin=data[['User_Id','dates']]
#数据清洗完成，导出到本地
data.to_excel(r'./UserBehavio_Done.xlsx',sheet_name='data1',startcol=0,index=False)
data.to_csv(r'E:./userlogin.csv',index=False)



'''-----------------二、数据可视化---------------------------'''
'''-----------------(一)总体运营分析-------------------------'''
#(1)日均浏览量
dates=['2017-11-25','2017-11-26','2017-11-27','2017-11-28','2017-11-29','2017-11-30','2017-12-01','2017-12-02','2017-12-03']
d_pv=[98460,100612,91666,92981,95734,99507,102643,129577,128827]

# 绘图
x=dates
y=d_pv
plt.bar(x=x, height=y, label='日均访问量', color='steelblue', alpha=0.8)
# 设置标题
plt.title("商品的日均访问量")
# 为两条坐标轴设置名称
plt.xlabel("日期")
plt.ylabel("访问数量")
# 显示图例
plt.legend()
# 画折线图
plt.plot(x, y, "r", marker='.', ms=10, label="日均访问量")
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.savefig("a.jpg")
plt.show()

#(2)日均访客数
dates=['2017-11-25','2017-11-26','2017-11-27','2017-11-28','2017-11-29','2017-11-30','2017-12-01','2017-12-02','2017-12-03']
d_pv=[7099,7270,7155,7127,7255,7339,7403,9717,9744]
#折线柱状混合图
x=dates
y=d_pv
plt.bar(x=x, height=y, label='日均用户数', color='steelblue', alpha=0.8)
# 设置标题
plt.title("商品的日均用户数")
# 为两条坐标轴设置名称
plt.xlabel("日期")
plt.ylabel("用户数")
# 显示图例
plt.legend()
# 画折线图
plt.plot(x, y, "r", marker='.', ms=10, label="用户参与")
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.savefig("a.jpg")
plt.show()




#（3）日转化率=支付客户数/访问客户数
count_type1 = count_type.unstack()
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
count_type1.plot(kind='bar')
plt.xlabel('任务类型')
plt.ylabel('任务量')
plt.title('A,B两公司不同任务类型下的任务量')
plt.show()






#PV和UV的分析
data.groupby(['Date'])['User_Id'].count().plot()
data.groupby(['Date','User_Id']).count().reset_index().groupby('Date')['User_Id'].count().plot()


#(4)用户不同行为的时间活跃度
plt.figure(figsize=(8,5))
plt.plot(data.groupby(['Behavior_type'])['hour'].value_counts()['pv'].sort_index())
plt.plot(data.groupby(['Behavior_type'])['hour'].value_counts()['cart'].sort_index(),label = 'cart')
plt.plot(data.groupby(['Behavior_type'])['hour'].value_counts()['fav'].sort_index(),label = 'fav')
plt.plot(data.groupby(['Behavior_type'])['hour'].value_counts()['buy'].sort_index(),label = 'buy')
plt.legend()
plt.title('不同时间段的用户活跃度')
plt.show()
#可以看出除了pv比较高，其它的行为都相差不大，用户的转化不高，我们接下来看看转化率



'''-----------------------(二)时间序列分析--------------------------'''
##(1)活跃时间段：绘图
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 5))
data.groupby('hour')['hour'].count().plot()
plt.xlabel('时间')
plt.ylabel('点击量')
plt.title('不同时间段的用户活跃度')
plt.show()

'''--------------------（四）漏斗图--------------------------------------'''
# 从pyecharts包中导出创建漏斗图的函数
import pandas as pd
from pyecharts as pec

# 1.导入创建漏斗图所需要的数据
#从浏览到购买的各环节转化率
df = pd.read_csv('E:/实习/userbehavior/漏斗数据.csv', encoding='utf-8',header=None,index_col=None)#列标题导入出错时处理办法
columns=['环节','数量','转化率']
df.columns=columns
attr1 = df['环节']
values1 = df['转化率']
print(attr1)
print(values1)
funnel1 = pec.Funnel('漏斗图')
funnel1.add(name='环节',  # 指定图例名称
            attr=attr1,  # 指定属性名称
            value=values1,  # 指定属性所对应的值
            is_label_show=True,  # 确认显示标签
            label_formatter='{c}'+'%',  # 指定标签显示的方式
            legend_top='bottom',    # 指定图例位置，为避免遮盖选择右下展示
            # pyecharts包的文档中指出，当label_formatter='{d}'时,标签以百分比的形式显示.
            # 但我这样做的时候,发现显示的百分比与原始数据对应不上,只好用上面那种显示形式
            label_pos='outside',  # 指定标签的位置,inside,outside
            legend_orient='vertical',  # 指定图例显示的方向
            legend_pos='right')  # 指定图例的位置

funnel1.render(r'./funnel1.html') 

##2.独立访客转化漏斗
attr3 = ['pv','cart','fav','buy']
values3 = [100.00,75.40,68.84,40.00]
print(attr3)
print(values3)
funnel3 = pec.Funnel('独立访客转化漏斗图')
funnel3.add(name='环节',  # 指定图例名称
            attr=attr3,  # 指定属性名称
            value=values3,  # 指定属性所对应的值
            is_label_show=True,  # 确认显示标签
            label_formatter='{c}'+'%',  # 指定标签显示的方式
            legend_top='bottom',    # 指定图例位置，为避免遮盖选择右下展示
            # pyecharts包的文档中指出，当label_formatter='{d}'时,标签以百分比的形式显示.
            # 但我这样做的时候,发现显示的百分比与原始数据对应不上,只好用上面那种显示形式
            label_pos='outside',  # 指定标签的位置,inside,outside
            legend_orient='vertical',  # 指定图例显示的方向
            legend_pos='right')  # 指定图例的位置

funnel3.render(r'./funnel3.html') 


#3.加购到购买的转化率
attr2 = ['cart','fav','buy']
values2 = [100,50.71,36.84]
print(attr2)
print(values2)
funnel2 = pec.Funnel('漏斗图')
funnel2.add(name='环节',  # 指定图例名称
            attr=attr2,  # 指定属性名称
            value=values2,  # 指定属性所对应的值
            is_label_show=True,  # 确认显示标签
            label_formatter='{c}'+'%',  # 指定标签显示的方式
            legend_top='bottom',    # 指定图例位置，为避免遮盖选择右下展示
            # pyecharts包的文档中指出，当label_formatter='{d}'时,标签以百分比的形式显示.
            # 但我这样做的时候,发现显示的百分比与原始数据对应不上,只好用上面那种显示形式
            label_pos='outside',  # 指定标签的位置,inside,outside
            legend_orient='vertical',  # 指定图例显示的方向
            legend_pos='right')  # 指定图例的位置

funnel2.render(r'./funnel2.html') 

'''-----------------(四)用户行为分析--------------------------------'''
##1.复购情况
df2 = pd.read_csv('./用户复购情况.csv', encoding='GB2312')
df2.columns

x=df2['购买次数']
y=df2['用户数']
# 绘图
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
plt.bar(x=x, height=y, label='用户数', color='steelblue', alpha=0.8)
plt.xlabel('购买次数')
plt.ylabel('用户数')
plt.title('用户复购情况')
#折线图
plt.plot(x, y, "r", marker='.', ms=10, label="用户数")
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.savefig("b.jpg")
plt.show()


'''-----------------(五)商品销售分析--------------------------------'''
'''------------------柱状图+折线图----------------------------------'''
df3 = pd.read_csv(r'./商品销售分布表.csv', encoding='GB2312')
df3.columns

x=df3['销量']
y=df3['用户数']
# 绘图
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
plt.bar(x=x, height=y, label='用户数', color='steelblue')
plt.xlabel('销量')
plt.ylabel('用户数')
plt.title('商品销售分析')
#折线图
plt.plot(x, y, "r", marker='.', ms=10, label="用户数")
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.savefig("c.jpg")
plt.show()

'''-------------------------2.绘制玫瑰图-------------------------------'''
#销量top20
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyecharts import options as opts
from pyecharts.charts import Pie
#设置字体，可以在图上显示中文
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']

#1.销售量玫瑰图
# 创建数据框
df4=pd.read_csv(r'./商品销售top20.csv', encoding='GB2312')
df4.columns 
# 降序排序
df4.sort_values(by='销量', ascending=False, inplace=True)
# 提取数据
v = df4['商品'].values.tolist()
d = df4['销量'].values.tolist()
color_series = ['#FAE927','#E9E416','#C9DA36','#9ECB3C','#6DBC49',
                '#37B44E','#3DBA78','#14ADCF','#209AC9','#1E91CA',
                '#2C6BA0','#2B55A1','#2D3D8E','#44388E','#6A368B',
                '#7D3990','#A63F98','#C31C88','#D52178','#D5225B']
# 实例化Pie类
pie1 = Pie(init_opts=opts.InitOpts(width='750px', height='400px'))
# 设置颜色
pie1.set_colors(color_series)
# 添加数据，设置饼图的半径，是否展示成南丁格尔图
pie1.add("", [list(z) for z in zip(v, d)],
        radius=["30%", "135%"],
        center=["50%", "65%"],
        rosetype="area"
        )
# 设置全局配置项
pie1.set_global_opts(title_opts=opts.TitleOpts(title='商品销售top20图'),
                     legend_opts=opts.LegendOpts(is_show=False),
                     toolbox_opts=opts.ToolboxOpts())
# 设置系列配置项
pie1.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="inside", font_size=12,
                                               formatter="{b}:{c}次", font_style="italic",
                                               font_weight="bold", font_family="Microsoft YaHei"
                                               ),
                     )
# 生成html文档
pie1.render(r'./商品销售top20图.html')


##2.浏览top20
df5=pd.read_csv(r'./商品浏览量top20.csv', encoding='GB2312')
df5.columns 
# 降序排序
df5.sort_values(by='浏览量', ascending=False, inplace=True)
# 提取数据
v = df5['商品'].values.tolist()
d = df5['浏览量'].values.tolist()
color_series = ['#FAE927','#E9E416','#C9DA36','#9ECB3C','#6DBC49',
                '#37B44E','#3DBA78','#14ADCF','#209AC9','#1E91CA',
                '#2C6BA0','#2B55A1','#2D3D8E','#44388E','#6A368B',
                '#7D3990','#A63F98','#C31C88','#D52178','#D5225B']
# 实例化Pie类
pie1 = Pie(init_opts=opts.InitOpts(width='750px', height='400px'))
# 设置颜色
pie1.set_colors(color_series)
# 添加数据，设置饼图的半径，是否展示成南丁格尔图
pie1.add("", [list(z) for z in zip(v, d)],
        radius=["30%", "135%"],
        center=["50%", "65%"],
        rosetype="area"
        )
# 设置全局配置项
pie1.set_global_opts(title_opts=opts.TitleOpts(title='商品浏览量top20图'),
                     legend_opts=opts.LegendOpts(is_show=False),
                     toolbox_opts=opts.ToolboxOpts())
# 设置系列配置项
pie1.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="inside", font_size=12,
                                               formatter="{b}:{c}次", font_style="italic",
                                               font_weight="bold", font_family="Microsoft YaHei"
                                               ),
                     )
# 生成html文档
pie1.render(r'./商品浏览量top20图.html')

##3.加购top20
df6=pd.read_csv(r'./商品加购量top20.csv', encoding='GB2312')
df6.columns 
# 降序排序
df6.sort_values(by='加购量', ascending=False, inplace=True)
# 提取数据
v = df6['商品'].values.tolist()
d = df6['加购量'].values.tolist()
color_series = ['#FAE927','#E9E416','#C9DA36','#9ECB3C','#6DBC49',
                '#37B44E','#3DBA78','#14ADCF','#209AC9','#1E91CA',
                '#2C6BA0','#2B55A1','#2D3D8E','#44388E','#6A368B',
                '#7D3990','#A63F98','#C31C88','#D52178','#D5225B']
# 实例化Pie类
pie1 = Pie(init_opts=opts.InitOpts(width='750px', height='400px'))
# 设置颜色
pie1.set_colors(color_series)
# 添加数据，设置饼图的半径，是否展示成南丁格尔图
pie1.add("", [list(z) for z in zip(v, d)],
        radius=["30%", "135%"],
        center=["50%", "65%"],
        rosetype="area"
        )
# 设置全局配置项
pie1.set_global_opts(title_opts=opts.TitleOpts(title='商品加购量top20图'),
                     legend_opts=opts.LegendOpts(is_show=False),
                     toolbox_opts=opts.ToolboxOpts())
# 设置系列配置项
pie1.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="inside", font_size=12,
                                               formatter="{b}:{c}次", font_style="italic",
                                               font_weight="bold", font_family="Microsoft YaHei"
                                               ),
                     )
# 生成html文档
pie1.render(r'./商品加购量top20图.html')


##4.收藏top20
df6=pd.read_csv(r'./商品收藏量top20.csv', encoding='GB2312')
df6.columns 
# 降序排序
df6.sort_values(by='收藏量', ascending=False, inplace=True)
# 提取数据
v = df6['商品'].values.tolist()
d = df6['收藏量'].values.tolist()
color_series = ['#FAE927','#E9E416','#C9DA36','#9ECB3C','#6DBC49',
                '#37B44E','#3DBA78','#14ADCF','#209AC9','#1E91CA',
                '#2C6BA0','#2B55A1','#2D3D8E','#44388E','#6A368B',
                '#7D3990','#A63F98','#C31C88','#D52178','#D5225B']
# 实例化Pie类
pie1 = Pie(init_opts=opts.InitOpts(width='750px', height='400px'))
# 设置颜色
pie1.set_colors(color_series)
# 添加数据，设置饼图的半径，是否展示成南丁格尔图
pie1.add("", [list(z) for z in zip(v, d)],
        radius=["30%", "135%"],
        center=["50%", "65%"],
        rosetype="area"
        )
# 设置全局配置项
pie1.set_global_opts(title_opts=opts.TitleOpts(title='商品收藏量top20图'),
                     legend_opts=opts.LegendOpts(is_show=False),
                     toolbox_opts=opts.ToolboxOpts())
# 设置系列配置项
pie1.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="inside", font_size=12,
                                               formatter="{b}:{c}次", font_style="italic",
                                               font_weight="bold", font_family="Microsoft YaHei"
                                               ),
                     )
# 生成html文档
pie1.render(r'./商品收藏量top20图.html')




