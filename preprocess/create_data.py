#import patient data
import pandas as pd
import numpy as np
import pickle
import time
from datetime import datetime
from datetime import timedelta

# import data
path_demo=""
data_demo=pd.read_csv(path_demo,header=0) #columns:'ID', 'Age', 'gender'
#input_demo=pd.read_csv(path_demo,header=0) #columns:'ID', 'Age', 'gender'
#data_demo=pd.DataFrame(input_demo).values

#import table of topic data
path_topic=""
data_topic=pd.read_pickle(path_topic) # columns: 'ID', 'day_time', 'topics'
#data_topic=pd.DataFrame(input_topic).values

#import table of ICD-9 code
path_icd=""
data_icd=pd.read_pickle(path_icd) # columns: 'ID', 'day_time', 'icd9_code'
#input_icd=pd.read_csv(path_icd,header=0) # columns: 'ID', 'day_time', 'icd9_code' 
#data_icd=pd.DataFrame(input_icd).values

#import table of cpt code
path_cpt=""
data_cpt=pd.read_pickle(path_cpt) # columns: 'ID', 'day_time', 'cpt_code'
#input_cpt=pd.read_csv(path_cpt,header=0) # columns: 'ID', 'day_time', 'cpt_code'
#data_cpt=pd.DataFrame(input_cpt).values

#import table of med code
path_med=""
data_med=pd.read_pickle(path_med) # columns: 'ID', 'day_time', 'med_code'
#input_med=pd.read_csv(path_med,header=0) # columns: 'ID', 'day_time', 'med_code'
#data_med=pd.DataFrame(input_med).values

# get diagnosis time for patient with depression
path_depre_time=""
time_data=pd.read_pickle(path_depre_time) # columns: 'ID', 'depre_time', 'sign'
#time_data=pd.read_csv(path_depre_time,header=0) # columns: 'ID', 'depre_time', 'sign'
#depre_time=pd.DataFrame(time_data).values
depressed_pn=set(time_data['ID'])

# dataframe: ID, code, age, gender
df1=pd.DataFrame({'ID':[0],'code':[['a','b','SEP']],'age':[[0,0,0]],'gender':[[0,0,0]]})#no topic
df2=pd.DataFrame({'ID':[0],'code':[['a','b','SEP']],'age':[[0,0,0]],'gender':[[0,0,0]]})#no cpt
df3=pd.DataFrame({'ID':[0],'code':[['a','b','SEP']],'age':[[0,0,0]],'gender':[[0,0,0]]})#no topic and cpt

print('-----------start to create three datasets!!!! \n')

# get data for depressed patient
for i in range(time_data.shape[0]):
    #i=8
    n=time_data.iloc[i,0]# patient ID
    pn_depre_time=time_data.iloc[i,1]# get depression time
        
    pn_icd=data_icd[data_icd['ID'] == n]
    #pn_icd_times=[datetime.strptime(pntime,'%Y-%m-%d %H:%M:%S') for pntime in pn_icd.iloc[:,1]]

    pn_cpt=data_cpt[data_cpt['ID'] == n]
    #pn_cpt_times=[datetime.strptime(pntime.replace("'",""),'%Y-%m-%d %H:%M:%S') for pntime in pn_cpt.iloc[:,1]]

    pn_med=data_med[data_med['ID'] == n]
    #pn_med_times=[datetime.strptime(pntime.replace("'",""),'%Y-%m-%d %H:%M:%S') for pntime in pn_med.iloc[:,1]]

    pn_topic=data_topic[data_topic['ID'] == n]
    #pn_topic_times=[datetime.strptime(pntime,'%Y-%m-%d %H:%M:%S') for pntime in pn_topic.iloc[:,1]]

    pn_demo=np.squeeze(data_demo[data_demo['ID'] == n].values)
    age=pn_demo[1]
    gender=pn_demo[2]
    
    times=set(list(pn_icd['day_time'])+list(pn_cpt['day_time'])+list(pn_med['day_time'])+list(pn_topic['day_time']))
    
    pn_alltime=[]
    for atime in times:
        if atime < pn_depre_time:
            pn_alltime.append(atime)
    
    if len(pn_alltime)==0:
        continue
    
    pn_alltime.sort()
    pn_code1=[]#no topic
    pn_code2=[]#no cpt 
    pn_code3=[]#no topic and cpt
    
    for atime in pn_alltime:
    #atime=pn_alltime[12]

        icds=list(pn_icd[pn_icd['day_time'] == atime]['icd9_code'])
        cpts=list(pn_cpt[pn_cpt['day_time'] == atime]['cpt_code'])
        meds=list(pn_med[pn_med['day_time'] == atime]['med_code'])
        topics=np.squeeze(pn_topic[pn_topic['day_time'] == atime]['topics'])

        pn_code1.extend(icds)
        pn_code1.extend(cpts)
        pn_code1.extend(meds)
        pn_code1.append('SEP')
        
        pn_code2.extend(icds)
        pn_code2.extend(meds)
        pn_code2.extend(topics)
        pn_code2.append('SEP')
        
        pn_code3.extend(icds)
        pn_code3.extend(meds)
        pn_code3.append('SEP')
    
    if set(pn_code1)!=set(['SEP']):
        pn_data1=pd.DataFrame({'ID':[n],'code':[pn_code1],'age':[[age]*len(pn_code1)],'gender':[[gender]*len(pn_code1)]})
        df1=pd.concat([df1,pn_data1],axis=0)
        
    if set(pn_code2)!=set(['SEP']):
        pn_data2=pd.DataFrame({'ID':[n],'code':[pn_code2],'age':[[age]*len(pn_code2)],'gender':[[gender]*len(pn_code2)]})
        df2=pd.concat([df2,pn_data2],axis=0)
    
    if set(pn_code3)!=set(['SEP']):
        pn_data3=pd.DataFrame({'ID':[n],'code':[pn_code3],'age':[[age]*len(pn_code3)],'gender':[[gender]*len(pn_code3)]})
        df3=pd.concat([df3,pn_data3],axis=0)
    
    
