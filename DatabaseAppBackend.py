import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

def load_database(uploaded_database):
    #Verification?
    database_dict = json.load(uploaded_database)
    return database_dict
    
def retrieve_database_details(database_dict):
    database_detail_data = [pd.DataFrame(database_dict[product][i].get("Details"),index=[i]) for product in database_dict for i in range(len(database_dict[product]))]
    database_detail_df = pd.concat(database_detail_data)
    return database_detail_df

def retrieve_unique_names(database_dict):
    database_detail_df = retrieve_database_details(database_dict)
    unique_names = pd.Series(database_detail_df["Produktname"].unique(), name = "Produktname")
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

def retrieve_calibration_data(measurements):
    #Validierung?
    messungen = measurements.get("Kalibrierungen")
    bsa_konzentrationen = messungen[0].get("BSA-Konzentrationen [µg/ml]").copy()
        
    #Messreihen trennen
    opa_extinktionen = np.array([messung.get("OPA-Extinktionen") for messung in messungen])
    eigenabsorption_extinktionen = np.array([messung.get("Eigenabsorptionen") for messung in messungen])
    
    #Mittelwerte aus mehreren Kalibrierungen
    opa_extinktionen_mittelwert = np.mean(opa_extinktionen, axis=0)
    eigenabsorption_extinktionen_mittelwert = np.mean(eigenabsorption_extinktionen, axis=0)
    
    calibration_data = pd.DataFrame({
        "BSA-Konzentration [µg/ml]": bsa_konzentrationen,
        "OPA-Extinktion": opa_extinktionen_mittelwert,
        "Eigenabsorption": eigenabsorption_extinktionen_mittelwert
        })

    return calibration_data

def retrieve_measurement_data(measurements):
    measurements = measurements.get("Messungen")
    reinigungszeit = np.array([measurement.get("Reinigungszeit [min]") for measurement in measurements])
    opa_extinktionen = np.array([measurement.get("OPA-Extinktionen") for measurement in measurements])
    eigenabsorption_extinktionen = np.array([measurement.get("Eigenabsorptionen") for measurement in measurements])
    opa_blindwert = [measurement.get("OPA-Blindwert") for measurement in measurements]
    eigenabsorption_blindwert = [measurement.get("Eigenabsorptions-Blindwert") for measurement in measurements]
    #aliquot = np.array([measurement.get("Aliquot") for measurement in measurements])
    #verdünnungsfaktoren = np.array([measurement.get("Verdünnungsfaktoren") for measurement in measurements]) 

    measurement_data = pd.DataFrame({
        "Reinigungszeit [min]": reinigungszeit[0],
        "OPA-Extinktion 1": opa_extinktionen[0],
        "OPA-Extinktion 2": opa_extinktionen[1],
        "OPA-Extinktion 3": opa_extinktionen[2],
        "Eigen-absorption 1": eigenabsorption_extinktionen[0],
        "Eigen-absorption 2": eigenabsorption_extinktionen[1],
        "Eigen-absorption 3": eigenabsorption_extinktionen[2],  
        })
    return measurement_data

def calculate_calibrations(calibration_data):
    #Daten auslesen
    bsa_konzentrationen = calibration_data["BSA-Konzentration [µg/ml]"]
    opa_extinktionen_mittelwert = calibration_data["OPA-Extinktion"]
    eigenabsorption_extinktionen_mittelwert = calibration_data["Eigenabsorption"]
    
    #Blindwerte festlegen
    opa_blindwert_mittelwert = float(opa_extinktionen_mittelwert.iloc[[-1]])
    eigenabsorption_blindwert_mittelwert = float(eigenabsorption_extinktionen_mittelwert.iloc[[-1]])

    #absolute Extinktionen berechnen
    absolute_extinktionen = (opa_extinktionen_mittelwert-opa_blindwert_mittelwert)-(eigenabsorption_extinktionen_mittelwert-eigenabsorption_blindwert_mittelwert)
    
    #Format für lineare Regression vorbereiten
    bsa_konzentrationen_array = np.array(bsa_konzentrationen).reshape(-1, 1).astype(np.float32)
    
    #lineare Regression
    ausgleichsgerade = LinearRegression(fit_intercept=False).fit(bsa_konzentrationen_array, absolute_extinktionen)
    steigung = ausgleichsgerade.coef_[0]
    ordinate = ausgleichsgerade.intercept_
    r_wert = ausgleichsgerade.score(bsa_konzentrationen_array, absolute_extinktionen)

    f = calibration_figure(bsa_konzentrationen,absolute_extinktionen,steigung,ordinate,r_wert)

    return steigung, ordinate, r_wert, f

