import pandas as pd
import os
import re
from time import strptime
from time import process_time
from datetime import datetime

def timeParser(string):
    t = ''
    if re.match("上午",string):
        t = string[2:7] + ' ' + 'AM'
    else:
        t = string[2:7] + ' ' + 'PM'
    return t
def datetimetotimestamp(date,time):
    datetime_string = date+' '+timeParser(time)
    datetime_format = '%Y-%m-%d %I:%M %p'
    datetime_object = datetime.strptime(datetime_string, datetime_format)
    return datetime_object

def actionMsg(now_date,line):
    t, action = line.rstrip("\n").split("\t",1)
    member = ''
    msg = ''
    # ooo邀請xxx加入群組
    if re.match("(.*)邀請(.*)(加入|加入群組)$",action):
        member, msg = action.split("邀請",1)
        msg = '邀請' + msg
    # xxx加入群組
    elif re.match("(.*)加入群組$",action):
        member, msg = action.split("加入",1)
        msg = '加入' + msg
    # xxx已退出群組
    elif re.match("(.*)已退出群組$",action):
        member, msg = action.split("已退出",1)
        msg = '已退出' + msg
    # ooo已讓xxx退出群組
    elif re.match("(.*)已讓(.*)退出群組$", line):
        member, msg = action.split("已讓",1)
        msg = '已讓' + msg
    # ooo已收回訊息
    elif re.match("(.*)已收回訊息$", line):
        member, msg = action.split("已收回",1)
        msg = '已收回' + msg
    return {'time' : datetimetotimestamp(now_date,t), 'member': member, 'msg': msg}

def findLastDate(txt_path):
    f = open(txt_path, "r",encoding="utf-8")
    li = []
    for index,line in enumerate(f.readlines()):   
        # 略過前 3 行
        if index < 3:
            continue  
        # 紀錄日期指標
        if re.match("^\d{4}/\d{2}/\d{2}（(一|二|三|四|五|六|日)）$", line):
            li.append({
                'index': index,
                'date': line.rstrip("\n")[0:10].replace('/','-')
            })
    
    csv_path = txt_path.replace('.txt','.csv')        
    if os.path.isfile(csv_path) == True:
        df = pd.read_csv(csv_path,encoding='utf-8') 
        now_date = df.iloc[-1:].time.astype(str).str[0:10].to_string(index=False).strip()
        last_date = list(filter(lambda l: l['date'] == now_date, li))[0]
    else:
        df = pd.DataFrame(columns=['time','member','msg'])
        last_date = li[0]
    
    return last_date

def msg_txt_to_csv(txt_path):
    print('-----\nhandle msg from:\t'+txt_path)

    # 檢查是否已存在 csv 檔案, 有的話讀入
    csv_path = txt_path.replace('.txt','.csv')
    if os.path.isfile(csv_path) == True:
        df = pd.read_csv(csv_path,encoding='utf-8') 
        now_date = df.iloc[-1:].time.astype(str).str[0:10].to_string(index=False).strip()
    else:
        df = pd.DataFrame(columns=['time','member','msg'])
        now_date = '1970-01-01' # init date
    f = open(txt_path, "r", encoding="utf-8")

    # 剔除 dataframe 中最後一天的對話紀錄, 再從 txt 重新讀入
    last_date = findLastDate(txt_path) # csv_last_date_line_index
    df = df[~df.time.str.contains(last_date['date'],na=False)]
    rows = []
    for index,line in enumerate(f.readlines()[last_date['index']:]):   
        # 紀錄日期指標
        if re.match("^\d{4}/\d{2}/\d{2}（(一|二|三|四|五|六|日)）$", line):
            new_date = line.rstrip("\n")[0:10].replace('/','-')
            if strptime(now_date, "%Y-%m-%d") < strptime(new_date, "%Y-%m-%d"):
                now_date = new_date                
            else:
                continue
        # 處理訊息
        else:
            # 處理動作
            if re.match("^(上午|下午)\d{2}:\d{2}\t(.*)(加入|加入群組|退出群組|收回訊息)$", line):
                rows.append(actionMsg(now_date,line))
            # 處理一般對話訊息
            elif re.match("^(上午|下午)\d{2}:\d{2}\t(.*)\t(.*)", line):
                time, member, msg = line.rstrip("\n").split("\t",2)
                rows.append({
                    'time' : datetimetotimestamp(now_date,time),
                    'member': member,
                    'msg': msg
                })
            # 處理一般對話訊息包含多行的情況
            else:
                if len(rows) > 0:
                    rows[-1]['msg'] = rows[-1]['msg'].strip('"') + '\n'+ line.strip('\n"')
    f.close()
    df1 = pd.DataFrame(rows, columns=['time','member','msg'])
    df = pd.concat([df, df1], ignore_index=True)
    df.to_csv(csv_path,encoding="utf_8_sig",index=False)   
    return df
    
# init
dir_path = '/tmp/data/line_chat'
for filename in os.listdir(dir_path):
    if filename.endswith('.txt'):
        tStart = process_time()
        msg_txt_to_csv(dir_path+'/'+filename)
        tEnd = process_time() 
        print('generate:\t\t'+dir_path+'/'+filename.replace('.txt','.csv')+'\ncast:\t\t\t'+str(tEnd - tStart)+'sec')