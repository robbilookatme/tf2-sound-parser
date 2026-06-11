from lark import Lark, Transformer, Discard
import os, pathlib, json
from parser_types import *
from tf2_parser_config import *

# The following files are not from game_sounds_manifest.txt
#   but are instead hardcoded into SoundEmitterSystem.cpp
engine_soundscript_files = [
    "scripts/mvm_level_sounds.txt"
    ,"scripts/mvm_level_sound_tweaks.txt"
    ,"scripts/game_sounds_vo_mvm.txt"
    ,"scripts/game_sounds_vo_mvm_mighty.txt"
]

manifest_file_path = "scripts/game_sounds_manifest.txt"

class ManifestT(Transformer):
    def start(self, children):
        return children
    def file(self, children):
        return clean_string(children[0])

manifest_lark = Lark(r'''
?start: "game_sounds_manifest" "{" file* "}"

file: "\"" ("precache_file"i | "preload_file"i) "\"" STRING

%import common.CPP_COMMENT -> COMMENT
%import common.WORD
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
%ignore COMMENT
''')
    
class SoundscriptT(Transformer):
    def _f(self, _):
        return Discard

    def start(self, children):
        return children

    def script(self,children):
        name = children[0]
        action = flatten(children[1:])
        return {"name":name, "action":action}
    def script_name(self, children):
        return clean_string(children[0]).lower()
    def wave(self, children):
        return "sound/" + clean_filename(children[0])
    def one_wave(self, children):
        return children
    def random_wave(self, children):
        return children

soundscript_lark = Lark(r'''
?start: script*

?script : script_name "{" inscript* "}"
script_name : STRING

?inscript: one_wave
|          random_wave
|          STRING STRING                -> _f

one_wave : wave
random_wave : "\"rndwave\"" platform? "{" wave+ "}"
wave : "\"wave\"" STRING platform?
platform : ("[$WIN32]" | "[$X360]") -> _f

%import common.CPP_COMMENT -> COMMENT
%import common.WORD
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
%ignore COMMENT
''')

def get_soundscripts():
    print("Parsing soundscripts...")
    scripts = []

    tf2_misc_dir_vpk = vpk.open(tf2_misc_dir_vpk_path)

    mf = tf2_misc_dir_vpk.get_file(manifest_file_path)
    fd = mf.read().decode("utf-8")
    x = manifest_lark.parse(fd)
    soundscript_files = ManifestT().transform(x)

    for file in engine_soundscript_files:
        soundscript_files.append(file)

    for file in soundscript_files:
        print(file)
        f = tf2_misc_dir_vpk.get_file(file)
        fd = f.read().decode("utf-8")
        x = soundscript_lark.parse(fd)
        y = SoundscriptT().transform(x)
        y.sort(key=lambda a: a["name"])
        scripts += y

    script_dict = {}
    for s in scripts:
        name = s["name"]
        action = s["action"]
        script_dict[name] = action
    
    return script_dict

if __name__ == "__main__":
    data = get_soundscripts()
    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)
    output_path = "data/events.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent = 4)
    print("Written to", output_path)
