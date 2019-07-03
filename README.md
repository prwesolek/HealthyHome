<h2>HealthyHome: Find a healthy place to live in your city</h2>

<h3> NOTE: I am in the process of updating this repo. It will be completed by July 7 2019 </h3>

<h2> Summary </h2>

<p>I built this project as a Health Data Science Fellow at <a href="https://www.insighthealthdata.com/"> Insight</a> during the Summer 2019 session. The output of the project is the webapp <a href="http://philwesolek.com/"> HealthyHome </a> which helps renters and homebuyers compare properties by how environmental features of a neighborhood (commute time, population density, and safety) affect health  (weight, asthma, and sleep time).</p>

<p>  The underlying mathematical model is a collection of linear regressions which predicts obesity rates, asthma rates, and percent of people reporting more than seven hours of sleep for a neighborhood from the average commute time, population density, and crime rate for the neighborhood.  A smoothing process via K-nearest Neighbors is used to account for confounding factors, and this process substantially improves the accuracy of the linear regressions. This smoothing process can be considered as a form of <a href="https://en.wikipedia.org/wiki/Convolution">convolution</a>. </p> 

<p> The webapp takes as input two addresses, the user's expected commute time, and the user's level of concern about weight, asthma, or sleep time. The application then computes the census tracts for each address to obtain the environmental data, runs the linear regressions to compute non-obesity rate, non-asthma rate, and percent of people reporting a good night's sleep, and produces a HealthScore by taking a weighted sum of the outputs of the linear regressions, where the weights are given by the user's level of concern for the aforementioned health issues. The property with the higher HealthScore is reported to be the better property. The webapp  is built using flask and hosted on Amazon Web Services.</p>

<p>The data is from 2010 or later and has a census tract level of granularity. (<a href="https://en.wikipedia.org/wiki/Census_tract">Census tracts</a> are geographic units for the US Census Bureau which are roughly equivalent to a neighborhood; they contain an average of 4,000 people.) </p>

<p> I did most of this work in Spyder, and the scripts reflect this choice. I translated some of the more interesting programs to jupyter notebooks.</p>

<h2> Model Details </h2>

<h3> Feature Selection <h3>
 <p> The features used to predict each health issue rate are selected by running linear regressions to see how much each feature contributed. I additionally removed environmental features that intuitively should not predict the health issue in question.  The table below gives the environmental features used for each health issue. </p>

<table style="width:100%" border="1">
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
    <td>population density, expected commute time, safety</td>
 
  </tr>
  <tr>
    <td>good night's sleep</td>
    <td>population density, expected commute time</td>
  </tr>
 
</table>


<h3> Smoothing and linear regressions<h3>
<p> Health issue rates for a neighborhood depend on factors well beyond basic environmental features of the neighborhood. However, environmental features do affect health issue rates, as well-noted in the public health literature.  To account for the many confounding factors, I replace the health issue rate for a given neighborhood with an average health issue rate for similar neighborhoods, via K-nearest Neighbors. This average health issue rate I call the <b>smoothed</b> rate. The details for each health issue rate follow </p>

<ul>
<li><b>non-asthma rate:</b> For a given neighborhood, the smoothed  rate is the average non-asthma rate for the 300 neighborhoods with most similar population density.  </li>

<li><b>non-obesity rate:</b> For a given neighborhood, the smoothed rate is the average non-obesity rate for the 900 neighborhoods with most similar population density, expected commute time, and safety.  </li>

<li><b>percentage reporting a good night's sleep:</b> For a given neighborhood, the smoothed rate is the average percentage reporting a good night's sleep for the 500 neighborhoods with most similar population density and expected commute time.  </li>

</ul>

<p>The number of neighbors to use in the smoothing process is determined by trying to optimize for R2 while avoiding overfitting. The script visualization/R2-plotter.py graphs the number of neighbors used in the smoothing vs the R2 value. The function health_smoothing in the aforementioned script produces the column of smoothed values.</p>

<p> After smoothing, the following linear regressions are run:</p>
<ul>
<li>population density vs smoothed non-asthma rate </li>

<li>population density, expected commute time, and safety vs smoothed non-obesity rate.  </li>

<li>population density and expected commute time vs smoothed percentage reporting a good night's sleep </li>

</ul>
<p> These regressions are run via model.py. This script outputs the details of these regressions in report/regression-parameters-model1-final-param.txt. This program also outputs data/weights.csv which contains the coefficients and intercepts to be used by the webapp.</p>

<h3> Evaluation<h3>

<h3> HealthScore computation and the webapp</h3>
 
 <h3> Data and Preprocessing </h3>
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

 
 
 <h4> Health data</h4>
The health data is taken from the CDC's  2018 <a href="https://www.cdc.gov/500cities/index.htm">500 Cities Project</a>. This data set has detailed health information on the census tract level for the 500 largest cities in the US. This data set covers approximately 26,000 census tracts. The data set can be downloaded as a csv <a href="https://catalog.data.gov/dataset/500-cities-local-data-for-better-health-fc759">here</a>. Due to the large size of this file, the raw data is not contained in the repo. The script which cleans the raw data is cleaning-tools/clean-500-cities.py


<h4>Environmental data</h4>
The environmental data covers all census tracts and comes from four sources.
<ol>
  <li><p> <b>FBI Uniform Crime Reporting:</b> This data set gives county level information on crime from 2016. In the present repo, these data are located at data/raw/all-tracts/crime_data_w_population_and_crime_rate.csv. The data may be found online <a href="https://www.kaggle.com/mikejohnsonjr/united-states-crime-rates-by-county">here </a>.</p>
    <p> This data set is used to obtain crime rates for every county in the US. Some minor cleaning is necessary, and this is done in merging-tools/merge-all-tracts.py. This data set is somewhat unsatisfactory as it is not at the census tract level.</p>
  </li>
  
  <li> <p><b> US Census Geographic Data: </b> This geodatabase gives geographic data for census tracts. The database is too large to include in this repo. The raw data may be found <a href="https://www2.census.gov/geo/tiger/TGRGDB16/" >here</a>; the file name is tlgdb_2016_a_us_substategeo.gdb. </p>
  <p> This data set is used to obtain latitude and longitude, land area, and census tract code for every census tract in the US. The script cleaning-tools/area-importer.py extracts this information from the geodatabase. </p> </li>

 <li><p><b> 2016 US Census American Communities Survey:</b> This database gives detailed information on each census tracts. This data set is large and best accessed via the census API. For more details on this data set see <a href="https://www.census.gov/programs-surveys/acs">here</a></p>
    <p> This data set is used to obtain expected commute time. The script cleaning-tools/census-data-importer.py downloads the relevant information via the python library <a href="https://pypi.org/project/CensusData/">censusdata</a>. The script additionally requires the state codes used by the census. These codes are located in data/raw/all-tracts/state-geocodes-v2016.csv.</p>
    
 <li><p><b> 2010 US Census Summery File 1:</b> This database contains the data compiled by the 2010 census. This data set is large and best accessed via the census API. For more details on this data set see <a href="https://www.census.gov/data/datasets/2010/dec/summary-file-1.html">here</a></p>
    <p> This data set is used to obtain census tract population. The script cleaning-tools/census-data-importer.py accesses and downloads the relevant information via the python library requests. An API key is needed to access this file. One can obtain a key <a href="https://api.census.gov/data/key_signup.html">here</a>. </p></li>
      
    
</ol>



 

<h2> Future Improvements </h2>