def wfk_evaluation(measurement, slope):
    def protein_content_calculation(measurement, steigung):
        #einzelne Messungen aufteilen
        opa_extinktionen = np.array(measurement.get("OPA-Extinktionen"))
        eigenabsorption_extinktionen = np.array(measurement.get("Eigenabsorptionen"))
        opa_blindwert = measurement.get("OPA-Blindwert")
        eigenabsorption_blindwert = measurement.get("Eigenabsorptions-Blindwert")
        aliquot = np.array(measurement.get("Aliquot"))
        verdünnungsfaktoren = np.array(measurement.get("Verdünnungsfaktoren"))
        
        #absolute Absorption berechnen
        absolute_extinktionen=(opa_extinktionen-opa_blindwert)-(eigenabsorption_extinktionen-eigenabsorption_blindwert)

        #Protein-Gehälter berechnen
        protein_gehälter_prüfkörper=absolute_extinktionen*verdünnungsfaktoren/steigung*aliquot

        return protein_gehälter_prüfkörper
    
    #Berechnungen für alle Messungen
    protein_gehälter=[]
    for messung in measurement.get("Messungen"):
        #Berechnung in Funktion protein_gehalt_berechnung
        protein_gehälter.append(protein_content_calculation(messung, slope))
        
    #Mittelwert, Standardabweichung und Maskierung
    protein_gehälter=np.array(protein_gehälter)
    protein_gehälter[np.array([messung.get("Maskieren") for messung in measurement.get("Messungen")])]=np.nan

    protein_gehälter_mittelwert=np.nanmean(protein_gehälter,axis=0)
    protein_gehälter_standardabweichung=np.nanstd(protein_gehälter,axis=0)

    return protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung

def calibration_figure(bsa_konzentrationen, absolute_extinktionen, steigung, ordinate, r_wert):
    ideale_extinktionen=[steigung*konzentration+ordinate for konzentration in bsa_konzentrationen]

    fig_size = (10, 5)
    f = plt.figure(figsize=fig_size)
    plt.plot(bsa_konzentrationen, absolute_extinktionen, color='blue', marker='o', linestyle='solid')
    plt.plot(bsa_konzentrationen, ideale_extinktionen, color='blue', linestyle='dotted')
    plt.title("Kalibrierung mit BSA")
    plt.xlabel("BSA-Konzentration [µg/ml]")
    plt.ylabel("Extinktion")
    plt.text(320, 0.21, "y = "+str(round(float(steigung),4))+"x + "+str(round(float(ordinate),4)))
    plt.text(320, 0.15, "R-Wert = "+str(round(float(r_wert),4)))
    plt.axis([0, max(bsa_konzentrationen)*1.02, 0, max(absolute_extinktionen)*1.1])
    plt.grid(True)
    plt.close(f)
    return f

def grafik_wfk_auswertung(reiniger_eintrag, protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung):
    messzeiten=np.array(reiniger_eintrag["Messungen"][0].get("Reinigungszeit [min]").copy())

    fig_size = (10, 5)
    f = plt.figure(figsize=fig_size)
    plt.title(f"{reiniger_eintrag.get('Details').get('Produktname')}\nZeitlicher Verlauf Proteingehalt auf PK")
    plt.xlabel("Reinigungszeit [min]")
    plt.ylabel("Proteingehalt [µg]")
    plt.grid(True)
    for reihennummer, messung in enumerate(reiniger_eintrag["Messungen"]):
        unmaskierte_messzeiten=messzeiten[~np.array(messung.get("Maskieren"))]
        unmaskierte_protein_gehälter=protein_gehälter[reihennummer][~np.array(messung.get("Maskieren"))]
        plt.plot(unmaskierte_messzeiten, unmaskierte_protein_gehälter, label=f"Messreihe {reihennummer+1}", marker='o', linestyle='dotted')
    plt.plot(messzeiten, protein_gehälter_mittelwert, label="Mittelwert", color='red', marker='o', markersize=5, linestyle='solid', linewidth=2)
    plt.errorbar(messzeiten, protein_gehälter_mittelwert, yerr=protein_gehälter_standardabweichung, color='red', elinewidth=1, capsize=2)
    plt.legend()
    plt.close(f)
    return f