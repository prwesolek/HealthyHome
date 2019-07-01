
#%%

import pandas as pd
import censusdata
import requests


#%%

def get_pop_data(state):
    key="YOUR CENSUS API KEY" #get an API key from the census
    request = ("https://api.census.gov/data/2010/dec/sf1?get=P001001,NAME&for=tract:*&"+
               "in=state:"+state+"&key="+key ) #this url requests the population table
    r = requests.get(request) #make request
    L=r.json() #pop data
    header=L[0] #header with column titles
    body=L[1:] # data
    df=pd.DataFrame(body,columns=header)
    return df
    
def state_len(df): #makes state codes length two strings
    for i in range(len(df)):
        if len(df.loc[i,'State'])<2:
            df.at[i,'State']='0'+str(df.loc[i,'State'])
    return df

def get_state_codes(x):
    codes=[]
    for state in x.keys():
        y=x[state].sumlevel()
        codes.append(y)
    return codes


#%% Import population data
df_codes=pd.read_csv("data/raw/all-tracts/state-geocodes-v2016.csv") #state census codes
df_codes['State']=df_codes['State'].astype(str) #make state code a string
df_codes=state_len(df_codes) #make state code is two digits

data_frames=[]
for i in range(len(df_codes)):
    x=df_codes.loc[i,'State']
    statedata= get_pop_data(x) #get population data for all census tracts in state x
    data_frames.append(statedata)
    
df_concat=pd.concat(data_frames)

df_concat.to_csv("data/raw/all-tracts/population-data.csv",index=False)



#%% commute time importer 

L=(['B08303_002E','B08303_003E','B08303_004E', 'B08303_005E','B08303_006E',
'B08303_007E','B08303_008E','B08303_009E','B08303_010E','B08303_011E',
'B08303_012E','B08303_013E']) #commute time tables

D=({'B08303_002E':'t<5','B08303_003E':'5<t<9','B08303_004E':'10<t<14',
    'B08303_005E':'15<t<19','B08303_006E':'20<t<24',
'B08303_007E':'25<t<29','B08303_008E':'30<t<34','B08303_009E':'35<t<39',
'B08303_010E':'40<t<44','B08303_011E':'45<t<59',
'B08303_012E':'60<t<89','B08303_013E':'>90'}) #dictionary to make titles human-readable

df_codes=pd.read_csv("data/raw/all-tracts/state-geocodes-v2016.csv") #state census codes
df_codes['State']=df_codes['State'].astype(str) #make state code a string
df_codes=state_len(df_codes) #make state code is two digits

data_frames=[]
for i in range(len(df_codes)):
    x=df_codes.loc[i,'State']
    statedata= censusdata.download('acs5', 2016, 
                                   censusdata.censusgeo([('state', x),('county', '*'),('tract', '*')]),
                                   L) #downloads commute time data from census for state x
    statedata.rename(D,axis=1,inplace=True)
    data_frames.append(statedata)
    
df_concat=pd.concat(data_frames)

df_concat.to_csv("data/raw/all-tracts/commute-time-data.csv",index=False)

