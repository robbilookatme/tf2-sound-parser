import json, pathlib, csv
import get_tf2_json
from tf2_data_parse_types import *
from tf2_parser_config import *

def tf2_data_parse(force_renew_data, force_renew_transcripts):
    data = get_tf2_json.get_tf2_json(force_renew_data, force_renew_transcripts)

    data_rules = data["responserules"]["rules"]
    data_responses = data["responserules"]["responses"]
    data_scenes = data["scenes"]
    data_events = data["events"]
    data_transcripts = data["transcripts"]
    data_taunts = data["taunts"]
    data_bsp_sounds = data["bsp_sounds"]

    print("All data loaded!")

    # Get all the audio files from the actual TF2 sound directory
    print("Loading audio files...")
    audio_files = {}
    tf2_sound_misc_dir = vpk.open(tf2_sound_misc_dir_path)
    tf2_sound_vo_english_dir = vpk.open(tf2_sound_vo_english_dir_path)

    def add_audio_file_to_dict(file):
        file = file.lower()
        if (".mp3" in file or ".wav" in file) and file not in audio_files:
            af = AudioFile(file)
            audio_files[af] = af
            if af.base_name in data_transcripts:
                af.transcript = data_transcripts[af.base_name]["transcript"]
            # Print lines with missing transcripts
            elif False and "vo/" in file and "mvm/" not in file:
                print("No transcript for line:", af.base_name)
            return af
        return None

    for file in tf2_sound_vo_english_dir:
        add_audio_file_to_dict(file)

    for file in tf2_sound_misc_dir:
        add_audio_file_to_dict(file)

    for bsp, sound_list in data_bsp_sounds.items():
        for sound in sound_list:
            af = add_audio_file_to_dict(sound)
            if af != None:
                # assume map audio files are used
                af.state = FileState.USED
                
                # make sure to match map specific sound files first,
                #   so they aren't caught by other matchers
                grouped_output_paths["map_misc"].append(sound)

    print("Processing events...")
    # Iterate over every event, add to audio files
    events = {}
    for event_name, event_audio_list in data_events.items():
        event = Event(event_name, event_audio_list)
        for event_audio_file in event_audio_list:
            audio_file = None
            if event_audio_file in audio_files:
                audio_file = audio_files[event_audio_file]
                audio_file.state = FileState.USED
            else:
                audio_file = AudioFile(event_audio_file)
                audio_files[audio_file] = audio_file
                audio_file.state = FileState.MISSING
            
            if event not in audio_file.events:
                audio_file.events.append(event)
        events[event] = event

    print("Processing scenes...")
    # Iterate over every scene, add to events
    scenes = {}
    for scene_name, scene_event_list in data_scenes.items():
        scene = Scene(scene_name, scene_event_list)
        scene.missing = False
        for scene_event in scene_event_list:
            event = None
            if scene_event in events:
                event = events[scene_event]
                event.state = FileState.USED
            else:
                event = Event(scene_event)
                events[event] = event
                event.state = FileState.MISSING

            if scene not in event.scenes:
                event.scenes.append(scene)
        scenes[scene] = scene

    print("Processing responses...")
    # Iterate over every response, add to scenes
    responses = {}
    for response_name, response_scene_list in data_responses.items():
        response = Response(response_name, response_scene_list)
        response.missing = False
        for response_scene in response_scene_list:
            scene = None
            if response_scene in scenes:
                scene = scenes[response_scene]
                scene.state = FileState.USED
            else:
                scene = Scene(response_scene)
                scenes[scene] = scene
                scene.state = FileState.MISSING

            if response not in scene.responses:
                scene.responses.append(response)
        responses[response] = response

    print("Processing taunts...")
    # Iterate over taunts
    #  Using response list for taunts because I'm a hack fraud
    for taunt_name, taunt_scene_list in data_taunts.items():
        taunt = Response(taunt_name, taunt_scene_list)
        taunt.missing = False
        for taunt_scene in taunt_scene_list:
            scene = None
            if taunt_scene in scenes:
                scene = scenes[taunt_scene]
                scene.state = FileState.USED
            else:
                scene = Scene(taunt_scene)
                scenes[scene] = scene
                scene.state = FileState.MISSING

            if taunt not in scene.responses:
                scene.responses.append(taunt)
        responses[taunt] = taunt

    print("Processing rules...")
    # Iterate over every rule, add to responses
    rules = {}
    for rule_name, rule_data in data_rules.items():
        rule_response_list = rule_data["responses"]
        rule_criteria = rule_data["criteria"]
        rule_contexts = rule_data["contexts"]
        rule_applycontexttoworld = rule_data["applycontexttoworld"]
        rule = Rule(rule_name, rule_criteria, rule_response_list, rule_contexts, rule_applycontexttoworld)
        rule.missing = False
        for rule_response in rule_response_list:
            response = None
            if rule_response in responses:
                response = responses[rule_response]
                response.state = FileState.USED
            else:
                response = Response(rule_response)
                responses[response] = response
                response.state = FileState.MISSING
            
            if rule not in response.rules:
                response.rules.append(rule)
        rules[rule] = rule

    print("Producing output...")
    # Iterate over output filenames, generate csv and json for each
    for filename, file_match_list in grouped_output_paths.items():
        remaining = {}
        output = {}
        for audio_file in audio_files:
            matched = False
            for match_string in file_match_list:
                if match_string in audio_file.name:
                    matched = True
                    break

            if matched:
                output[audio_file] = audio_file
            else:
                remaining[audio_file] = audio_file
        
        if len(output) > 0:
            json_out = {}
            for af in output:
                af_json = {}
                af_json["base_name"] = af.base_name
                af_json["transcript"] = af.transcript
                af_json["state"] = af.state.value

                out_events = af.events
                out_events_json = []
                out_scenes = []
                for event in out_events:
                    out_events_json.append(event.name)
                    out_scenes += event.scenes
                
                out_scenes_json = []
                out_responses = []
                for scene in out_scenes:
                    out_scenes_json.append(scene.name)
                    out_responses += scene.responses

                out_responses_json = []
                out_rules = []
                for response in out_responses:
                    out_responses_json.append(response.name)
                    out_rules += response.rules

                out_rules_json = []
                out_criteria = []
                for rule in out_rules:
                    out_rules_json.append(rule.name)
                    out_rule_criteria = rule.criteria + []
                    to_world = rule.applycontexttoworld
                    context_str = "AppliesContextToWorld:" if to_world else "AppliesContext:"
                    for c in rule.contexts:
                        out_rule_criteria.append(context_str + c)
                    out_criteria.append(out_rule_criteria)

                af_json["events"] = sorted(list(set(out_events_json)))
                af_json["scenes"] = sorted(list(set(out_scenes_json)))
                af_json["responses"] = sorted(list(set(out_responses_json)))
                af_json["rules"] = sorted(list(set(out_rules_json)))
                af_json["criteria"] = sorted(out_criteria)
                
                json_out[af.name] = af_json

            pathlib.Path("output/json/").mkdir(parents=True, exist_ok=True)
            with open("output/json/" + filename + ".json", "w") as f:
                print("writing to", filename + ".json...")
                json.dump(json_out, f, indent = 4, sort_keys=True)

            pathlib.Path("output/csv/").mkdir(parents=True, exist_ok=True)
            with open("output/csv/" + filename + ".csv", "w") as f:
                print("writing to", filename + ".csv...")
                csv_file = csv.writer(f)

                keys = sorted(json_out.keys(), key = output_sort)
                
                for out_name in keys:
                    out_data = json_out[out_name]
                    out_state = ""
                    if out_data["state"] == FileState.MISSING.value:
                        out_state = "Missing?"
                    elif out_data["state"] == FileState.UNUSED.value:
                        out_state = "Unused?"

                    filename = out_name.split("/")[-1][:-4]
                    
                    rows = [
                        [
                            "Filename:",
                            out_data["base_name"],
                            "",
                            "Events:",
                            out_data["events"]
                        ],
                        [
                            "Full Path:",
                            out_name,
                            "",
                            "Scenes:",
                            out_data["scenes"]
                        ],
                        [
                            "Transcription:",
                            out_data["transcript"],
                            "",
                            "Responses:",
                            out_data["responses"]
                        ],
                        [
                            "Your Line:",
                            "",
                            "",
                            "Rules:",
                            out_data["rules"]
                        ],
                        [
                            out_state,
                            "",
                            "",
                            "Criteria:",
                            out_data["criteria"]
                        ],
                        []
                    ]
                    csv_file.writerows(rows)
                    

        audio_files = remaining

    if False:
        # Output number of audio files not accounted for
        print(len(audio_files), "audio files were not accounted for!")

        # List out every audio file not accounted for
        for af in audio_files:
            if af.state == FileState.MISSING:
                print("MISSING: ", end="")
            print(af.name)

if __name__ == "__main__":
    tf2_data_parse(True, True)
