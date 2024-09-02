import requests
import re
from lxml import etree
from fake_useragent import UserAgent
import csv
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog

def get(url, headers, cookies):
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.text
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return None


def get_title(res_text):
    res_text = etree.HTML(res_text)
    title = res_text.xpath("/html/body/div[3]/div/div/div[1]/h1/text()")
    if title:
        return title[0].strip()
    else:
        return "标题缺失"

# 获取总价
def get_price(res_text):
    res_text = etree.HTML(res_text)
    price = res_text.xpath("/html/body/div[5]/div[2]/div[3]/div/span[1]/text()")
    return price[0]


# 获取单价
def get_av_price(res_text):
    res_text = etree.HTML(res_text)
    av_price = res_text.xpath("/html/body/div[5]/div[2]/div[3]/div/div[1]/div[1]/span/text()")
    return av_price[0]


# 获取小区名称
def get_plname(res_text):
    res_text = etree.HTML(res_text)
    plname = res_text.xpath("/html/body/div[5]/div[2]/div[5]/div[1]/a[1]/text()")
    return plname[0]


# 获取地段
def get_place(res_text):
    res_text = etree.HTML(res_text)
    place = res_text.xpath("/html/body/div[5]/div[2]/div[5]/div[2]/span[2]/a/text()")
    return place


# 获取基本属性
def get_jbsx(res_text):
    res_text = etree.HTML(res_text)
    # 获取房屋户型\所在楼层\建筑面积\户型结构\套内面积\建筑类型\房屋朝向\建筑结构\装修情况\梯户比例\配备电梯
    house_jbsx = res_text.xpath("//*[@id='introduction']/div/div/div[1]/div[2]/ul/li/text()")
    return house_jbsx


# 获取交易属性
def get_jysx(res_text):
    res_text = etree.HTML(res_text)
    # 获取挂牌时间/交易权属/上次交易/房屋用途/房屋年限/产权所属/抵押信息/房本备件
    house_jysx = res_text.xpath("//*[@id='introduction']/div/div/div[2]/div[2]/ul/li/span[2]/text()")
    # 无抵押要预处理，去除首尾空格
    house_jysx[6] = house_jysx[6].strip()
    return house_jysx


def timeToYear(dt):
    return datetime.datetime.strptime(dt, '%Y-%m-%d').date().strftime('%Y')

