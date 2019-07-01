#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 12:55:37 2019

@author: bhula-wesolekhousehold
"""
#%%
import pandas as pd
from sklearn.neighbors.regression import KNeighborsRegressor,check_array, _get_weights
from sklearn.neighbors import RadiusNeighborsRegressor
import matplotlib.pyplot as plt
import numpy as np
import math
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error,r2_score

#%%

def health_smoothing_rad_neighbors(df,health,cols,rad=10): #see R2-plotter for details
    X=df[cols]
    y=df[health]
    knn= KNeighborsRegressor(n_neighbors=rad).fit(X,y)  
    Y=knn.predict(X)
    df[health+'-smooth']=Y
    return df

def get_smoothed_cols(df,D): #computes smoothed columns and fits a linear regession
    DD={} #dictionary for linear regressors
    for x in ['no-obesity','no-asthma', 'no-mental-health-prob', 'sleep >7']: 
        cols,rad=D[x] #features and number of neighbors
        df=health_smoothing_rad_neighbors(df,x,cols,rad)  #smooth health issue column
        smoothed_col=x+"-smooth"   
        
        X=df[cols]
        y=df[smoothed_col]
        
        linreg=LinearRegression().fit(X,y) #fit linear regression
        DD[x]=linreg
    return df,DD

def writer(outfilename,string):
    outfilename.write(string+".\n")


def evaluator(df_train,df_test,L,name):
    D=({'no-asthma':(['density'],L[0]),'sleep >7':(['density','commute'],L[1]),
               'no-obesity':(['commute', 'density','safety'],L[2]),
               'no-mental-health-prob':(['commute', 'safety','density','pollution'],L[3])})
    
    df_train_smooth,DD=get_smoothed_cols(df_train,D) #makes smoothed columns and gives the dictionary of linear regression objects
    df_test_smooth,b=get_smoothed_cols(df_test,D)
    
    outfile=open(name,'w')
    
    R2_scores={} #dictionary for R2-scores
    for x in ['no-obesity','no-asthma', 'no-mental-health-prob', 'sleep >7']:
        linreg=DD[x] #get linear regressor object
        cols,rad=D[x] #features for health isssue x and number of neighbors rad
        
        X_train=df_train_smooth[cols]
        y_train=linreg.predict(X_train)
        X_test=df_test_smooth[cols]
        y_test=linreg.predict(X_test)
        
        #write a report
        writer(outfile,"For "+x+" the features are "+str(D[x][0])+" and the number of neighbors is "+str(D[x][1]))
        writer(outfile,"For "+x+" the coiefficients are "+str(linreg.coef_))
        writer(outfile,"For "+x+" the R2 score for test set is "+str(r2_score(y_test,df_test_smooth[x+"-smooth"])))
        writer(outfile,"For "+x+" the MSE score for test set is "+str(mean_squared_error(y_test,df_test_smooth[x+"-smooth"])))
        writer(outfile,"\n")
        R2_scores[x]=[r2_score(y_train,df_train_smooth[x+"-smooth"]),r2_score(y_test,df_test_smooth[x+"-smooth"])]
    outfile.close()
    return R2_scores
    

#%%


df_train=pd.read_csv("data/normalized-health-and-environmental-train.csv")
df_test=pd.read_csv("data/normalized-health-and-environmental-test.csv")
model="model-1"
run="test-final"
nums=[300,500,900,900]  #the number of neighbors to use in smoothing of asthma,sleep,obesity,and mental health, respectively



name="reports/evaluation-"+model+"-"+run+".txt"

D=evaluator(df_train,df_test,nums,name)
a=pd.DataFrame(D,index=['train','test']) #R2-values for test-train comparison
a.to_csv("data/R2-values.csv")


