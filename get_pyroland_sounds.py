import json
from tree_type import *

def load_json(fp):
    with open(fp) as f:
        return json.load(f)

# Sounds that are replaced with laughter in pyroland
#   Info taken from tf_gamerules.cpp
pl_lines = load_json("pyroland_line_replacements.json")
responserules = load_json("data/responserules.json")
rules = responserules["rules"]
responses = responserules["responses"]
taunts = load_json("data/taunts.json")
scenes = load_json("data/scenes.json")
events = load_json("data/events.json")

backslash_taunt_events = [
    "taunt_yetipunch_soldier_scream",
    "soldier.scardy_cat",
    "demo.scardy_cat",
    "medic.scardy_cat",
    "heavy.scardy_cat",
    "pyro.scardy_cat",
    "spy.scardy_cat",
    "engineer.scardy_cat",
]

data = TreeNode("Pyroland Taunt Line Replacements")
for taunt,taunt_scene_list in taunts.items():
    taunt_data = TreeNode(taunt)
    data.addChild(taunt_data)
    for scene in taunt_scene_list:
        if scene in scenes:
            scene_data = TreeNode(scene)
            taunt_data.addChild(scene_data)

            for event in scenes[scene]:
                if event in events:
                    event_data = TreeNode(event)
                    scene_data.addChild(event_data)

                    unchanged = True if event in backslash_taunt_events else False

                    for sound in events[event]:
                        vo_sound = sound.replace("sound/","")
                        if vo_sound in pl_lines:
                            line = sound
                            if unchanged:
                                line += " - UNCHANGED"
                            else:
                                line += " -> " + pl_lines[vo_sound]
                            sound_data = TreeLeaf(line)
                            event_data.addChild(sound_data)

for rule_name, rule_data in rules.items():
    if "ConceptPlayerTaunt" in rule_data["criteria"]:
        weapon_criterion = "Unknown"
        for c in rule_data["criteria"]:
            if c.startswith("WeaponIs") and not c.startswith("WeaponIsNot"):
                weapon_criterion = c
                break
            elif "FrankenHeavy" in c:
                weapon_criterion = c
                break

        for response in rule_data["responses"]:
            response_data = TreeNode("Weapon Taunt: " + weapon_criterion)
            data.addChild(response_data)

            for scene in responses[response]:
                if scene in scenes:
                    scene_data = TreeNode(scene)
                    response_data.addChild(scene_data)

                    for event in scenes[scene]:
                        if event in events:
                            event_data = TreeNode(event)
                            scene_data.addChild(event_data)

                            unchanged = True if event in backslash_taunt_events else False

                            for sound in events[event]:
                                vo_sound = sound.replace("sound/","")
                                if vo_sound in pl_lines:
                                    line = sound
                                    if unchanged:
                                        line += " - UNCHANGED"
                                    else:
                                        line += " -> " + pl_lines[vo_sound]
                                    sound_data = TreeLeaf(line)
                                    event_data.addChild(sound_data)

data.children.sort(key = lambda x: x.name)
data.prune()
data.print()
