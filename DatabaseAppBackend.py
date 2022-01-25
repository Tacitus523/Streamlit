import json
import pandas as pd
from collections import namedtuple

def load_database(uploaded_database):
    #Verification?
    database_dict = json.load(uploaded_database)
    return database_dict
    
def retrieve_database_details(database_dict):
    detail_data = [pd.DataFrame(database_dict[product][i].get("Details"),index=[i]) for product in database_dict for i in range(len(database_dict[product]))]
    detail_df = pd.concat(detail_data)
    return detail_df

def retrieve_unique_names(database_dict):
    detail_df = retrieve_database_details(database_dict)
    unique_names = pd.DataFrame(detail_df["Produktname"].unique(),columns = ["Produktname"])
    return unique_names

def retrieve_query_result(database_dict, product_search):
    query_result = database_dict.get(product_search)
    if query_result is None:
        return None
    detail_data = [pd.DataFrame(query_result[i].get("Details"),index=[i]) for i in range(len(query_result))]
    detail_df = pd.concat(detail_data)
    return detail_df

def unpack_json(json_file, cleaner_name):
    overall_data = json.load(json_file)
    cleaner_data = overall_data.get(cleaner_name)
    if cleaner_data is None:
        return None
    details = []
    calibrations = []
    measurements = []
    for measurement_set in cleaner_data:
        details.append(measurement_set.get("Details"))
        calibrations.append(measurement_set.get("Kalibrierungen"))
        measurements.append(measurement_set.get("Messungen"))
    return details, calibrations, measurements