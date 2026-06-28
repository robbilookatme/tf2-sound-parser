# Can be set to a lowercase class name ("demoman", "engineer", etc) to only get
#  taunts for a certain class
class_name = ""

import json
from tree_type import *

def load_json(fp):
    with open(fp) as f:
        return json.load(f)

fol = "data/"
responserules = load_json(fol + "responserules.json")
rules = responserules["rules"]
responses = responserules["responses"]
taunts = load_json(fol + "taunts.json")
transcripts = load_json(fol + "transcripts.json")
scenes = load_json(fol + "scenes.json")
events = load_json(fol + "events.json")

data = TreeNode("TauntTree")

# Criteria that result in a special taunt playing
special_taunt_criteria = [
    "IsAprilFoolsTaunt",
    "IsFrankenHeavy",
    "IsRobotCostume",
    "IsDemowolf",
    "IsHalloweenTaunt"
]

for rule_name, rule_data in rules.items():
    if "ConceptPlayerTaunt" in rule_data["criteria"]:
        weapon_criterion = "Unknown"
        for c in rule_data["criteria"]:
            if c.startswith("WeaponIs") and not c.startswith("WeaponIsNot"):
                weapon_criterion = c
                break
            elif c in special_taunt_criteria:
                weapon_criterion = c
                break

        for response in rule_data["responses"]:
            response_data = TreeNode("Weapon Taunt: " + weapon_criterion)
            data.add_child(response_data)

            for scene in responses[response]:
                if scene in scenes and class_name in scene:
                    scene_data = TreeNode(scene)
                    response_data.add_child(scene_data)

                    for event in scenes[scene]:
                        if event in events:
                            event_data = TreeNode(event)
                            scene_data.add_child(event_data)

                            # Remove duplicate sounds from event
                            sound_list = events[event]
                            seen_set = set()
                            sound_list = [x for x in sound_list if not (x in seen_set or seen_set.add(x))]

                            for sound in sound_list:
                                if "sound/vo" in sound:
                                    base_sound = sound.split("/")[-1][:-4]
                                    transcript = base_sound
                                    if base_sound in transcripts:
                                        transcript += ' -> "' + transcripts[base_sound]["transcript"] + '"'
                                    event_data.add_child(TreeLeaf(transcript))

for taunt,taunt_scene_list in taunts.items():
    taunt_data = TreeNode(taunt)
    data.add_child(taunt_data)

    for scene in taunt_scene_list:
        if scene in scenes and class_name in scene:
            scene_data = TreeNode(scene)
            taunt_data.add_child(scene_data)

            for event in scenes[scene]:
                if event in events:
                    event_data = TreeNode(event)
                    scene_data.add_child(event_data)

                    # Remove duplicate sounds from event
                    sound_list = events[event]
                    seen_set = set()
                    sound_list = [x for x in sound_list if not (x in seen_set or seen_set.add(x))]
                    
                    for sound in sound_list:
                        if "sound/vo" in sound:
                            base_sound = sound.split("/")[-1][:-4]
                            transcript = base_sound
                            if base_sound in transcripts:
                                transcript += ' -> "' + transcripts[base_sound]["transcript"] + '"'
                            event_data.add_child(TreeLeaf(transcript))

data.children.sort(key=lambda x: x.name)
data.prune()
data.print()
