#!/usr/bin/env python
import pandas as pd
import requests
import json
import numpy as np
import bokeh
from bokeh.core.properties import value
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import dodge
import geopandas
import math
import censusgeocode as cg
from bokeh.models import Span


def get_add(r): #get the address that the google api outputs
    number=''
    street=''
    city=''
    state=''

    if 'address_components' not in r[0].keys(): #checks to see if google api returned something funny
        return ''
    else:
        info=r[0]['address_components'] #list of address get_components

        #step through to find number,street, city, and state
        for i in range(len(info)):
            if 'types' not in info[i].keys():
                continue
            if info[i]['types']==['street_number']:
                number=info[i]['short_name']
            if info[i]['types']==['route']:
                street=info[i]['short_name']
            if info[i]['types']==['locality', 'political']:
                city=info[i]['short_name']
            if info[i]['types']==['administrative_area_level_1', 'political']:
                state=info[i]['short_name']
        #make address string
        add=str(number)+" "+str(street)+" "+str(city)+" "+str(state)

        # make a short address string.
        if str(number) !='':
            add_short=str(number)+" "+str(street)
        elif str(street)!='':
            add_short=str(street)+" "+str(city)
        else:
            add_short=str(city)+" "+str(state)

        return add,add_short


def lat_long_comp(numberandstreet,town,state): #uses google api to compute lat and long
    key="YOUR API CODE" #google maps api key
    url="https://maps.googleapis.com/maps/api/geocode/json?"

    #format the addresses a bit; this is probably not necessary.
    numberandstreet=numberandstreet.replace(" ","+")
    town=town.replace(" ","+")

    req="address="+numberandstreet+",+"+town+",+"+state+"&key="+key #string for api

    r = requests.get(url+req)
    results = r.json()['results'] #api output
    location = results[0]['geometry']['location'] #lat/lon
    return location['lat'], location['lng'],results


def closest_point_comp(lat,long,df):
    df1=df.copy() #make a copy of dataframe
    df1['lat1']=lat #make a constant column
    df1['long1']=long #make a constant column

    gdf = geopandas.GeoDataFrame(
            df, geometry=geopandas.points_from_xy(df['long'], df['lat'])) #makes a geodataframe with a geometry column

    gdf1 = geopandas.GeoDataFrame(
            df1, geometry=geopandas.points_from_xy(df1['long1'], df1['lat1'])) #makes a second geodataframe with geometry column from constant columns above

    n=gdf.distance(gdf1).idxmin() #use geopandas magic to compute the distance between lat,long points and then find the index of the least distance
    return n


def get_components(df,D,m1,m2,local,commute1,commute2):

    #load linear regression weights info. If locally hosted, the location is different
    if local:
        df_w=pd.read_csv("weights.csv",index_col='health')
    else:
        df_w=pd.read_csv("flaskapp/weights.csv",index_col='health')

    offset=0 #this will be the sum of the intercepts for each regression

    for health in ['obesity','asthma','sleep']:
        df_w.at[health]=df_w.loc[health]*D[health] #multiply regression coiefficients and intercept by the user weights
        offset=offset+df_w.loc[health,'intercept'] #add intercept to offset

    #check what user did with commute time
    if commute1=='use-default':
        com1=df.loc[m1,'commute'] #take the average commute time
    else:
        com1=float(commute1) #use the value selected

    if commute2=='use-default':
        com2=df.loc[m2,'commute']
    else:
        com2=float(commute2)

    L1 = [com1*df_w['commute'].sum(),
         df.loc[m1,'density']*df_w['density'].sum(),
         df.loc[m1,'safety']*df_w['safety'].sum()] #values for bar plot

    L2= [com2*df_w['commute'].sum(),
        df.loc[m2,'density']*df_w['density'].sum(),
        df.loc[m2,'safety']*df_w['safety'].sum()] #values for bar plot

    return L1,L2,offset,com1,com2

def plot_bokeh(L1,L2,name1,name2):
    bokeh.plotting.reset_output #clear the plot from last times

    name1=name1.lower() #location 1
    name2=name2.lower() #location 2

    #compute the chart range
    m=max(L1+L2)
    mm=min(L1+L2+[0])
    m=math.ceil(m)+1
    mm=math.floor(mm)-3

    #labels for bars and legend
    env_factors = ['commute time', 'population density','safety']
    locations = [name1, name2]

    data = {'env_factors' : env_factors,
            name1  : L1,
            name2   : L2 } #data dictionary for bokeh plot

    #make the plot Future: Use seaborn. This is more complicated than I like.
    source = ColumnDataSource(data=data)

    p = figure(x_range=env_factors, y_range=(mm, m), plot_height=350,plot_width=800,
               toolbar_location=None, tools="")

    p.vbar(x=dodge('env_factors', -0.25, range=p.x_range), top=name1, width=0.2, source=source,
           color="#469e34", legend=value(name1))

    p.vbar(x=dodge('env_factors',  0.0,  range=p.x_range), top=name2, width=0.2, source=source,
           color="#e37d59", legend=value(name2))
    hline = Span(location=0, dimension='width', line_color='black', line_width=1)
    p.renderers.extend([ hline])
    p.x_range.range_padding = 0.1
    p.legend.location = "bottom_right"
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = "20pt"
    p.xaxis.major_label_text_font_size = "15pt"
    p.background_fill_color = None
    p.border_fill_color = None
    return p




def main_loop(D,df,X,numberandstreet1,town1,state1,numberandstreet2,town2,state2,a_ob,a_as,a_sl,local,commute1,commute2):


    try:
        weights={'obesity':a_ob,'asthma':a_as,'sleep':a_sl} #health issue weights from user

        lat1,long1,r1=lat_long_comp(numberandstreet1,town1,state1) # gets latitude and longitude
        add1,add_short1=get_add(r1) #gets address from google

        df1=X.get_group(D[state1]) #get dataframe cooresponding to state. This is really selecting a table, if I did it in SQL
        m1=closest_point_comp(lat1,long1,df1) #computes census tract

        lat2,long2,r2=lat_long_comp(numberandstreet2,town2,state2)
        add2,add_short2=get_add(r2)

        df2=X.get_group(D[state2])
        m2=closest_point_comp(lat2,long2,df2)

        L1,L2,offset,com1,com2=get_components(df,weights,m1,m2,local,commute1,commute2) #gets list of values for bar chart, coiefficient offset, and commute times

        #compute winner and loser
        if sum(L1)+offset>sum(L2)+offset:
            win_add=add_short1
            lose_add=add_short2
            win_vals=L1
            lose_vals=L2
        else:
            win_add=add_short2
            lose_add=add_short1
            win_vals=L2
            lose_vals=L1

        p=plot_bokeh(win_vals,lose_vals,win_add,lose_add)


        return sum(L1)+offset,sum(L2)+offset,p,offset,add1,add2,com1,com2

    except:
        error="Please check address formatting and try again."
        return error,error,'a','offset','add1','add2','com1','com2'
