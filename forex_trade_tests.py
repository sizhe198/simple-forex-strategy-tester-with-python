# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 02:44:36 2019

@author: sizhe198
"""
import cx_Oracle                            
import talib
import numpy as np

def jincha(short,long,price):               #gloden cross singnal for moving average
    ma_s =talib.SMA(price,timeperiod=short)
    ma_l =talib.SMA(price,timeperiod=long)
    jincha=[]
    jincha.append(0)
    for i in range(1,len(price)):
        if ma_s[i] > ma_l[i] and ma_s[i-1]<=ma_l[i-1]:
            jincha.append(1)
        else:
            jincha.append(0)
    return jincha  

def sicha(short,long,price):                 #gloden cross singnal for moving average
    ma_s =talib.SMA(price,timeperiod=short)
    ma_l =talib.SMA(price,timeperiod=long)
    sicha=[]
    sicha.append(0)
    for i in range(1,len(price)):
        if ma_s[i-1] >= ma_l[i-1] and ma_s[i]<ma_l[i]:
            sicha.append(-1)
        else:
            sicha.append(0)
    return sicha
def get_time(x,y):                        #get the trading time for the singnal
    return [a for a in range(len(y)) if y[a] == x]

## define uptrend，if short term moving average above long term moving average for K period of time then the uptrend is confirmed.
def longtrend(short,long,K,price): 
    ma_s =talib.SMA(price,timeperiod=short)      
    ma_l=talib.SMA(price,timeperiod=long)
    longtrend=[]
    for i in range(len(price)-1):
        if i< K-1:
            longtrend.append(0)
        else:
            chi=0
            for j in range(K):
                if ma_s[i-j]>ma_l[i-j]:
                    chi+=1
            if chi==K:
                longtrend.append(1)
            else:
                longtrend.append(0)
    return longtrend
## define downtrend，if short term moving average below long term moving average then the downtrend is confirmed.
def shortrend(short,long,price):
    ma_s=talib.SMA(price,timeperiod=short)
    ma_l=talib.SMA(price,timeperiod=long)
    shortrend=[]
    for i in range(len(price)):
        if round(ma_s[i],5)<round(ma_l[i],5):
            shortrend.append(1)
        else:
            shortrend.append(0)
    return shortrend

#data processing. combine 5 mins data with 30 mins data which identifed with trend 
def data_proc(short_30,long_30):
    shortrends=shortrend(short_30,long_30,data_30mins)
    period_5_30=[]
    j=0
    for i in range(len(data_class)-1):
       if j <len(shortrends):
          if  data_class[i]==data_class[i+1]:
               period_5_30.append(shortrends[j])
          else:
               period_5_30.append(shortrends[j])
               j+=1
       else:
          period_5_30.append(shortrends[j])
    period_5_30.append(shortrends[j])
    return period_5_30
# computing the signals to open the position without considering when to close the position
def get_open(short_5_si,long_5_si,period_5_30,forbid_tm_st,forbid_tm_end): 
    #si=sicha(short_5_si,long_5_si,opend)
    jin=jincha(short_5_si,long_5_si,opend)   
    #jin_time=get_time(1,jin)                    
    signal_open=[]
    for i in range(len(period_5_30)):          
       if jin[i]==0:
            signal_open.append(0)
       elif jin[i]==1:
           if period_5_30[i]==1 and (int(data[i][1][0:2]) < forbid_tm_st or  int(data[i][1][0:2])>= forbid_tm_end):
             signal_open.append(-1)
           else:
             signal_open.append(0)
    open_time=get_time(-1,signal_open)
    return open_time

# computing the singal of open and close position with the consideration of max gain and loss with a trading cost of 0.0002
def get_signal(short_5_jin,long_5_jin,open_time,max_loss,max_gain):
    si=sicha(short_5_jin,long_5_jin,opend)   
    si_time=get_time(-1,si)
    all_times=[]
    y=0
    for i in range(len(open_time)):
       if  open_time[i]<=y:
           continue
       else:
           for j in range(0,len(si_time)):
             if si_time[j]>open_time[i]:     
                num=[]
                q=0
                for m in range(open_time[i],si_time[j]):    
                   if opend[open_time[i]]-high[m+1]-0.0002 > -max_loss and opend[open_time[i]]-low[m+1]-0.0002 < max_gain:
                      num.append(1)
                   else:
                      num.append(-1)
                      q=m+2
                      break
                if sum(num)==si_time[j]-open_time[i]:
                    all_times.append([open_time[i],si_time[j]])
                    y=si_time[j]
                    break
                else:
                    all_times.append([open_time[i],q])
                    y=q
                    break              
    return all_times

#compute the gain with the considration of when not to open position 

def profit_count020(all_times,max_loss,max_gain): 
    profit=[]
    for i in range(len(all_times)):
        if opend[all_times[i][0]]-high[all_times[i][1]-1]-0.0002 <=-max_loss:
            profit.append([-max_loss*680])
        elif opend[all_times[i][0]]-low[all_times[i][1]-1]-0.0002 >= max_gain:
            profit.append([max_gain*680])
        else:
            profit.append([(opend[all_times[i][0]]-opend[all_times[i][1]])*680])
    profit_sum=sum(np.array(profit))
    return profit_sum

# ETL for data 
conn=cx_Oracle.connect('name/password@localhost/XE')    
c=conn.cursor()                                           
x=c.execute('select * from FOREX_EURU') # table name                  
data=x.fetchall()
c.close()                                                 
conn.close()

high2=[]
for i in range(len(data)):
    high2.append(data[i][3])
high=np.array(high2)
del high2

low2=[]
for i in range(len(data)):
    low2.append(data[i][4])
low=np.array(low2)
del low2

opend2=[]
for i in range(len(data)):
    opend2.append(data[i][2])
opend=np.array(opend2)
del opend2

data_class=[]
for i in range(len(data)):
    if data[i][1][3:5] in ('05','10','15','20','25','00'):
        data_class.append(1)
    else:
        data_class.append(2)
data_30min=[]
data_30min.append(data[0][2])
for i in range(len(data)-1):
     if data_class[i]!=data_class[i+1]:
        data_30min.append(data[i+1][2])
data_30mins=np.array(data_30min)

# compute the profit with different parameter for the max profit
pro_test3=[]
for i in range(7,18,5):
 for j in range(22,35,6):
        period_5_30 = data_proc(i,j)
        for u in range(2,10,2):
                for p in range(15,36,4):
                    open_time=get_open(u,p,period_5_30,3,7)
                    for o in range(32,50,5):
                        for q in range(73,110,10):
                            for x in range(25,52,8):
                                for z in range (35,120,25):
                                   all_times=get_signal(o,q,open_time,x*0.0001,z*0.0001)
                                   pro_test3.append([profit_count020(all_times,x*0.0001,z*0.0001),i,j,u,p,o,q,x,z])
                                   print(i,j,u,p,o,q,x,z)
