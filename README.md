<h2>HealthyHome: Find a healthy place to live in your city</h2>

<h3> NOTE: I am in the process of updating this repo. It will be completed by July 7 2019 </h3>

<h2> Summary </h2>

<p>I built this project as a Health Data Science Fellow at <a href="https://www.insighthealthdata.com/"> Insight</a> during the Summer 2019 session. The output of the project is the webapp <a href="http://philwesolek.com/"> HealthyHome </a> which helps renters and homebuyers compare properties by how environmental features of a neighborhood (commute time, population density, and safety) affect health  (weight, asthma, and sleep time).</p>

<p> The webapp is built using flask and hosted on Amazon Web Services. The underlying data is from 2010 or later and has a census tract level of granularity. (<a href="https://en.wikipedia.org/wiki/Census_tract">Census tracts</a> are geographic units for the US Census Bureau which are roughly equivalent to a neighborhood; they contain an average of 4,000 people. )</p>

<p> I did most of this work in the (somewhat) outmoded Spyder. The scripts reflect this choice. I translated some of the more interesting scripts to jupyter notebooks.</p>

<h2> Model Details </h2>

<h3> Feature Selection <h3>

<h3> Smoothing <h3>

<h3> Tuning and Linear Regressions </h3>

<h3> Evaluation<h3>
 
 <h3> Data and Preprocessing </h3>
 <h4>Preprocessing</h4>
<p>The processed data consists of three files: data/normalized-environmental.csv, data/normalized-health-and-environmental-train.csv, and data/normalized-health-and-environmental-test.csv. The processing steps are as follows:</p>
<ul>
<li><p> Compute population density</p></li>
<li><p> Take log of population density, as it is log-normally distributed.</p></li>
<li><p> Compute expected commute time. <p></li>
<li> <p> Turn health issue rates into non-occurrence rates. For instance, percent obesity becomes percent non-obesity. </p></li>
<li> <p>Turn crime rate into safety rate. </p></li>
<li> <p> 50-50 test-train split for merged health and enironmental data.<p> </li>
<li> <p>Make safety rate and population rate into T-scores. </p> </li>
</ul>
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
