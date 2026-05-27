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

def get_data(name, func, force_renew):
    filename = "data/" + name + ".json"
    data = None
    try:
        if force_renew:
            raise Exception()
        with open(filename) as f:
            data = json.load(f)
            if len(data) == 0:
                raise Exception()
            print("Loaded data from", filename)
    except:
        if force_renew:
            print("Force renew flag enabled for " + filename + ", recreating...")
        else:
            print("Failed to load data from " + filename + ", recreating...")
        data = func()
        with open(filename, "w") as f:
            json.dump(data, f, indent = 4)

    return data

def get_tf2_json(force_renew_data, force_renew_transcripts):
    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)
    data = {}
    for name, func in data_funcs.items():
        if name == "transcripts":
            force_renew = force_renew_transcripts
        else:
            force_renew = force_renew_data
        data[name] = get_data(name, func, force_renew)
    return data

if __name__ == "__main__":
    get_tf2_json(True, True)
