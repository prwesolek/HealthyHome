#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 16:43:24 2019

@author: bhula-wesolekhousehold
"""

#%%

import fiona

#%%

gdb = fiona.open("YOUR DATABASE FILE",layer='Census_Tract') #download tlgdb_2016_a_us_substategeo.gdb
gdb.driver 
gdb.schema # {'geometry': '3D MultiLineString', 'properties': OrderedDict([(u'FCSubtype', 'int'), ...
Area=[]
Tract=[]
lat=[]
lon=[]
for i in range(74133): #goes through every census tract; check the length is correct
    x=gdb.next() #increments the database
    Tract.append(x['properties']['GEOID']) #tract code
    lat.append(x['properties']['INTPTLAT']) #lat
    Area.append(x['properties']['ALAND']) #area
    lon.append(x['properties']['INTPTLON']) #long
    
D={'TractFIPS':Tract,'lat':lat,'long':lon,'area':Area}
df=pd.DataFrame(D)
df.to_csv("data/raw/all-tracts/tracts-area-lat-long.csv",index=False)