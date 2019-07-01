
import pandas as pd
from sklearn.decomposition import PCA  
from sklearn.preprocessing import StandardScaler


def reorganizer(df, cols):
    X=df.groupby('GeoLocation') #groups by lat/long
    L=[] #list of dataframes to be merged
    
    for x,dfa in X:
        Y=dfa[['Short_Question_Text','Data_Value']]
        Y=Y.set_index('Short_Question_Text') #make health issues the index
        
        Y=Y.T #make health issues the columns and data value the row
        Y.index=[x] #make tract code the index
        for z in cols:
            Y[z]=dfa[z].iloc[0] #makes TractFIPS column with value given by the groupby dataframe cooresponding to lat/long x
        L.append(Y)
        
    df_final=pd.concat(L,sort=True) #concatenate dataframes
    return df_final


def clean_it_up(df,year=2016):
    R=(['Diabetes','High Cholesterol','High Blood Pressure','Current Asthma', 
       'Coronary Heart Disease', 'High Cholesterol', 'Mental Health', 'Obesity', 'Sleep <7 hours' ] )

    
    df=df[(df['GeographicLevel']=='Census Tract') & (df['Year']==year)]  #reduce to census tracts   
    df=df[df['Short_Question_Text'].isin(R)] #reduce to poor health indicators
    
    return df



def cities_cleaner(df1,cols):
    df1=clean_it_up(df1) #reduces to year 2016 data and only relevant health issues
    df1=reorganizer(df1,cols) #makes a dataframe with columns given by health issues and TractFIPS
    df1.dropna(inplace=True) #drop rows with nan
    df1['TractFIPS']=df1['TractFIPS'].astype(int) #delete decimal places
    df1['TractFIPS']=df1['TractFIPS'].astype(str) #make tractfips a string
    df1.reset_index(inplace=True) 
    keep=(['Coronary Heart Disease', 'Current Asthma', 'Diabetes',
       'Mental Health', 'Obesity', 'Sleep <7 hours', 'TractFIPS']) #columns to keep
   
    return df1[keep]

#%% DATA
    
df_main=pd.read_csv("data/raw/500_Cities__Local_Data_for_Better_Health__2018_release.csv")

#clean up cities
df_main=cities_cleaner(df_main,['TractFIPS'])

#save to csv
df_main.to_csv("data/raw/500-cities-clean.csv",index=False)