# get data for non-depressed patient
for i in range(data_demo.shape[0]):
    #i=8
    n=data_demo.iloc[i,0]# patient ID
    if n in depressed_pn:
        continue
    
    age=data_demo.iloc[i,1]
    gender=data_demo.iloc[i,2]

    pn_icd=data_icd[data_icd['ID'] == n]
    #pn_icd_times=[datetime.strptime(pntime,'%Y-%m-%d %H:%M:%S') for pntime in pn_icd.iloc[:,1]]

    pn_cpt=data_cpt[data_cpt['ID'] == n]
    #pn_cpt_times=[datetime.strptime(pntime.replace("'",""),'%Y-%m-%d %H:%M:%S') for pntime in pn_cpt.iloc[:,1]]

    pn_med=data_med[data_med['ID'] == n]
    #pn_med_times=[datetime.strptime(pntime.replace("'",""),'%Y-%m-%d %H:%M:%S') for pntime in pn_med.iloc[:,1]]

    pn_topic=data_topic[data_topic['ID'] == n]
    #pn_topic_times=[datetime.strptime(pntime,'%Y-%m-%d %H:%M:%S') for pntime in pn_topic.iloc[:,1]]
    
    pn_alltimes=list(set(pn_icd['day_time'])|set(pn_cpt['day_time'])|set(pn_med['day_time'])|set(pn_topic['day_time']))
    if len(pn_alltimes)==0:
        continue
        
    pn_alltimes.sort()
    pn_code1=[]#no topic
    pn_code2=[]#no cpt 
    pn_code3=[]#no topic and cpt
    
    for atime in pn_alltimes:
    #atime=pn_alltime[12]

        icds=list(pn_icd[pn_icd['day_time'] == atime]['icd9_code'])
        cpts=list(pn_cpt[pn_cpt['day_time'] == atime]['cpt_code'])
        meds=list(pn_med[pn_med['day_time'] == atime]['med_code'])
        topics=np.squeeze(pn_topic[pn_topic['day_time'] == atime]['topics'])

        pn_code1.extend(icds)
        pn_code1.extend(cpts)
        pn_code1.extend(meds)
        pn_code1.append('SEP')
        
        pn_code2.extend(icds)
        pn_code2.extend(meds)
        pn_code2.extend(topics)
        pn_code2.append('SEP')
        
        pn_code3.extend(icds)
        pn_code3.extend(meds)
        pn_code3.append('SEP')
    
    if set(pn_code1)!=set(['SEP']):
        pn_data1=pd.DataFrame({'ID':[n],'code':[pn_code1],'age':[[age]*len(pn_code1)],'gender':[[gender]*len(pn_code1)]})
        df1=pd.concat([df1,pn_data1],axis=0)
    
    if set(pn_code2)!=set(['SEP']):
        pn_data2=pd.DataFrame({'ID':[n],'code':[pn_code2],'age':[[age]*len(pn_code2)],'gender':[[gender]*len(pn_code2)]})
        df2=pd.concat([df2,pn_data2],axis=0)
    
    if set(pn_code3)!=set(['SEP']):
        pn_data3=pd.DataFrame({'ID':[n],'code':[pn_code3],'age':[[age]*len(pn_code3)],'gender':[[gender]*len(pn_code3)]})
        df3=pd.concat([df3,pn_data3],axis=0)
    

df1=df1.reset_index(drop=True)
df1=df1.drop(df1.index[0])
df1=df1.reset_index(drop=True)
df1.to_pickle('data_no_topic.pkl')

df2=df2.reset_index(drop=True)
df2=df2.drop(df2.index[0])
df2=df2.reset_index(drop=True)
df2.to_pickle('data_no_cpt.pkl')

df3=df3.reset_index(drop=True)
df3=df3.drop(df3.index[0])
df3=df3.reset_index(drop=True)
df3.to_pickle('data_no_topic_cpt.pkl')

print('all data created!!! \n')
