<h2>HealthyHome: Find a healthy place to live in your city</h2>

<h2> Summary </h2>

<p>I built this project over three weeks as a Health Data Science Fellow at <a href="https://www.insighthealthdata.com/"> Insight</a> during the Summer 2019 session. The output of the project is the webapp <a href="http://philwesolek.com/"> HealthyHome </a> which helps renters and homebuyers compare properties by how the environmental features of a neighborhood (commute time, population density, and safety) affect health  (weight, asthma, and sleep time).</p>

<p>  The underlying mathematical model is a collection of linear regressions which predicts obesity rates, asthma rates, and percent of people reporting adequate sleep time for a neighborhood from the average commute time, population density, and crime rate for the neighborhood.  A smoothing process via K-nearest Neighbors is used to account for confounding factors, and this process substantially improves the accuracy of the linear regressions. This smoothing process can be considered as a form of <a href="https://en.wikipedia.org/wiki/Convolution">convolution</a>. </p> 

<p> The webapp takes as input two addresses, the user's commute time, and the user's level of concern about weight, asthma, or sleep time. The application then computes the census tracts for each address to obtain the environmental data, runs the linear regressions to compute non-obesity rate, non-asthma rate, and percent of people reporting adequate sleep, and produces a HealthScore by taking a weighted sum of the outputs of the linear regressions, where the weights are given by the level of importance assigned by the user for the aforementioned health concerns. The property with the higher HealthScore is reported to be the better property. The webapp  is built using flask and hosted on Amazon Web Services. The webapp additionally uses Google's geocoding API. An API key can be obtained <a href="https://developers.google.com/maps/documentation/geocoding/start?utm_source=google&utm_medium=cpc&utm_campaign=FY18-Q2-global-demandgen-paidsearchonnetworkhouseads-cs-maps_contactsal_saf&utm_content=text-ad-none-none-DEV_c-CRE_315916118282-ADGP_Hybrid+%7C+AW+SEM+%7C+SKWS+~+Geocoding+API-KWID_43700039136946657-kwd-335278985932-userloc_9001873&utm_term=KW_%2Bgeocoder%20%2Bapi-ST_%2Bgeocoder+%2Bapi&gclid=COmfluGynuMCFVndswodWiIK0Q" >here</a>; your code must be input on line 55 in flaskapp/calculator1.py.</p>

<p>The data is from 2010 or later and has a census tract level of granularity. <a href="https://en.wikipedia.org/wiki/Census_tract">Census tracts</a> are geographic units for the US Census Bureau which are roughly equivalent to a neighborhood; they contain an average of 4,000 people. </p>

<p> I did most of this work in Spyder, and the scripts reflect this choice. I translated some of the more interesting programs to jupyter notebooks.</p>

<h2> Model Details </h2>

<h3> Feature Selection </h3>
 <p> The features used to predict each health issue rate are selected by running linear regressions to see how much each feature contributed and by looking in the public health literature for previously established correlations; see the Feature-selection jupyter notebook for the regressions. These linear regressions additionally suggest that the percentage of people reporting good mental health does not depend linearly on the environmental features, so I omitted this health issue. The table below gives the environmental features used as predictors for each health issue. </p>

<table style="width:100%" align="center">
  <tr>
    <th>Health Issue Rate</th>
    <th>Environmental Features</th> 
  
  </tr>
  <tr>
    <td>non-asthma</td>
    <td>population density</td>
  
  </tr>
  <tr>
    <td>non-obesity</td>
    <td>population density, commute time, safety</td>
 
  </tr>
  <tr>
    <td>adequate sleep</td>
    <td>population density,  commute time</td>
  </tr>
 
</table>


<h3> Smoothing and linear regressions</h3>
<p> Health issue rates, e.g. asthma rates, for a neighborhood depend on factors well beyond basic environmental features; the scatter plots and KDE plots in visualization/plots for the case of population density vs non-asthma rates illustrate this fact. Environmental features none-the-less affect health, so to account for the many confounding factors, I replace the health issue rate for a given neighborhood with an average health issue rate for similar neighborhoods, via K-nearest Neighbors. This average health issue rate I call the <b>smoothed</b> rate. The details follow. </p>