cookies = {
    "your_cookie_name": "lianjia_ssid=2b06db71-0883-45c7-a0ad-78212571c592; lianjia_uuid=3e7913df-5136-4d09-ab73-18e1659405e9; select_city=310000; crosSdkDT2019DeviceId=wxhpbc-bz9e4r-n8kj1figxpmwj1u-oj4r5hjrw; login_ucid=2000000441102514; lianjia_token=2.0013426d3b4383b06502ef440a7629b8fa; lianjia_token_secure=2.0013426d3b4383b06502ef440a7629b8fa; security_ticket=sxhfs+sAma0WRDUM/1/ezuMskL5c7dGJJUe59zYHeXBUhXrioN1Ki9wbFaLA6qwAIpej6vzSINGcI9RWfqWqH3U2B/uKoqUlzXlnBYlW72T/ZFmJh8D195Xu75hQ7CgbcVpNxcFNChxXaeTnQ/1X9PkKbC2lSwlPvjJ3eMPqfzQ=; ftkrc_=12b1a560-8409-439a-8444-93da0efa3d4c; lfrc_=18ba8879-83da-4e04-a6ee-d06fdc61ae79; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1724754335; HMACCOUNT=81F6F99E0883E032; sajssdk_2015_cross_new_user=1; _jzqa=1.4340822170864491000.1724754335.1724754335.1724754335.1; _jzqc=1; _jzqx=1.1724754335.1724754335.1.jzqsr=clogin%2Elianjia%2Ecom|jzqct=/.-; _jzqckmp=1; _ga=GA1.2.883139606.1724754347; _gid=GA1.2.1141134892.1724754347; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22191935e96ab25a5-0c86ebd3093991-26001e51-2073600-191935e96ac203c%22%2C%22%24device_id%22%3A%22191935e96ab25a5-0c86ebd3093991-26001e51-2073600-191935e96ac203c%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _ga_LRLL77SF11=GS1.2.1724754347.1.1.1724754742.0.0.0; _ga_GVYN2J1PCG=GS1.2.1724754347.1.1.1724754742.0.0.0; hip=NcofRL1Ssc78Ja1XEHfoGCNA9xBfKEQnvcnZnSEl-YY5ezIxjkneW0r7p5kp7LqJpTYFPHCzBwRUUoCdpUhYPaqmB92aMQPYtZpEyEKyGrrpklqaProv005feek1WtreWC7UPck0mG5g5C6WleyiV53AJbdZTjDbcBrm6kX5ZfkyHMMAGUJv5LpGEA%3D%3D; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1724756306; _jzqb=1.3.10.1724754335.1; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}


def crawling(file_name):
    csv_title = ['标题', '总价', '单价', '小区名称', '地段', '房屋户型', '所在楼层', '建筑面积', '户型结构', '套内面积',
                 '建筑类型',
                 '房屋朝向', '建筑结构', '装修情况', '梯户比例', '配备电梯', '挂牌时间', '交易权属', '上次交易',
                 '房屋用途', '房屋年限',
                 '产权所属', '抵押信息', '房本备件', '房源核验码']
    with open(file_name, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(csv_title)

    url = 'https://sh.lianjia.com/ershoufang/'
    res = get(url, headers, cookies)
    if res is None:
        return
    res_text = etree.HTML(res)
    s = res_text.xpath("/html/body/div[3]/div/div[1]/dl[2]/dd/div[1]/div[1]/a/@href")
    for item in s:
        url = 'https://sh.lianjia.com/' + item
        for i_page in range(1, 31):
            page_url = url + f'pg{i_page}'
            res = get(page_url, headers, cookies)
            if res is None:
                continue
            print(f"正在处理页面: {page_url}")

            # 获取源码中每个二手房详情页的url
            re_f = '<a class="" href="(.*?)" target="_blank"'
            url_list = re.findall(re_f, res)
            for i_url in url_list:
                try:
                    r_url = get(i_url, headers, cookies)
                    if r_url is None:
                        continue
                    row = [
                        get_title(r_url),
                        get_price(r_url),
                        get_av_price(r_url),
                        get_plname(r_url),
                        get_place(r_url)
                    ]
                    jbsx = get_jbsx(r_url)
                    row.extend(jbsx)
                    jysx = get_jysx(r_url)
                    if len(jysx) != 9:
                        continue
                    row.extend(jysx)
                    with open(file_name, 'a', encoding='utf-8', newline='') as f:
                        csv_writer = csv.writer(f)
                        csv_writer.writerow(row)
                except Exception as e:
                    print(f"处理 {i_url} 时发生错误: {e}")
                    continue


def data_cleaning(file_name):
    house_df = pd.read_csv(file_name, encoding='utf-8')
    # 去掉没用的列
    col = house_df.columns.tolist()
    li_unuse = ['房源核验码', '房本备件', '套内面积']
    for item in li_unuse:
        col.remove(item)
    house_df = house_df[col]
    # 去除缺失值
    house_df.dropna(inplace=True)
    '''
    分割房屋户型
    '''
    split1 = ['厅', '厨', '卫']
    split_data = house_df['房屋户型'].astype('str').str.split('室', expand=True)
    # 修改分割后的字段名称
    split_data.columns = ['室', 'other']
    # 与原始数据进行合并
    house_df = house_df.join(split_data['室'].astype('int'))
    for item in split1:
        # 对指定列进行分割
        split_data = split_data['other'].astype('str').str.split(item, expand=True)
        # 修改分割后的字段名称
        split_data.columns = [item, 'other']
        # 与原始数据进行合并
        house_df = house_df.join(split_data[item].astype('int'))
    '''
    分割所在楼层
    '''
    split_data = house_df['所在楼层'].astype('str').str.split(' ', expand=True)
    # 修改分割后的字段名称
    split_data.columns = ['楼层高低', '楼层数']
    # 与原始数据进行合并
    house_df = house_df.join(split_data)
    del house_df['所在楼层']
    '''
    去除单位
    '''
    house_df['建筑面积'] = house_df['建筑面积'].apply(lambda x: float(x.replace('㎡', ''))).astype(float)
    '''
    处理地段
    '''
    house_df['地段'] = house_df['地段'].astype('str').str.split("'", expand=True)[1]
    '''
    加一行Id
    '''
    house_df.insert(loc=0, column='houseId', value=range(1, len(house_df) + 1))
    house_df['上次交易'].replace('暂无数据', '1995/6/30', inplace=True)
    house_df['上次交易'] = pd.to_datetime(house_df['上次交易'])
    house_df['挂牌时间'] = pd.to_datetime(house_df['挂牌时间'])
    house_df.to_csv(file_name, index=False)


def visualizing(file_name):
    # 指定画布风格
    plt.style.use("fivethirtyeight")
    # 设置中文字体
    sns.set_style({'font.sans-serif': ['simhei', 'Arial']})
    house_df = pd.read_csv(file_name, encoding='utf-8')
    # # 按区域分析数量和价格
    df_house_mean = house_df.groupby('地段')['单价'].mean().sort_values(ascending=False).to_frame().reset_index()
    f, [ax1, ax3] = plt.subplots(2, 1, figsize=(12, 18))
    sns.barplot(x='地段', y='单价', palette='Blues_d', data=df_house_mean, ax=ax1)
    ax1.set_title('上海各区二手房每平米单价对比')
    ax1.set_xlabel('区域')
    ax1.set_ylabel('每平米单价')
    sns.boxplot(x='地段', y='总价', data=house_df, ax=ax3)
    ax3.set_title('上海各区二手房房屋总价')
    ax3.set_xlabel('区域')
    ax3.set_ylabel('房屋总价')
    plt.savefig('images/img1')
    plt.show()

    f, [ax1, ax2] = plt.subplots(1, 2, figsize=(16, 6))
    # # 房屋面积
    sns.distplot(house_df['建筑面积'], ax=ax1, color='r')
    sns.kdeplot(house_df['建筑面积'], shade=True, ax=ax1)
    ax1.set_xlabel('面积')
    # # 房屋面积和价格的关系
    sns.regplot(x='建筑面积', y='总价', data=house_df, ax=ax2)
    ax2.set_xlabel('面积')
    ax2.set_ylabel('总价')
    plt.savefig('images/img2')
    plt.show()

    f, ax1 = plt.subplots(figsize=(12, 12))
    sns.countplot(y='房屋户型', data=house_df, ax=ax1)
    ax1.set_title('房屋户型', fontsize=15)
    ax1.set_xlabel('数量')
    ax1.set_ylabel('户型')
    plt.savefig('images/img3')
    plt.show()

    f, [ax1, ax2, ax3] = plt.subplots(1, 3, figsize=(20, 5))
    sns.countplot(house_df['装修情况'], ax=ax1)
    sns.barplot(x='装修情况', y='总价', data=house_df, ax=ax2)
    sns.boxplot(x='装修情况', y='总价', data=house_df, ax=ax3)
    plt.savefig('images/img4')
    plt.show()

    # 按照楼层高低、建筑类型、配备电梯绘制饼图
    f, [ax1, ax2, ax3] = plt.subplots(1, 3, figsize=(20, 5))
    lc = house_df['楼层高低'].str[0].value_counts(normalize=True)
    lx = house_df['建筑类型'].value_counts(normalize=True)
    dt = house_df['配备电梯'].value_counts(normalize=True)
    ax1.pie(x=lc, labels=lc.index + "楼层", autopct="%.2f%%", pctdistance=0.7, labeldistance=1.1, radius=1)
    ax1.set_title('楼层高低')
    ax2.pie(x=lx, labels=lx.index, autopct="%.2f%%", pctdistance=1.2, labeldistance=1.4, radius=1)
    ax2.set_title('建筑类型')
    ax3.pie(x=dt, labels=dt.index, autopct="%.2f%%", pctdistance=0.7, labeldistance=1.1, radius=1)
    ax3.set_title('配备电梯')
    plt.savefig('images/img5')
    plt.show()

    house_df['地段'] = LabelEncoder().fit_transform(house_df['地段'].values)
    corr = house_df.corr()
    f, ax1 = plt.subplots(figsize=(12, 12))
    sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns,
                linewidths=0.2, cmap="YlGnBu", annot=True, ax=ax1)
    ax1.set_title('热点图')
    plt.savefig('images/img6')
    plt.show()

    f, ax1 = plt.subplots(figsize=(12, 12))
    house_df.corr()['总价'].sort_values(ascending=False).plot(kind='bar', ax=ax1, fontsize=24)
    plt.xticks(rotation=360)
    ax1.set_title('各特征与总价的相关程度')
    plt.savefig('images/img7')
    plt.show()

    f, ax1 = plt.subplots(figsize=(12, 12))
    y = house_df['上次交易'].apply(timeToYear).value_counts().sort_index(ascending=True)
    ax1.set_title('房屋上次交易时间变化趋势')
    plt.xlabel("交易时间")
    plt.ylabel("交易数量")
    plt.plot(y)
    plt.grid(color='r', linestyle='--', linewidth=0.5)
    plt.savefig('images/img8')
    plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename()
    crawling(file)
    data_cleaning(file)
    visualizing(file)
