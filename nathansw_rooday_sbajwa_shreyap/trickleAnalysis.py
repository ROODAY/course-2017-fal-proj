import json
import time
import pprint 
import datetime
import dml
import prov.model
import uuid
import pandas as pd
import numpy as np
import seaborn as sns
from bson import ObjectId
from urllib.request import urlopen
from  itertools import combinations , combinations_with_replacement , product

import pprint

### Algorithm 2

class trickleAnalysis(dml.Algorithm):
  def return_distance(row, neighborhood_distance_matrix):
    return neighborhood_distance_matrix.loc[row.neighborhood1,row.neighborhood2]

  def cal_neighborhood_diff(x,ref_df):
    if((x['neighborhood2'] in ref_df.index) & (x['neighborhood1'] in ref_df.index)):
      return((ref_df[x['neighborhood1']] - ref_df[x['neighborhood2']] ))
    else:
      return np.nan

  def get_corr(x,correlation_col,neighborhood_pair):
    neighborhood_name = x['neighborhood']
    filtered_df = neighborhood_pair[(neighborhood_pair['neighborhood1']==neighborhood_name) & neighborhood_pair['is_neighbor']==1]
    return filtered_df['neighborhood_distance'].corr(filtered_df[correlation_col])

  contributor = 'nathansw_rooday_sbajwa_shreyap'
  ### Make sure this is the correct dataset file name
  reads = ['nathansw_rooday_sbajwa_shreyap.trickling', 'nathansw_rooday_sbajwa_shreyap.neighborhoodMap', 'nathansw_sbajwa.householdincome', 'nathansw_sbajwa.povertyrates', 'nathansw_sbajwa.commuting']
    
  # Currently it just creates a csv file 
  writes = ['nathansw_rooday_sbajwa_shreyap.trickleAnalysis']

  @staticmethod
  def execute(trial=False):
    startTime = datetime.datetime.now()
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('nathansw_rooday_sbajwa_shreyap', 'nathansw_rooday_sbajwa_shreyap')
    
    trickle_db = repo['nathansw_rooday_sbajwa_shreyap.trickling']
    neighborhoodMap_db = repo['nathansw_rooday_sbajwa_shreyap.neighborhoodMap']
    householdincome_db = repo['nathansw_sbajwa.householdincome']
    povertyrates_db = repo['nathansw_sbajwa.povertyrates']
    commuting_db = repo['nathansw_sbajwa.commuting']

    trickle_data = trickle_db.find_one()
    del trickle_data['_id']
    neighborhood_distance_matrix = pd.DataFrame.from_dict(trickle_data)
    neighborhood_distance_matrix.index = neighborhood_distance_matrix.neighborhood

    unique_neighborhood = neighborhood_distance_matrix.index.tolist()
    neighborhood_pair = pd.DataFrame(list(product(unique_neighborhood,repeat=2)))
    neighborhood_pair.columns = ['neighborhood1','neighborhood2']
    neighborhood_pair = neighborhood_pair[neighborhood_pair['neighborhood1'] != neighborhood_pair['neighborhood2']]
    neighborhood_pair['neighborhood_distance'] = neighborhood_pair.apply(trickleAnalysis.return_distance,args=(neighborhood_distance_matrix,), axis=1)

    neighborhoodMap_data = neighborhoodMap_db.find_one()
    del neighborhoodMap_data['_id']
    neighborhood = pd.DataFrame([(key, x) for key,val in neighborhoodMap_data.items() for x in val], columns=['neighborhood1', 'neighborhood1'])
    neighborhood.columns = ['neighborhood1','neighborhood2']
    neighborhood['is_neighbor']=1

    neighborhood_pair = neighborhood_pair.merge(neighborhood,left_on=['neighborhood1','neighborhood2'],right_on=['neighborhood1','neighborhood2'],how='left')#[['neighborhood1','neighborhood2','is_neighbor_y']]
    neighborhood_pair.columns = ['neighborhood1','neighborhood2','neighborhood_distance','is_neighbor']
    neighborhood_pair = neighborhood_pair.fillna(0)
    
    povertyrates_data = povertyrates_db.find_one()
    del povertyrates_data['_id']
    PovertyRates = pd.DataFrame.from_dict(povertyrates_data).transpose()
    PovertyRates.columns = 'Income_' + PovertyRates.columns
    poverty_rate = PovertyRates['Income_Poverty rate']
    poverty_rate = poverty_rate.apply(lambda x: float(x.split("%")[0]))

    neighborhood_pair['poverty_percentage_diff'] = neighborhood_pair.apply(trickleAnalysis.cal_neighborhood_diff,args=([poverty_rate]),axis=1)
    neighborhood_trickling_effect = pd.DataFrame({
      'neighborhood': unique_neighborhood
    })
    neighborhood_trickling_effect.index = neighborhood_trickling_effect.neighborhood
    correlation_col = 'poverty_percentage_diff'
    neighborhood_trickling_effect['poverty_trickling_effect'] = neighborhood_trickling_effect.apply(trickleAnalysis.get_corr, args=(['poverty_percentage_diff', neighborhood_pair]),axis=1)
    
    householdincome_data = householdincome_db.find_one()
    del householdincome_data['_id']
    HouseholdIncome = pd.DataFrame.from_dict(householdincome_data).transpose()
    HouseholdIncome.columns = 'Income_' + HouseholdIncome.columns
    median_income = HouseholdIncome['Income_Median Income']
    median_income = median_income.apply(lambda x: float(x.replace(",","").replace("$","").replace("-","0") ))
    neighborhood_pair['median_income_diff'] = neighborhood_pair.apply(trickleAnalysis.cal_neighborhood_diff,args=([median_income]),axis=1)
    neighborhood_trickling_effect['median_income_effect'] = neighborhood_trickling_effect.apply(trickleAnalysis.get_corr, args=(['median_income_diff', neighborhood_pair]),axis=1)

    commuting_data = commuting_db.find_one()
    del commuting_data['_id']
    MeansOfCommuting = pd.DataFrame.from_dict(commuting_data).transpose()
    bike_commute = MeansOfCommuting['Bicycle %']
    bike_commute = bike_commute.apply(lambda x: float(x.replace("%","")))
    neighborhood_pair['bike_commute_diff'] = neighborhood_pair.apply(trickleAnalysis.cal_neighborhood_diff,args=([bike_commute]),axis=1)
    neighborhood_trickling_effect['bike_commute_effect'] = neighborhood_trickling_effect.apply(trickleAnalysis.get_corr, args=(['bike_commute_diff', neighborhood_pair]),axis=1)

    walk_commute = MeansOfCommuting['Walked %']
    walk_commute = walk_commute.apply(lambda x: float(x.replace("%","")))
    neighborhood_pair['walk_commute_diff'] = neighborhood_pair.apply(trickleAnalysis.cal_neighborhood_diff,args=([walk_commute]),axis=1)
    neighborhood_trickling_effect['walk_commute_effect'] = neighborhood_trickling_effect.apply(trickleAnalysis.get_corr, args=(['walk_commute_diff', neighborhood_pair]),axis=1)

    bus_commute = MeansOfCommuting['Bus or trolley %']
    bus_commute = bus_commute.apply(lambda x: float(x.replace("%","")))
    neighborhood_pair['bus_commute_diff'] = neighborhood_pair.apply(trickleAnalysis.cal_neighborhood_diff,args=([bus_commute]),axis=1)
    neighborhood_trickling_effect['bus_commute_effect'] = neighborhood_trickling_effect.apply(trickleAnalysis.get_corr, args=(['bus_commute_diff', neighborhood_pair]),axis=1)

    car_commute = MeansOfCommuting['Car, truck, or van %']
    car_commute = car_commute.apply(lambda x: float(x.replace("%","")))
    neighborhood_pair['car_commute_diff'] = neighborhood_pair.apply(trickleAnalysis.cal_neighborhood_diff,args=([car_commute]),axis=1)
    neighborhood_trickling_effect['car_commute_effect'] = neighborhood_trickling_effect.apply(trickleAnalysis.get_corr, args=(['car_commute_diff', neighborhood_pair]),axis=1)

    finalTrickleData = neighborhood_trickling_effect.to_dict()    
    del finalTrickleData['neighborhood']
    
    repo.dropCollection('trickleAnalysis')
    repo.createCollection('trickleAnalysis')
    repo['nathansw_rooday_sbajwa_shreyap.trickleAnalysis'].insert_one(finalTrickleData)
    
    repo.logout()
    endTime = datetime.datetime.now()
    return {"start":startTime, "end":endTime}

  @staticmethod
  def provenance(doc = prov.model.ProvDocument(), startTime=None, endTime=None):
    client = dml.pymongo.MongoClient()
    repo = client.repo

    ##########################################################

    ## Namespaces
    doc.add_namespace('alg', 'http://datamechanics.io/algorithm/sbajwa_nathansw/') # The scripts in / format.
    doc.add_namespace('dat', 'http://datamechanics.io/data/sbajwa_nathansw/') # The data sets in / format.
    doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
    doc.add_namespace('log', 'http://datamechanics.io/log#') # The event log.


    """
    ## Agents
    this_script = doc.agent('alg:nathansw_rooday_sbajwa_shreyap#mbta_stops_lines', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

    ## Activities
    get_mbta_stops_lines = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

    ## Entitites
    # Data Source
    resource = 
    # Data Generated
    mbta_stops_lines = 
       
    ############################################################

        ## wasAssociatedWith      

    ## used   

    ## wasGeneratedBy

    ## wasAttributedTo    

    ## wasDerivedFrom

    ############################################################
    """
    repo.logout()

    return doc

trickleAnalysis.execute()