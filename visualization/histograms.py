#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 18:41:47 2019

@author: bhula-wesolekhousehold
"""
#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#%%
def make_histo(df,col,bins,name):
    X=df[col]
    plt.hist(X, bins=bins)
    plt.title("Frequency of "+name)
    plt.xlabel(name)
    plt.ylabel("Frequency")

    plt.savefig("visualization/plots/histograms/"+name+".png")
    
    plt.show()
    plt.clf()

#%%
df_main=pd.read_csv("data/non-normalized-health-and-environmental.csv")



columns=([ 'no-asthma',  'no-mental-health-prob','no-obesity', 'sleep >7', 'pollution','commute',
          'safety', 'density'])
for col in columns:
    name=col
    make_histo(df_main,col,30,name)
    

