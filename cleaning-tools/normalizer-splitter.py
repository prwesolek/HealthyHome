#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 08:16:27 2019

@author: bhula-wesolekhousehold
"""

#%%

import pandas  as pd

from scipy.stats import zscore
from sklearn.model_selection import train_test_split




#%%

def make_t_score(df,cols):
    df[cols]=df[cols].apply(zscore)
    for col in cols:
        df[col]=(df[col]*10)+50
    return df

def scale_out_of_100(df,col):
    m=df[col].max()
    df[col]=(df[col]/m)*100
    return df

#%%
cols=[ 'density', 'safety']

#all environmental data
df_env=pd.read_csv("data/raw/all-tracts/merged-and-cleaned.csv")
l_env=len(df_env)
df_env.dropna(inplace=True)
print("all environmental data loss",l_env-len(df_env))
df_env=make_t_score(df_env,cols)

df_env.to_csv("data/normalized-environmental.csv",index=False)


# 500 cities data

df_500=pd.read_csv("data/non-normalized-health-and-environmental.csv")
l_500=len(df_500)
df_500.dropna(inplace=True)
print("500 cities loss", l_500-len(df_main))

X_train,X_test=train_test_split(df_500,test_size=.5) #50/50 test train split

X_train=make_t_score(X_train,cols)
X_test=make_t_score(X_test,cols)

X_train.to_csv("data/normalized-health-and-environmental-train.csv",index=False)
X_test.to_csv("data/normalized-health-and-environmental-test.csv",index=False)


#%%
#all environmental data
df_env=pd.read_csv("data/raw/all-tracts/merged-and-cleaned-with-income.csv")
l_env=len(df_env)
df_env.dropna(inplace=True)
print("all environmental data loss",l_env-len(df_env))
df_env=make_t_score(df_env,cols)


df_env.to_csv("data/normalized-environmental-with-income.csv",index=False)
