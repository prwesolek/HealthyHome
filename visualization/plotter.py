#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 18:51:14 2019

@author: bhula-wesolekhousehold
"""
#%%
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
#%%%

df_r2=pd.read_csv("data/R2-values.csv",index_col='Unnamed: 0')
del df_r2['no-mental-health-prob']
D={'no-obesity':'obesity','no-asthma':'asthma','sleep >7':'sleep'}
df_r2.rename(D,axis=1,inplace=True)
df=df_r2.T.copy()


#turn dataframe into a two column frame to use seaborn
df['run']='a'
df1=df[['train','run']].copy()
df1['run']='train'
df1.rename({'train':'R2-value'},axis=1,inplace=True)
df2=df[['test','run']].copy()
df2['run']='test'
df2.rename({'test':'R2-value'},axis=1,inplace=True)
a=pd.concat([df1,df2])
a.reset_index(inplace=True)
a.rename({'index':''},axis=1,inplace=True)



name="visualization/plots/R2-Train-Test"


sns.set(font_scale=1.5)
sns_plot=sns.factorplot(x='', y='R2-value', hue='run', data=a, kind='bar')
sns_plot.set(ylim=(0,1))
sns_plot.savefig(name+".png")



#%%


sns.set(font_scale=1)
df_main=pd.read_csv("data/normalized-health-and-environmental-train.csv")
df=df_main[['density','pollution','safety','commute']]
df2=df_main[['no-obesity', 'sleep >7', 'no-asthma',
       'no-mental-health-prob']]
corr2=df2.corr()
sns_plot2=sns.heatmap(corr2, 
        xticklabels=corr2.columns,
        yticklabels=corr2.columns)
figure2 = sns_plot2.get_figure()    
figure2.savefig("visualization/plots/corollation-matrix-health-issues.png",bbox_inches='tight')
plt.clf()


sns.set(font_scale=1)
corr=df.corr()
sns_plot=sns.heatmap(corr, 
        xticklabels=corr.columns,
        yticklabels=corr.columns)
figure = sns_plot.get_figure()    
figure.savefig("visualization/plots/corollation-matrix-features.png",bbox_inches='tight')
plt.clf()

