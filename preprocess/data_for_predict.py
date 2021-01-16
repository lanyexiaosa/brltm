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

#import table of topic data
path_topic=""
data_topic=pd.read_pickle(path_topic) # columns: 'ID', 'day_time', 'topics'

#import table of ICD-9 code
path_icd=""
data_icd=pd.read_pickle(path_icd) # columns: 'ID', 'day_time', 'icd9_code'

#import table of cpt code
path_cpt=""
data_cpt=pd.read_pickle(path_cpt) # columns: 'ID', 'day_time', 'cpt_code'

#import table of med code
path_med=""
data_med=pd.read_pickle(path_med) # columns: 'ID', 'day_time', 'med_code'

# get diagnosis time for patient with depression
path_depre_time=""
time_data=pd.read_pickle(path_depre_time) # columns: 'ID', 'depre_time', 'sign'
depressed_pn=set(time_data['ID'])

print('-----------start to create three datasets!!!! \n')

def get_dataframe(back_day,block,window):
    # dataframe: ID, code, age, gender
    df=pd.DataFrame({'ID':[0],'code':[['a','b','SEP']],'age':[[0,0,0]],'gender':[[0,0,0]],'label':[[1]]})

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

        icd_times=[atime for atime in pn_icd['day_time'] if atime<pn_depre_time+timedelta(-block-back_day) and 
                       atime >= pn_depre_time+timedelta(-block-back_day-window)]
        cpt_times=[atime for atime in pn_cpt['day_time'] if atime<pn_depre_time+timedelta(-block-back_day) and 
                       atime >= pn_depre_time+timedelta(-block-back_day-window)]
        med_times=[atime for atime in pn_med['day_time'] if atime<pn_depre_time+timedelta(-block-back_day) and 
                       atime >= pn_depre_time+timedelta(-block-back_day-window)]
        topic_times=[atime for atime in pn_topic['day_time'] if atime<pn_depre_time+timedelta(-block-back_day) and 
                       atime >= pn_depre_time+timedelta(-block-back_day-window)]


        pn_alltime=list(set(icd_times+cpt_times+med_times+topic_times))

        if len(pn_alltime)==0:
            continue

        pn_alltime.sort()
        pn_code=[]
        for atime in pn_alltime:
        #atime=pn_alltime[12]

            icds=list(pn_icd[pn_icd['day_time'] == atime]['icd9_code'])
            cpts=list(pn_cpt[pn_cpt['day_time'] == atime]['cpt_code'])
            meds=list(pn_med[pn_med['day_time'] == atime]['med_code'])
            topics=np.squeeze(pn_topic[pn_topic['day_time'] == atime]['topics'])

            pn_code.extend(icds)
            pn_code.extend(cpts)
            pn_code.extend(meds)
            pn_code.extend(topics)
            pn_code.append('SEP')

        if set(pn_code)==set(['SEP']):
            continue

        pn_age=[age]*len(pn_code)
        pn_gender=[gender]*len(pn_code)

        pn_data=pd.DataFrame({'ID':[n],'code':[pn_code],'age':[pn_age],'gender':[pn_gender],'label':[[1]]})
        df=pd.concat([df,pn_data],axis=0)
        
       # get data for non-depressed patient
    for i in range(data_demo.shape[0]):
        #i=8
        n=data_demo.iloc[i,0]# patient ID
        if n in depressed_pn:# if depressed patients
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
        
        end_time=max(pn_icd['day_time']) 
        if len(pn_cpt['day_time'])>0:
            end_time=max(end_time,max(pn_cpt['day_time']))
        if len(pn_med['day_time'])>0:
            end_time=max(end_time,max(pn_med['day_time']))
        if len(pn_topic['day_time'])>0:
            end_time=max(end_time,max(pn_topic['day_time']))
        
 
        icd_times=[atime for atime in pn_icd['day_time'] if atime<end_time+timedelta(-block-back_day) and 
                       atime >= end_time+timedelta(-block-back_day-window)]
        cpt_times=[atime for atime in pn_cpt['day_time'] if atime<end_time+timedelta(-block-back_day) and 
                       atime >= end_time+timedelta(-block-back_day-window)]
        med_times=[atime for atime in pn_med['day_time'] if atime<end_time+timedelta(-block-back_day) and 
                       atime >= end_time+timedelta(-block-back_day-window)]
        topic_times=[atime for atime in pn_topic['day_time'] if atime<end_time+timedelta(-block-back_day) and 
                       atime >= end_time+timedelta(-block-back_day-window)]
        
        pn_alltimes=list(set(icd_times+cpt_times+med_times+topic_times))
        if len(pn_alltimes)==0:
            continue

        pn_alltimes.sort()
        pn_code=[]
        for atime in pn_alltimes:
        #atime=pn_alltime[12]

            icds=list(pn_icd[pn_icd['day_time'] == atime]['icd9_code'])
            cpts=list(pn_cpt[pn_cpt['day_time'] == atime]['cpt_code'])
            meds=list(pn_med[pn_med['day_time'] == atime]['med_code'])
            topics=np.squeeze(pn_topic[pn_topic['day_time'] == atime]['topics'])

            pn_code.extend(icds)
            pn_code.extend(cpts)
            pn_code.extend(meds)
            pn_code.extend(topics)
            pn_code.append('SEP')

        if set(pn_code)==set(['SEP']):
            continue

        pn_age=[age]*len(pn_code)
        pn_gender=[gender]*len(pn_code)

        pn_data=pd.DataFrame({'ID':[n],'code':[pn_code],'age':[pn_age],'gender':[pn_gender],'label':[[0]]})
        df=pd.concat([df,pn_data],axis=0)     

    df=df.reset_index(drop=True)
    df=df.drop(df.index[0])
    df=df.reset_index(drop=True)
    df.to_pickle('all_data_'+str(block)+'.pkl')
    print('dataframe created!!!!!\n')
    

get_dataframe(15,0,180)#two before
get_dataframe(15,90,180)#three months before
get_dataframe(15,180,180)#six months before
get_dataframe(15,365,180)#one year before


print('all data created!!! \n')
