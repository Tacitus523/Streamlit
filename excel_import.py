import pandas as pd
import json
from datetime import datetime

def import_wfk_data_from_excel(excel_dateipfad, datenbank):
    #Funktion um ein Dictionary mit mehreren Messungen in eine Liste mit einzelnen Messungen aufzuteilen
    def dict_splitter(gemeinsames_dict):
        dict_liste=[]
        eintrag={}
        index = 0
        for messungsteil in gemeinsames_dict:
            if len(messungsteil.split("."))==1:
                eintrag[messungsteil]=gemeinsames_dict[messungsteil]
            elif messungsteil.split(".")[-1]==str(index):
                eintrag[messungsteil.split(".")[0]]=gemeinsames_dict[messungsteil]
            else:
                index+=1
                dict_liste.append(eintrag)
                eintrag={}
                eintrag[messungsteil.split(".")[0]]=gemeinsames_dict[messungsteil]
        dict_liste.append(eintrag)

        return dict_liste

    #Haupt-Dataframe mit Multiindex laden
    df = pd.read_excel(excel_dateipfad, sheet_name="Export", header=[0,1], engine="openpyxl")

    #Drei Unter-Dataframes ohne überflüssige Werte abteilen
    try:
        details = df["Details"].dropna(axis=0,how="all").dropna(axis=1,how="all")
        kalibrierungen = df["Kalibrierung"].dropna(axis=0,how="all").dropna(axis=1,how="all")
        messungen = df["Messung"].dropna(axis=0,how="all").dropna(axis=1,how="all")
    except Exception as e:
        print("Import failed:", e)
        return False
    
    if len(details) == 0 or len(kalibrierungen) == 0 or len(messungen) == 0:
        print("Import field missing")
        return False

    #Datentyp der Maskierung korrigieren
    try:
        for spalte in messungen.columns:
            if "Maskieren" in "".join(spalte):
                messungen[spalte]=messungen[spalte].astype('bool')
    except Exception as e:
        print("Masking failed:", e)
        return datenbank
    
    #Drei Unter-Dataframes in geeignet formatierte Dictionaries verarbeiten
    details_bib = dict((x,y) for x,y in details.to_dict(orient="split")["data"])
    kalibrierungen_bib = dict_splitter(kalibrierungen.to_dict(orient="list"))
    messungen_bib = dict_splitter(messungen.to_dict(orient="list"))

    #Datentyp des Datum für das spätere Speichern im json-Format ändern
    for eintrag in details_bib:
        if isinstance(details_bib[eintrag], (datetime, pd.Timestamp)):
            details_bib[eintrag] = details_bib[eintrag].strftime('%d.%m.%Y')

    #Blindwerte und Aliquote als einzelne Werte aus der Liste lesen
    for messung in messungen_bib:
        for messungsteil in messung:
            if "Blindwert" in messungsteil or "Aliquot" in messungsteil:
                messung[messungsteil] = messung[messungsteil][0]

    #Neuen Eintrag vorbereiten
    produktname = details_bib["Produktname"]
    eintrag = {
        "Details": details_bib,
        "Kalibrierungen": kalibrierungen_bib,
        "Messungen": messungen_bib
    }

    #Neuen Eintrag überprüfen und eintragen
    if not produktname in datenbank:
        datenbank[produktname] = [eintrag]
    else:
        if eintrag in datenbank[produktname]:
            return False
        else:
            datenbank[produktname].append(eintrag)
    return True

def prepare_download(database_dict):
    #Datentyp des Datums für das Speichern im json-Format ändern
    for cleaner_entry in database_dict:
        cleaner_datasets = database_dict[cleaner_entry]
        for dataset in cleaner_datasets:
            detail_entries = dataset.get("Details")
            for detail_entry in detail_entries:
                if isinstance(detail_entries[detail_entry], (datetime, pd.Timestamp)):
                    detail_entries[detail_entry] = detail_entries[detail_entry].strftime('%d.%m.%Y')
    return json.dumps(database_dict, indent=2)

