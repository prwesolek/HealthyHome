#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:43:28 2019

@author: bhula-wesolekhousehold
"""
#%%
import pandas as pd
import numpy as np


def make_tract_str(df):
    df['TractFIPS']=df['TractFIPS'].astype(str) #make tract string
    for i in df.index.values: #check length 11
        if len(df.loc[i,'TractFIPS'])<11:
            df.at[i,'TractFIPS']='0'+str(df.loc[i,'TractFIPS'])
    return df


def pop_cleaner(df):
    df['TractFIPS']='' #make column for TractFIPS
    Errors=[] #error list
    for i in df.index.values:
        state=str(df.loc[i,'state']) #state code
        county=str(df.loc[i,'county']) #county code
        tract=str(df.loc[i,'tract']) #tract code
        if len(state)<2: #state must be length 2
            state='0'+state
            
        if 3-len(county)>0:  #county must be length 3
            n=3-len(county)
            county='0'*n+county
            
        if 6-len(tract)>0: #tract must be length 6
            n=6-len(tract)
            tract='0'*n+tract
            
        df.at[i,'TractFIPS']=state+county+tract #make TractFIPS code
        
        if len(df.loc[i,'TractFIPS'])!=11: #check for errors
            Errors.append(i)
            
    del df['NAME']
    del df['state']
    del df['county']
    del df['tract']
    return df, Errors


def tract_formater(df):
    for i in range(len(df)):
        raw=df.loc[i,'TractFIPS'] #read in tract description
        
        n_state=raw.find('state') #get state code postion
        num_state=raw[n_state+6:n_state+8] #get state code
        
        n_county=raw.find('county') #get county code position
        num_county=raw[n_county+7:n_county+10] #get county code
        
        n_tract=raw.find('tract') #get tract code position
        num_tract=raw[n_tract+6:n_tract+12] #get tract code
        
        df.at[i,'TractFIPS']=num_state+num_county+num_tract #get tract FIPS code
    return df




def make_exps(df):
    D=({'t<5':('5min',5), '5<t<9':('9min',9), '10<t<14':('14min',14),
        '15<t<19':('19min',19), '20<t<24':('24min',24),'25<t<29':('29min',29), 
        '30<t<34':('34min',34), '35<t<39':('39min',39), '40<t<44':('44min',44),
       '45<t<59':('52min',52), '60<t<89':('74min',74),
      '>90':('90min',90)}) #dictionary with column names as keys, and (shortname, time) as values
 
    columns=[] #new column names
    for name in D.keys():
        df[D[name][0]]=df[name]/df['totals'] #make probabilty 
        df[D[name][0]+'-expected']=df[D[name][0]]*D[name][1] #multiply probability by value
        #delete unnecessary columns
        del df[name] 
        del df[D[name][0]]
        
        columns.append(D[name][0]+"-expected") #add new column name
    return df,columns

def cities_cleaner(df1):
  
    df1['TractFIPS']=df1['TractFIPS'].astype(str) #make tractFIPS a string

    for i in df1.index.values: #make all strings have length 11
        if len(df1.loc[i,'TractFIPS'])!=11:
            df1.at[i,'TractFIPS']='0'+df1.loc[i,'TractFIPS']
    
    return df1 

def fix_commute_time(df):
    cols=(['t<5', '5<t<9', '10<t<14', '15<t<19', '20<t<24',
       '25<t<29', '30<t<34', '35<t<39', '40<t<44', '45<t<59', '60<t<89',
      '>90']) #relevant columns
    df.rename({'Unnamed: 0':'TractFIPS','long commute':'commute'},axis=1,inplace=True) #rename 
    
    df_commute=tract_formater(df)  #get TractFIPS code
    
    df_counts=df_commute[cols].sum(axis=1) #find total number of respondents for each tract
    df_commute['totals']=df_counts #make a totals column
    
    df_commute,cols=make_exps(df_commute) #makes columns of value*prob, so that we can compute expected value
        
    df_expected=df_commute[cols].sum(axis=1) #expected value 
    
    df_commute['commute']=df_expected #make expected value commute time column
    cols=cols+['totals']
    df_commute.drop(cols,axis=1,inplace=True) #drop unnecessary columns
    
    return df_commute[['TractFIPS','commute']]

def crime_data_fixer(dfa):
    df=dfa[['crime_rate_per_100000','FIPS_ST', 'FIPS_CTY']].copy() #reduce to relevant columns
    df['FIPS_ST']=df['FIPS_ST'].astype(str) #make state code a string
    df['FIPS_CTY']=df['FIPS_CTY'].astype(str) #make county code a string
    df['code']='a' #make a column for code
    
    for i in range(len(df)):
        if len(df['FIPS_ST'].iloc[i])==1:
            df.at[i,'FIPS_ST']='0'+df.loc[i,'FIPS_ST'] #state code must be length 2
        if len(df['FIPS_CTY'].iloc[i])==1: #county code must be length 3
            df.at[i,'FIPS_CTY']='00'+df.loc[i,'FIPS_CTY']
        if len(df['FIPS_CTY'].iloc[i])==2:
            df.at[i,'FIPS_CTY']='0'+df.loc[i,'FIPS_CTY']
        
   
    df['code']=df['FIPS_ST']+df['FIPS_CTY'] #get combined code
    df=df[['crime_rate_per_100000','code']] #take relevant columns
    df=df[df['crime_rate_per_100000']!=0] #drop any zeros. There are few of these
    return df


def make_log(df,columns):
    for col in columns:
        df[col]=df[col]+.0001 #eliminate  zeros
        df[col]=np.log(df[col]) #take log of each entry
    return df

def make_health_pos(df):
    conditions=(['Coronary Heart Disease', 'Current Asthma', 
                 'Diabetes','Mental Health', 'Obesity', 
                 'Sleep <7 hours']) #columns names in raw 500-cities data
    
    D=({'Coronary Heart Disease':'no-heart-disease', 
       'Current Asthma':'no-asthma', 
       'Diabetes':'no-diabetes','Mental Health':'no-mental-health-prob'
       , 'Obesity':'no-obesity', 
       'Sleep <7 hours':'sleep >7'}) #new names
    
    for condition in conditions:
        df[condition]=100-df[condition] #make positive
        
    df.rename(D,axis=1,inplace=True)
    return df

#%%
    
#read in data

df_alpha=pd.read_csv("data/raw/all-tracts/tracts-area-lat-long.csv") #area and lat/long data for each tract 

df_pol=pd.read_csv("data/raw/all-tracts/Environmental_Health_Hazard_Index.csv") #pollution data for each tract

df_pop=pd.read_csv("data/raw/all-tracts/population-data.csv") #population data for each tract

df_commute=pd.read_csv("data/raw/all-tracts/commute-time-data.csv") #commute time data for each tract

df_crime=pd.read_csv("data/raw/all-tracts/crime_data_w_population_and_crime_rate.csv") #crime data for each county


#%%
# area and lat/long data
df_alpha=make_tract_str(df_alpha) #format tract id to be a string of length 11


#Pollution data (this is not used in the end. Perhaps I will try to incorperate this in an updated model)
df_pol.rename({"TRACT_ID":"TractFIPS"},axis=1,inplace=True) #rename id tract
del df_pol['OBJECTID'] #delete unecessary column

df_pol=make_tract_str(df_pol) #format tract string

df_pol.rename({'HAZ_IDX':'pollution'},axis=1,inplace=True) #rename column


df_merged=pd.merge(df_pol,df_alpha,how='inner', on='TractFIPS') #merge pollution data with geographic data
    
print("merge 0 loss",len(df_alpha)-len(df_merged)) # Check to see how much was lost

#Population data
df_pop,errors=pop_cleaner(df_pop) #makes census tract code and outputs a list of errors
print("errors in population clean",len(errors)) #check to see if there are any errors


df_merged1=pd.merge(df_pop,df_merged,how='inner', on='TractFIPS')
    
print("merge 1 loss", len(df_alpha)-len(df_merged1)) #check to see how much was lost

#Make density 
df_merged1['area']=df_merged1['area']/(5280)**2 #turn square feet into square miles
df_merged1['density']=df_merged1['population']/df_merged1['area'] #make density column
df_merged1=make_log(df_merged1,['density']) #density is log normal, so take log

del df_merged1['population']
del df_merged1['area']

#commute data
df_commute=fix_commute_time(df_commute) #makes expected commmute time column

df_merged2=pd.merge(df_commute,df_merged1,how='inner', on='TractFIPS')

print("merge 2 loss",len(df_alpha)-len(df_merged2)) #check what was lost

#clean up crime
df_merged2['code']=df_merged2['TractFIPS'].str[:5] # reduce to county code

df_crime=crime_data_fixer(df_crime) #this formats the county code, so that we can merge.

df_merged3=pd.merge(df_crime,df_merged2,how='inner', on='code')

print("Total loss",len(df_alpha)-len(df_merged3)) #check data loss

df_merged3['safety']=100-(df_merged3['crime_rate_per_100000']/1000) #make crime rate into safety rate

#final clean up
df_merged3=df_merged3[['TractFIPS', 'commute', 'pollution','density','safety',
       'lat', 'long']] #reduce to relevant columns
print("size of final csv", len(df_merged3)) #check length again
df_merged3.to_csv("data/raw/all-tracts/merged-and-cleaned.csv",index=False) #write to csv


#%% add to 500 cities
df_tracts=pd.read_csv("data/raw/all-tracts/merged-and-cleaned.csv")
df_500=pd.read_csv("data/raw/500-cities-clean.csv")

#tidy 500 cities up
df_500=make_health_pos(df_500)
df_500=df_500[['TractFIPS','no-obesity', 'sleep >7','no-asthma','no-mental-health-prob']] #reduce to relevant columns

#format TractFIPS column
df_500=make_tract_str(df_500) 
df_tracts=make_tract_str(df_tracts)

df_merged=pd.merge(df_500,df_tracts,how='inner', on='TractFIPS')

print("merge loss", len(df_500)-len(df_merged)) #check how much was lost
df_merged.to_csv("data/non-normalized-health-and-environmental.csv",index=False)


#%% make a file with income

df_main=pd.read_csv("data/raw/all-tracts/merged-and-cleaned.csv")
df_add=pd.read_csv("data/raw/all-tracts/per-capita-income.csv")


df_main=make_tract_str(df_main)
df_add=tract_formater(df_add)
df_add.head()
df_merged=pd.merge(df_main,df_add,how='inner',on='TractFIPS')
df_merged.to_csv("data/raw/all-tracts/merged-and-cleaned-with-income.csv",index=False)