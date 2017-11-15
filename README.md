# course-2017-fal-proj

This repository pertains to CS591 - Fall 2017 taught by Andrei lapets.
**This project description will be updated as we continue work on the infrastructure.**

## Narrative:
```
    The purpose of our project was to gather data on overweight persons in the Boston city area,
    and calculate whether or not there exists a correlation between income/property values and 
    the number of overweight peoplein then vicinity. Furthermore, we gathered data on the 
    location of current winter food markets and data on failed health inspections and their 
    corresponding locations. This allows us to map/plot the locations thathave poor health 
    standards and access to safe/healthy food. These two data points allow us to make a 
    constrained decision of the optimal location of health food stores. Our findings are 
    constrained to just the Zipcodes that are registered with the city of Boston (I.E Brookline 
    is not included in our findings). Our data points are further constrained to just landmass, 
    as optimal locations could indicate a non-viable placement for a store/restaurant.
    
    Part II:
    
    For part II of the project to apply constraints, we first added constraints of the location
    of each obese person to the market was limited to a distance of under 1 mile. The second 
    constraint we used first required that we limit the shapefile of the Boston Area to just 
    land mass (Couldn't remove ponds and lakes/rivers). We then calculated the optimal locations
    of health food markets and if they were not in the shapefile, then they were adjusted to be
    within the location constraints of the shapefile. Our findings indicated that there is a need
    for more healthy foods in the areas of Dorchester/Roxbury (Some market locations were hilariously
    placed around KFC/McDonalds/Taco Bell and other fast food stores). The data also indicated that 
    there was less of a need for Healthy food stores in the financial district and the Allston - 
    Brighton areas. This is conclusive with our findings of the correlation between income
    and obesity. 
        Our second constraint was to find the correlation of obesity and property values, 
    with a subset that allows us to compute the correlation coefficient between the neighborhoods
    in the shapefile and the overweight individual/property values from our other datasets. This 
    data allowed us to conclude that HuntingAve/Prudential Center, Bay Village Neighborhood, Fenway 
    Neighborhood, Government Center and Central Artery had no major correlation between
    obesity and property value, while Charleston, and the South End districs had a significant,
    measurable correlation between the two metrics.
```

## Note:
   ```
   setOptimalHealthMarkets.py is an extension of setObesityMarkets.py, in order to satisfy the 
   constraint satisfaction and optimization sections of project II. The dataset generated by
   setObesityMarkets.py will end with keyword "OLD" to indicate that the set is deprecated.
   
   It is important to note that the dataset that we used to generate the correlation coefficient
   between obesity and income was not extensive enough to compute an accurate depiction for
   all the neighborhoods. However, there were some neighborhoods that were overrepresented in
   the dataset, and yielded a correlation that is measurable and accurate.
   ```



## Data Sets:

1. #### getHealthInspections.py 
```
    Retrieves data about HealthInspections from data.boston.gov and deposits the data in an instance of MongoDB.
```
2. #### getObesityData.py 
```
    Retrieves 16000 data points regarding obesity statistics from the CDC website.
    This is then added to the instance of MongoDB for further manipulation downstream.
```
3. #### getOrganicPrices.py 
```
    Retrieves data of the average price for particular food items
    during the 12 months of the year. This data is not used downstream.
```
4. #### getPropertyValues.py 
```
    Retrieves data on different types of buildings/homes in boston as well
    as other descriptors of value from data.boston.gov. This data is used
    downstream for a correlation between obesitry and income.
```
5. #### getWinterMarkets.py
```
    Retrieves data on the location of seasonal markets in the boston area from data.cityofboston.gov.
    This data is deposited into the MongoDB instance and is used downstream to calculate the distance 
    of optimal placements of markets based on obesity statistics.
```
6. #### getZipCodeData.py
```
    Retrieves a mapping object of the zipcodes in Boston to their respective districts 
    and town names. This is used downstream as a metric of joining some datapoint 
    fields based on ZipCodes.
```
7. #### setHealthPropertyZip
```
    Retrieves the data generated by getHealthInspections.py, getPropertyValues.py, 
    and getZipCodeData.py and runs multiple aggregations, projections, selections, 
    and transformations on the data to properly format the data to place back in mongoDB.
```
8. #### setObesityMarkets.py 
```
    Retrieves the data generated by getObesityData.py and getWinterMarkets
    and runs K means to determine the optimal location for Winter Health Markets.
```
9. #### getBostonZoning.py
```
    Retrieves a GeoJson of the landmass of the Greater Boston and area and deposits
    it in MongoDb.
```

10. #### setObesityPropertyCorrelation.py
```
    Reads the datasets on Obesity and Property Values and first maps each overweight 
    person to the properties around them. The amount of overweight individuals to each 
    property is then condensed into ranges (incremented by 100,000). This bucked data is 
    then used to calculate the correlation coefficient of obesity to property values and 
    the output is loaded into MongoDB. Our findings showed the expected results, that there 
    are more overweight people in areas with lower property values.
```

11. #### setOptimalHealthMarkets.py
```
    Runs k-means to determine the optimal locations for Health Food stores in the Boston
    area based off of the location of overweight individuals in the Boston Area. 
    Constraints are also applied from a shapeFile that is limited to the Boston
    Area landmass.
```
## Instructions:
```
    -  In order to run the code:
        - run mongodb via the "mongod" command (May need SuperUser Permissions)
        - run "mongo reset.js" and "mongo setup.js"
        - run "python3 execute.py biel_otis" to execute the code
        - The code may take up to 10 minutes to run and produce a provenance diagram
```

## Requirements:
```
    - Multiple Python libraries are required for this project:
        - geopy (pip install geopy)
        - shapely (pip install shapely)
        - sklearn (pip install sklearn)
        - scipy (pip install scipy)
        - dml (pip install dml)
        - prov (pip install prov)
```

#### James Otis and Max Biel (2017)
