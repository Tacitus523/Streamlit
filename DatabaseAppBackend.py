import json
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

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
    unique_names = pd.Series(detail_df["Produktname"].unique(), name = "Produktname")
    unique_names.sort_values(inplace=True)
    return unique_names

def retrieve_query_result(database_dict, product_search):
    query_result = database_dict.get(product_search)
    return query_result

def retrieve_query_details(query_result):
    if query_result is None:
        return None
    detail_data = [pd.DataFrame(query_result[i].get("Details"),index=[i]) for i in range(len(query_result))]
    detail_df = pd.concat(detail_data)
    return detail_df

def retrieve_calibrations(query_entry):
    #Validierung?
    messungen = query_entry.get("Kalibrierungen")
    bsa_konzentrationen = messungen[0].get("BSA-Konzentrationen [µg/ml]").copy()
        
    #Messreihen trennen
    opa_extinktionen = np.array([messung.get("OPA-Extinktionen") for messung in messungen])
    eigenabsorption_extinktionen = np.array([messung.get("Eigenabsorptionen") for messung in messungen])
    
    #OPA-Messwerte mitteln
    opa_extinktionen_mittelwert = np.mean(opa_extinktionen,axis=0)

    #Eigenabsorption mitteln
    eigenabsorption_extinktionen_mittelwert = np.mean(eigenabsorption_extinktionen,axis=0)
    
    calibration_data = pd.DataFrame({"BSA-Konzentration [µg/ml]": bsa_konzentrationen,
                                     "OPA-Extinktion": opa_extinktionen_mittelwert,
                                     "Eigenabsorption": eigenabsorption_extinktionen_mittelwert})

    return calibration_data

def calculate_calibrations(bsa_konzentrationen, opa_extinktionen_mittelwert, eigenabsorption_extinktionen_mittelwert):
    #Blindwerte festlegen
    opa_blindwert_mittelwert = opa_extinktionen_mittelwert[-1]
    eigenabsorption_blindwert_mittelwert = eigenabsorption_extinktionen_mittelwert[-1]

    #absolute Extinktionen berechnen
    absolute_extinktionen = (opa_extinktionen_mittelwert-opa_blindwert_mittelwert)-(eigenabsorption_extinktionen_mittelwert-eigenabsorption_blindwert_mittelwert)

    #Format für lineare Regression vorbereiten
    bsa_konzentrationen_array = np.array(bsa_konzentrationen).reshape(-1, 1).astype(np.float32)
    
    #lineare Regression
    ausgleichsgerade = LinearRegression(fit_intercept=False).fit(bsa_konzentrationen_array, absolute_extinktionen)
    steigung = ausgleichsgerade.coef_[0]
    ordinate = ausgleichsgerade.intercept_
    r_wert = ausgleichsgerade.score(bsa_konzentrationen_array, absolute_extinktionen)

    #if grafik:
    #    grafik_kalibrierung(bsa_konzentrationen,absolute_extinktionen,steigung,ordinate,r_wert)

    return steigung, ordinate, r_wert