<ul>
<li><b>non-asthma rate:</b> For a given neighborhood, the smoothed  rate is the average non-asthma rate for the 300 neighborhoods with most similar population density.  </li>

<li><b>non-obesity rate:</b> For a given neighborhood, the smoothed rate is the average non-obesity rate for the 900 neighborhoods with most similar population density, commute time, and safety.  </li>

<li><b>percent reporting adequate sleep:</b> For a given neighborhood, the smoothed rate is the average percentage reporting adequate sleep for the 500 neighborhoods with most similar population density and commute time.  </li>

</ul>

<p>The number of neighbors to use in the smoothing process is determined by trying to optimize for R2 while avoiding overfitting. This is accomplished by considering the graph of neighbors smoothed vs R2 for each health issue; see visualization/plots for these graphs. The number of neighbors is chosen such that the R2 value is at least .7 and the rate of increase of the graph begins to decrease.  The script visualization/R2-plotter.py graphs the number of neighbors used in the smoothing vs the R2 value.</p>


<p> After smoothing, the following linear regressions are run:</p>
<ul>
<li>population density vs smoothed non-asthma rate </li>

<li>population density, commute time, and safety vs smoothed non-obesity rate.  </li>

<li>population density and commute time vs smoothed percentage reporting adequate sleep. </li>

</ul>
<p> These regressions are run via model.py. This script outputs the details of these regressions in report/regression-parameters-model1-final-param.txt. This program also outputs data/weights.csv which contains the coefficients and intercepts to be used by the webapp.</p>

<h3> Evaluation</h3>
<p>  I reserve half the data for testing; a 50-50 test-train split seems prudent as the smoothing process is in principle sensitive to the size of the data set in question. To evaluate the model, I smooth the test set health issue rate values using the smoothing parameters determined from the train set. The linear models are then applied and the R2 scores calculated.  The model behaves well on the test set, with R2 values staying over .7. The plot visualization/plots/R2-Train-Test.png gives a side-by-side comparison of the R2 values. </p>

<p> R2 is used for evaluation as this metric measures the variance accounted for by the model. The ultimate goal is to distinguish locations based on their health issue rates. The model therefore needs to be able to detect differences between health issue rates, and so the model needs to be able to account for the variance between data points. </p>

<p>The script evaluation-tools/test-train-eval.py performs the evaluation. This script builds the linear model from the training data, smooths the test data, and computes the R2 value for the predicted smoothed values for the test set data. A report titled reports/evaluation-model-1-test-final.txt is written. </p>


 
 <h3> Data and Preprocessing </h3>

 
 <h4> Health data</h4>
The health data is taken from the CDC's  2018 <a href="https://www.cdc.gov/500cities/index.htm">500 Cities Project</a>. This data set has detailed health information at the census tract level for the 500 largest cities in the US. This data set covers approximately 26,000 census tracts. The data set can be downloaded as a csv <a href="https://catalog.data.gov/dataset/500-cities-local-data-for-better-health-fc759">here</a>. Due to the large size of this file, the raw data is not contained in the repo. The script which cleans the raw data is cleaning-tools/clean-500-cities.py.


