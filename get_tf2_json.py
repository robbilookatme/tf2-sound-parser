import os, json, pathlib
import parse_vcds, parse_soundscripts, parse_rule_response, parse_transcripts, parse_item_schema, parse_bsps

data_funcs = {
    "transcripts" : lambda a, force_renew_transcripts:
        parse_transcripts.get_transcripts(force_renew_transcripts),
    "scenes" : lambda a,b : parse_vcds.get_vcds(),
    "events" : lambda a,b : parse_soundscripts.get_soundscripts(),
    "responserules" : lambda a,b : parse_rule_response.get_responserules(),
    "taunts" : lambda a,b : parse_item_schema.get_item_schema(),
    "bsp_sounds" : lambda a,b : parse_bsps.get_bsp_sounds(),
}

def get_data(name, func, force_renew_data, force_renew_transcripts):
    filename = "data/" + name + ".json"
    data = None
    try:
        if force_renew_data:
            raise Exception()
        with open(filename) as f:
            data = json.load(f)
            if len(data) == 0:
                raise Exception()
            print("Loaded data from", filename)
    except:
        if force_renew_data:
            print("Force renew flag enabled for " + filename + ", recreating...")
        else:
            print("Failed to load data from " + filename + ", recreating...")
        data = func(force_renew_data, force_renew_transcripts)
        with open(filename, "w") as f:
            json.dump(data, f, indent = 4)

    return data

def get_tf2_json(force_renew_data, force_renew_transcripts):
    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)
    data = {}
    for name, func in data_funcs.items():
        data[name] = get_data(name, func, force_renew_data, force_renew_transcripts)
    return data

if __name__ == "__main__":
    get_tf2_json(True, True)