#Validierung Kalibrierung
def validation_calibration():
    #fehlende/falsche Messwerte überprüfen, Standardwerte nachtragen
    bsa_konzentrationen=[]
    for messung in messungen:
        if not messung.get("OPA-Extinktionen"):
            raise KeyError("Für jede Messung muss eine Messreihe mit OPA-Extinktionen mit dem Namen \"OPA-Extinktionen\" angegeben werden")
        
        if not messung.get("Eigenabsorptionen"):
            raise KeyError("Für jede Messung muss eine Messreihe mit Eigenabsorptionen mit dem Namen \"Eigenabsorptionen\" angegeben werden")

        if not messung.get("BSA-Konzentrationen [µg/ml]"):
            messung["BSA-Konzentrationen"] = [500,250,125,62.5,31.3,15.6,7.8,3.9,0]

        for messreihe in messung:
            if not len(messung.get(messreihe))==len(messung.get("BSA-Konzentrationen [µg/ml]")):    
                raise ValueError("Es müssen gleich viele Extinktionen und Konzentrationen eingegeben werden")
            
            if not bsa_konzentrationen:
                bsa_konzentrationen=messung.get("BSA-Konzentrationen [µg/ml]")
            elif not bsa_konzentrationen==messung.get("BSA-Konzentrationen [µg/ml]"):
                raise ValueError("Extinktionsmesswerte müssen identischen BSA-Konzentrationen entsprechen")

#Validierungen Messungen
def validation_measurements():
    #fehlende/falsche Messwerte überprüfen, Standardwerte nachtragen
    if not reiniger_eintrag.get("Messungen"):
        raise TypeError("Es liegen keine Messungen zur Auswertung vor")

    if not reiniger_eintrag.get("Kalibrierungen"):
        raise TypeError("Es liegt keine Kalibrierung für die Auswertung vor")

    messzeiten=None
    for messung in reiniger_eintrag.get("Messungen"):
        if not messung.get("OPA-Extinktionen"):
            raise KeyError("Für jede Messung muss eine Messreihe mit OPA-Extinktionen mit dem Namen \"OPA-Extinktionen\" angegeben werden")
        
        if not messung.get("Eigenabsorptionen"):
            raise KeyError("Für jede Messung muss eine Messreihe mit Eigenabsorptionen mit dem Namen \"Eigenabsorptionen\" angegeben werden")

        if not messung.get("Aliquot"):
            raise KeyError("Für jede Messung muss eine Messreihe ein Aliquot mit dem Namen \"Aliquot\" angegeben werden")
        elif not isinstance(messung.get("Aliquot"),(int,float)):
            raise ValueError("Aliquot muss eine Zahl sein")

        if not messung.get("Reinigungszeit [min]"):
            messung["Reinigungszeit [min]"] = [0,5,10,20,30]

        if not messung.get("Verdünnungsfaktoren"):
            messung["Verdünnungsfaktoren"] = [1] * len(messung.get("OPA-Extinktionen"))

        if not messung.get("Maske"):
            messung["Maske"] = [False] * len(messung.get("OPA-Extinktionen"))

        if not len(messung.get("OPA-Extinktionen"))==len(messung.get("Eigenabsorptionen")):    
            raise ValueError("Es müssen gleich viele OPA-Extinktionen und Eigenabsorptionen angegeben werden")
        
        if not messzeiten:
            messzeiten=messung.get("Reinigungszeit [min]").copy()
        elif not messzeiten==messung.get("Reinigungszeit [min]"):
            raise ValueError("Extinktionsmesswerte müssen identischen Zeitenpunkten entsprechen")

        if not len(messung.get("OPA-Extinktionen"))==len(messung.get("Reinigungszeit [min]")):    
            raise ValueError("Es müssen gleich viele Extinktionensmesswerte und Zeitpunkte angegeben werden")
    
        if not (messung.get("Eigenabsorptions-Blindwert") and messung.get("OPA-Blindwert")):
            raise ValueError("Es müssen Blindwerte für OPA-Extinktionen und Eigenabsorption angegeben werden")