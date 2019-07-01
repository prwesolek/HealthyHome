#!/usr/bin/env python3

import pandas as pd
from sklearn.neighbors.regression import KNeighborsRegressor,check_array, _get_weights
from sklearn.neighbors import RadiusNeighborsRegressor
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error,r2_score


def writer(outfilename,string):
    outfilename.write(string+".\n")


def health_smoothing(df,health,cols,rad=10): #see R2-plotter for documentation
    X=df[cols]
    y=df[health]
    knn= KNeighborsRegressor(n_neighbors=rad).fit(X,y)
    Y=knn.predict(X)
    df[health+'-smooth']=Y
    return df

def add_missing_features_vals(D): #adds missing keys to dictionary D
    L=['commute', 'safety','density','pollution']
    for x in L:
        if x not in D.keys():
            D[x]=0
    return D


def weight_computer(df,outfile,L):
    #keys for DD are the health features. The values are ordered pairs (features, n_neighbors for KNN)
    DD=({'no-asthma':(['density'],L[0]),
        'sleep >7':(['density','commute'],L[1]),
        'no-obesity':(['commute', 'safety','density'],L[2]),
        'no-mental-health-prob':(['commute', 'safety','density','pollution'],L[3])}) 

    D1=({'no-asthma':'asthma','sleep >7':'sleep',
        'no-obesity':'obesity','no-mental-health-prob':'mental'}) #renaming dictionary
    
    I=[] #list of intercepts
    features=[] #list of dictionaries where each dictionary has the feature as a key and the coiefficient as the value

    for x in ['no-obesity','no-asthma', 'no-mental-health-prob', 'sleep >7']:
        I.append(D1[x])
        vals={} #coiefficients for regression

        cols,rad=DD[x]

        df_smooth=health_smoothing(df,x,cols,rad) #make smoothed column for health issue x

        smoothed_col=x+"-smooth"
        X=df_smooth[cols]
        y=df_smooth[smoothed_col]

        linreg=LinearRegression().fit(X,y) #fit a linear regression
        Y=linreg.predict(X) #predict Y values from regression
        
        #write a report
        writer(outfile,"For "+x+" the features are "+str(DD[x][0])+" and the number of neighbors is "+str(DD[x][1]))
        writer(outfile,"For "+x+" the coiefficients are "+str(linreg.coef_))
        writer(outfile,"For "+x+" the intercept is "+str(linreg.intercept_))
        writer(outfile,"For "+x+" the R2 score is "+str(r2_score(Y,y)))
        writer(outfile,"For "+x+" the MSE score is "+str(mean_squared_error(Y,y)))
        writer(outfile,"\n")

        n=len(DD[x][0]) #number of features
        for i in range(n):
            vals[DD[x][0][i]]=linreg.coef_[i] #set key to be i-th feature and value to be i-th coiefficient

        vals=add_missing_features_vals(vals) #make key for other features with value 0

        vals['intercept']=linreg.intercept_ #make an entry for the intercept
        features.append(vals)

    return df,features

#%%



df_main=pd.read_csv("data/normalized-health-and-environmental-train.csv")
model="model1"
run="final-param"
nums=[300,500,900,900] #the number of neighbors to use in smoothing of asthma,sleep,obesity,and mental health, respectively




name="reports/regression-parameters-"+model+"-"+run+".txt"#name of report txt file
outfile=open(name,'w') #open report file

df,F=weight_computer(df_main,outfile,nums) #outputs dataframe with smoothed columns as well as a dictionary with coiefficients

outfile.close()
a=pd.DataFrame(F,index=['obesity','asthma', 'mental', 'sleep']) #makes a dataframe from the list of dictionaries

a.to_csv("data/weights.csv") 
