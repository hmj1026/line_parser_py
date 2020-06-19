import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import re
import os
from time import process_time

# plot 參數設定
# matplotlib.pyplot 中文字型參考：https://medium.com/marketingdatascience/%E8%A7%A3%E6%B1%BApython-3-matplotlib%E8%88%87seaborn%E8%A6%96%E8%A6%BA%E5%8C%96%E5%A5%97%E4%BB%B6%E4%B8%AD%E6%96%87%E9%A1%AF%E7%A4%BA%E5%95%8F%E9%A1%8C-f7b3773a889b
plt.rcParams.update({
    'font.family': ['Microsoft JhengHei'],
    'font.sans-serif': ['Microsoft JhengHei'],
    'figure.autolayout': True,
    'axes.unicode_minus': True,
    'savefig.dpi': 100,
    'figure.dpi': 100
})

# 欄位去識別化
def deIdentify(df):
    df.dropna(inplace=True)
    members_in_df = df.member.unique().tolist()
    mentioned_in_df = df.mentioned.unique().tolist()
    members_in_li = list(set(members_in_df+mentioned_in_df))
    members = []
    for i,el in enumerate(members_in_li):
        members.append({'id':i,'member':el})
    df_members = pd.DataFrame(members)
    res = pd.merge(df_members, df, left_on='member', right_on='member').sort_values(by='time')
    res = res.drop(columns={'member'}).rename(columns={'id':'_member','mentioned':'member'})
    res = pd.merge(df_members, res, left_on='member', right_on='member').sort_values(by='time')
    res = res.drop(columns={'member'}).rename(columns={'_member':'member','id':'mentioned'})
    return res

# ooo 以@提及了 xxx 的 list
def mentionedListFromCsv(csv_path):
    print('-----\nhandle mentioned from:\t'+ csv_path)
    mentioned_csv_path = csv_path.replace('.csv','-mentioned.csv')
    if os.path.isfile(mentioned_csv_path) == True:
        df2 = pd.read_csv(mentioned_csv_path, encoding='utf-8') 
    else:
        df = pd.read_csv(csv_path, encoding='utf-8')
        members = df.member.unique().tolist()
        mentioned_list = []
        mentioned_members = []
        df_mentioned = df[df.msg.str.contains('(@.*\s)',na=False)].reset_index()
        for index, row in df_mentioned.iterrows():
            # 尋找被提及的成員
            # Python | Test if string contains element from list: https://www.geeksforgeeks.org/python-test-if-string-contains-element-from-list/
            li_mentioned = [ele for ele in list(map(lambda s:str(s)+' ',members)) if(str(ele) in row.msg)]
            li_mentioned = list(map(lambda s:s.strip(), li_mentioned))
            if len(li_mentioned) > 0:
                for li in li_mentioned:
                    mentioned_list.append({'time':row.time,'member':row.member,'mentioned':li})
            if index%1000 == 0:
                print(index)
        df2 = pd.DataFrame(mentioned_list,index=None).dropna(axis='rows')
        df2.to_csv(csv_path.replace('.csv','-mentioned.csv'),encoding="utf_8_sig",index=False)

    #df2 = deIdentify(df2) # 去識別化
    return df2

# 畫出 Social Network Analysis 圖
# Ref: http://jonathansoma.com/lede/algorithms-2017/classes/networks/networkx-graphs-from-source-target-dataframe/
def plotSNAbyMentionedList(df2,plot_title,png_output_path):
    print('handle sna plot...')
    source = 'member'
    target = 'mentioned'
    
    # 前 10% 被 mentioned 的 members
    n = round(len(df2.mentioned.unique())/10)
    obs_targets_list = df.groupby([source,target]).size().groupby(target).size().sort_values(ascending=False).head(n).index.tolist()  
    df2 = df2[df2.mentioned.isin(obs_targets_list)]
    
    # 1. Create the graph    
    if n < 16:
        figsize = 16
    else:
        figsize = n
    plt.figure(figsize=(figsize, figsize))
    
    g = nx.from_pandas_edgelist(df2, source=source, target=target) 

    # 2. Create a layout for our nodes
    layout = nx.circular_layout(g)

    # 3. Draw the parts we want    
    nx.draw_networkx_edges(g, layout, alpha=0.5, edge_color="#AAAAAA")
    targets = [node for node in g.nodes() if node in df2[target].unique()]
    size = [g.degree(node) * 50 for node in g.nodes() if node in df2[target].unique()]
    nx.draw_networkx_nodes(g, layout, nodelist=targets, node_size=size, node_color='lightblue')

    people = [node for node in g.nodes() if node in df2[source].unique()]
    nx.draw_networkx_nodes(g, layout, nodelist=people, node_size=50, node_color='#AAAAAA')

    target_dict = dict(zip(targets, targets))
    nx.draw_networkx_labels(g, layout, labels=target_dict)
    # 4. Turn off the axis because I know you don't want it
    plt.axis('off')

    plt.title(plot_title, fontsize=32)

    # 5. Tell matplotlib to show it
    plt.savefig(png_output_path)
    #plt.show()

# init 
dir_path = '/tmp/data/line_chat'
for filename in os.listdir(dir_path):
    if filename.endswith('.csv') and not filename.endswith('mentioned.csv'):
        tStart = process_time()
        df = mentionedListFromCsv(dir_path+'/'+filename)
        plot_filename = filename.replace('.csv','-SNA.png')
        plot_title = filename.replace('.csv','-前 10% 被 @ 的成員互動圖')
        plotSNAbyMentionedList(df,plot_title,dir_path+'/'+plot_filename)
        tEnd = process_time()
        print('generate:\t\t'+dir_path+'/'+plot_filename+'\ncast:\t\t\t'+str(tEnd - tStart)+'sec')