<h4>Environmental data</h4>
The environmental data covers all census tracts (~74000) and comes from four sources.
<ol>
  <li><p> <b>FBI Uniform Crime Reporting:</b> This data set gives county level information on crime from 2016. In the present repo, these data are located at data/raw/all-tracts/crime_data_w_population_and_crime_rate.csv. The data may be found online <a href="https://www.kaggle.com/mikejohnsonjr/united-states-crime-rates-by-county">here </a>.</p>
    <p> This data set is used to obtain crime rates for every county in the US. Some minor cleaning is necessary, and this is done in merging-tools/merge-all-tracts.py. This data set is somewhat unsatisfactory as it is not at the census tract level.</p>
  </li>
  
  <li> <p><b> US Census Geographic Data: </b> This geodatabase gives geographic data for census tracts. The database is too large to include in this repo. The raw data may be found <a href="https://www2.census.gov/geo/tiger/TGRGDB16/" >here</a>; the file name is tlgdb_2016_a_us_substategeo.gdb. </p>
  <p> This data set is used to obtain latitude and longitude, land area, and census tract code for every census tract in the US. The script cleaning-tools/area-importer.py extracts this information from the geodatabase. </p> </li>

 <li><p><b> 2016 US Census American Communities Survey:</b> This database gives detailed information on each census tract. This data set is large and best accessed via the census API. For more details on this data set see <a href="https://www.census.gov/programs-surveys/acs">here</a></p>
 <p> This data set is used to obtain expected commute time. The script cleaning-tools/census-data-importer.py downloads the relevant information via the python library <a href="https://pypi.org/project/CensusData/">censusdata</a>. The script additionally requires the state codes used by the census. These codes are located in data/raw/all-tracts/state-geocodes-v2016.csv.</p>
 </li>

 <li><p><b> 2010 US Census Summery File 1:</b> This database contains the data compiled by the 2010 census. This data set is large and best accessed via the census API. For more details on this data set see <a href="https://www.census.gov/data/datasets/2010/dec/summary-file-1.html">here</a></p>
 <p> This data set is used to obtain census tract population. The script cleaning-tools/census-data-importer.py accesses and downloads the relevant information via the python library requests. An API key is needed to access this file; one can obtain a key <a href="https://api.census.gov/data/key_signup.html">here</a>. </p>
  </li>
      
    
</ol>
 <h4>Preprocessing</h4>
<p>The processed data consist of three files: data/normalized-environmental.csv, data/normalized-health-and-environmental-train.csv, and data/normalized-health-and-environmental-test.csv. The processing steps from the raw data are as follows:</p>
<ol>
<li><p> Compute population density</p></li>
<li><p> Take log of population density; the raw data is log-normally distributed.</p></li>
<li><p> Compute expected commute time. <p></li>
<li> <p> Turn health issue rates into non-occurrence rates; for instance, percent obesity becomes percent non-obesity. </p></li>
<li> <p>Turn crime rate into safety rate. </p></li>
<li> <p> 50-50 test-train split for merged health and environmental data.<p> </li>
<li> <p>Make safety rate and population density into T-scores. </p> </li>
</ol>
<p>The first five tasks are accomplished via merging-tools/merge-all-tracts.py. The last two are done via cleaning-tools/normalizer-splitter.py</p>

 

<h2> Future Improvements </h2>
<ul>
<li> <b> other features: </b> Health issue rates depend on many hidden variables, and to account for this, I would like to bring in more environmental features. Here are several ideas: number of grocery stores in neighborhood, number of parks in neighborhood, number of urgent care clinics in neighborhood, public transportation in neighborhood, <a href="https://www.walkscore.com/">WalkScore</a>, and <a href="http://howloud.com/">noise level</a>. </li>

<li> <b> mental health:</b> I would like to include the percentage of people reporting good mental health as a heath issue, even if this means moving to a non-linear model. </li>

<li> <b> better data: </b> I would like to obtain crime data on the census tract level; these data are currently at the county level. I would also like to find better pollution data. I believe the current pollution data that I have is normalized in such a way as to make it a poor predictor in my model. </li>

<li> <b> more sophistication: </b> My current smoothing process is rather naive. I would like to either smooth by convolving my data points with a normal distribution or smooth by dynamically computing the number of neighbors to use for each data point. I would also like to explore hierarchical linear models to account for random effects, such as the region of the United States.</li>

<li> <b> better user interface: </b> I would like to add a feature allowing the user to input his or her work address so that the model can compute commute time.  </li>

</ul>

