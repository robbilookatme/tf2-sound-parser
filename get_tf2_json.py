import os, json, pathlib
import parse_vcds, parse_soundscripts, parse_rule_response, parse_transcripts, parse_item_schema, parse_bsps

data_funcs = {
    "transcripts" : parse_transcripts.get_transcripts,
    "scenes" : parse_vcds.get_vcds,
    "events" : parse_soundscripts.get_soundscripts,
    "responserules" : parse_rule_response.get_responserules,
    "taunts" : parse_item_schema.get_item_schema,
    "bsp_sounds" : parse_bsps.get_bsp_sounds,
}

def get_data(name, func):
    filename = "data/" + name + ".json"
    data = None
    try:
        with open(filename) as f:
            data = json.load(f)
            print("Loaded data from", filename)
    except:
        print("Failed to load data from " + filename + ", recreating...")
        data = func()
        with open(filename, "w") as f:
            json.dump(data, f, indent = 4)

    return data

def get_tf2_json():
    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)
    data = {}
    for name, func in data_funcs.items():
        data[name] = get_data(name, func)
    return data

if __name__ == "__main__":
    get_tf2_json()
