import json

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


    