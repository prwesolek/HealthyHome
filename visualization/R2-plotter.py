#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 12:49:54 2019

@author: bhula-wesolekhousehold
"""

#%%

import pandas as pd
from sklearn.neighbors.regression import KNeighborsRegressor,check_array, _get_weights
from sklearn.neighbors import RadiusNeighborsRegressor
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error
#%%

def health_smoothing(df,health,cols,rad=10):
    X=df[cols] #features
    y=df[health] #data

    knn= KNeighborsRegressor(n_neighbors=rad).fit(X,y) #fit KNN for smoothing
    
    Y=knn.predict(X) #smoothed column
    df[health+'-smooth']=Y #make new column in dataframe
    return df
    
def R2_plotter(df1,health,cols,name,length):
    X=np.linspace(10,length,num=20) #20 points from 10 to length
    Y=[] #R2 values
    for x in X:
        x=math.ceil(x) #take ceiling
        df=health_smoothing(df1,health,cols, x) #make a column by KNN smoothing
        X1=df[cols] #input features
        w=df[health+'-smooth'] #output value
        linreg=LinearRegression().fit(X1,w) #fit a linear regressiong
        z=linreg.score(X1,w) #compute R2 score
        Y.append(z) 
    #make a plot
    plt.scatter(X,Y, marker= 'o', alpha=0.8)
    plt.xlabel('Number of neighbors to smooth')
    plt.ylabel('R2 score for '+health)
    plt.savefig(name+".png")
    plt.show()
    plt.clf()
    

 #%%
df_main=pd.read_csv("data/normalized-health-and-environmental-train.csv")


D=({'no-asthma':['density'],
    'sleep >7':['density','commute'],
    'no-obesity':['commute', 'safety','density'],
    'no-mental-health-prob':['commute', 'safety','density']}) #features to use with for each health issue

for health in D.keys():
    name1="visualization/plots/R2-tuning-"+health #filename for plot
    R2_plotter(df_main,health,D[health],name1,5000)  #make plot of number of neighbors verse R2

