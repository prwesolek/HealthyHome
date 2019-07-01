#!/usr/bin/env python
from flask import Flask, render_template, request,jsonify

from bokeh.embed import components
import bokeh
import pandas as pd

from flaskapp import app #uncomment for production
from flaskapp.calculator1 import main_loop  #uncomment for production
local=False #uncomment for production


# from calculator1 import main_loop #comment for production
# app = Flask(__name__) #comment for production
# local=True #comment for production


@app.route('/',methods = ['POST', 'GET'])
def home():
    D=({'AL': '01','AK': '02','AZ': '04','AR': '05','CA': '06','CO': '08','CT': '09',
     'DE': '10','DC': '11','FL': '12','GA': '13','HI': '15','ID': '16','IL': '17',
     'IN': '18','IA': '19','KS': '20','KY': '21','LA': '22','ME': '23','MD': '24',
     'MA': '25','MI': '26','MN': '27','MS': '28','MO': '29','MT': '30','NE': '31',
     'NV': '32','NH': '33','NJ': '34','NM': '35','NY': '36','NC': '37','ND': '38',
     'OH': '39','OK': '40','OR': '41','PA': '42','RI': '44','SC': '45','SD': '46',
     'TN': '47','TX': '48','UT': '49','VT': '50','VA': '51','WA': '53','WV': '54',
     'WI': '55','WY': '56'}) # This converts the input state abbreviation to the census state code.

    # Changes data source path if running locally.
    if local:
        df=pd.read_csv("data-all-tracts-normalized.csv")
    else:
        df=pd.read_csv("flaskapp/data-all-tracts-normalized.csv") #primary data source


    df=make_tract_str(df) #format tract identifying string.
    df['state']=df['TractFIPS'].map(state) #isolates state code
    X=df.groupby('state')# This is to speed up the code. (Future improvement: make a proper database.)

    if request.method == 'POST':
        # Import the post data
       numberandstreet1=request.form['name1']
       numberandstreet2=request.form['name2']
       town1=request.form['city1']
       town2=request.form['city2']
       state1=request.form['state1'].upper()
       state2=request.form['state2'].upper()
       commute1=request.form['commute1']
       commute2=request.form['commute2']
       a_ob=float(request.form['obesity'])
       a_as=float(request.form['asthma'])
       a_sl=float(request.form['sleep'])

       #Check to see if the state is not properly formatted.
       if state1 not in D.keys() or state2 not in D.keys():
           errorst="Please enter two digit code for state."
           return render_template('index.html', error=errorst)


       #Run main program which produces the healthscores, plot, intercept, formatted addresses, and commute times
       score1,score2,p,offset,add1,add2,com1,com2=main_loop(D,df,X,numberandstreet1,town1,state1,
                                                            numberandstreet2,town2,state2,
                                                            a_ob,a_as,a_sl,local,
                                                            commute1,commute2)

       if p=='a': #checks if the main_loop ran into a problem. In this case, it outputs score1, which contains the error message.
           return render_template('index.html',error=score1)

       else:
           # A little rounding, to avoid long floats
           x1=round(score1,2)
           x2=round(score2,2)
           com1=round(com1,2)
           com2=round(com2,2)

           #Find the winner
           if x1>x2:
               win=x1
               lose=x2
               add_win=add1
               add_lose=add2
               com_win=com1
               com_lose=com2

           else:
               win=x2
               lose=x1
               add_win=add2
               add_lose=add1
               com_win=com2
               com_lose=com1

           # get the figure from the bokeh plot
           fig_s1, fig_d1 = components(p)

           #Make some output strings
           title="HealthScore Contributions"
           note_offset="<li>The Healthscore is the sum of the contributions from the graph plus "+str(round(offset,2))+".</li>"
           note1=add_win.lower()
           hscore1=str(win)
           expected1=str(com_win)+ " minutes"

           note2=add_lose.lower()
           hscore2=str(lose)
           expected2=str(com_lose)+" minutes"

           return render_template('index.html',
                              fig_s1=fig_s1,
                              fig_d1=fig_d1,
                              title=title,
                              note_offset=note_offset,
                              note1=note1,
                              note2=note2,
                              hscore1=hscore1,
                              hscore2=hscore2,
                              expected1=expected1,
                              expected2=expected2,
                              name1=numberandstreet1,
                              name2=numberandstreet2,
                              bkversion=bokeh.__version__,)
    else:
        return render_template('index.html')


def state(x): #grab the state code from the census tract code.
    return x[:2]

def make_tract_str(df): #formats the tract code.
    df['TractFIPS']=df['TractFIPS'].astype(str)
    for i in df.index.values:
        if len(df.loc[i,'TractFIPS'])<11:
            df.at[i,'TractFIPS']='0'+str(df.loc[i,'TractFIPS'])
    return df




if __name__ == '__main__': #comment for production
   app.run(host='0.0.0.0', debug = True,port=5000) #comment for production
