import pandas as pd
import matplotlib.pyplot as plt
import os
import math
from time import process_time

# plot 參數設定
# matplotlib.pyplot 中文字型參考：https://medium.com/marketingdatascience/%E8%A7%A3%E6%B1%BApython-3-matplotlib%E8%88%87seaborn%E8%A6%96%E8%A6%BA%E5%8C%96%E5%A5%97%E4%BB%B6%E4%B8%AD%E6%96%87%E9%A1%AF%E7%A4%BA%E5%95%8F%E9%A1%8C-f7b3773a889b
plt.rcParams.update({
    'font.family': ['Microsoft JhengHei'],
    'figure.autolayout': True,
    'axes.unicode_minus': True,
    'savefig.dpi': 100,
    'figure.dpi': 100
})

# 欄位去識別化
def deIdentify(df):
    df.dropna(inplace=True)
    members_in_df = df.member.unique().tolist()
    members = []
    for i,el in enumerate(members_in_li):
        members.append({'id':i,'member':el})
    df_members = pd.DataFrame(members)
    res = pd.merge(df_members, df, left_on='member', right_on='member').sort_values(by='time')
    return res

# 處理 msg
def plotMsgStatics(title, input_csv_path):
    print('-----\nhandle statics from:\t'+input_csv_path)

    # 讀入 csv 檔案
    df = pd.read_csv(input_csv_path, encoding='utf-8')
    #df = deIdentify(df) # 去識別化

    # 找出 dataframe 中所有月份
    months = df.time.replace(to_replace ='-\d{2}\s\d{2}:\d{2}:\d{2}$', value = '', regex = True).unique()

    # plot 初始化
    fig = plt.figure(figsize=(3*7, math.ceil(len(months)/3)*4)) # 設定 plt figure
    plt.title(os.path.basename(input_csv_path).replace('.csv','')+'-'+title, y=1.03, fontsize=32) # 設定 plot title
    plt.axis('off') # 關閉外圍 plot axis
    for idx,month in enumerate(months):
        df2 = df[(df.time.str.contains(month))]
        if title == '貼圖統計':
            msgs = df2[df2.msg == '[貼圖]'].groupby(['member']).size().sort_values(ascending=False)
        elif title == '照片統計':
            msgs = df2[df2.msg == '[照片]'].groupby(['member']).size().sort_values(ascending=False)
        elif title == '影片統計':
            msgs = df2[df2.msg == '[影片]'].groupby(['member']).size().sort_values(ascending=False)
        elif title == '收回統計':
            msgs = df2[df2.msg == '已收回訊息'].groupby(['member']).size().sort_values(ascending=False)
        else:
            msgs = df2.groupby(['member']).size().sort_values(ascending=False)
        df_filter_msg = pd.DataFrame({'member':msgs.index,'num':msgs.values}).sort_values(by='num', ascending=False).head(10)

        # 略過 rows length 為 0 的月份
        if df_filter_msg.shape[0] == 0:
            continue

        # 處理 subplot
        ax = fig.add_subplot(math.ceil(len(months)/3),3,idx+1)
        df_filter_msg.sort_values(by='num', ascending=False)\
            .head(10)\
            .plot(ax=ax, subplots=True, x="member", y="num", fontsize=16, legend=False, kind='barh')
        #ax.get_children()[0].set_color('r') # top 1 紅色標記

        # 移除 y 軸 label
        ax.set_ylabel('')

        # 設定 subplot title
        ax.set_title(month)
    plot_filename = input_csv_path.replace('.csv','')+'-'+title+'.png'
    plt.savefig(plot_filename) # 儲存 fig

# init
dir_path = '/tmp/data/line_chat'
titles = ['貼圖統計','照片統計','影片統計','收回統計','說話統計']
for filename in os.listdir(dir_path):
    if filename.endswith('.csv') and not filename.endswith('mentioned.csv'):
        for title in titles:
            tStart = process_time()
            plotMsgStatics(title, dir_path+'/'+filename)
            tEnd = process_time()
            print('generate:\t\t'+dir_path+'/'+filename.replace('.csv','')+'-'+title+'.png'+'\ncast:\t\t\t'+str(tEnd - tStart)+'sec')