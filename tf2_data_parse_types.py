from enum import Enum

# Order of files in output csv/json based on string matching
output_sort_list = [
    "_mvm_",
    "vo/toughbreak/",
    "vo/taunts/pyro/",
    "vo/taunts/scout/",
    "vo/taunts/soldier/",
    "vo/taunts/spy/",
    "vo/taunts/sniper/",
    "vo/taunts/medic/",
    "vo/taunts/heavy/",
    "vo/taunts/demo/",
    "vo/taunts/engy/",
    "_sf12_",
    "_sf13_",
    "_item_",
    "vo/compmode/",
]
def output_sort(key):
    sort_value = 0

    for i in range(len(output_sort_list)):
        s = output_sort_list[i]
        if s in key:
            sort_value += 1 << i

    zeroes = len(str( 1 << len(output_sort_list) ))
    sort_value = str(sort_value).zfill(zeroes)
    return sort_value + key

# string matching to determine output file
#  map_misc is determined at runtime
grouped_output_paths = {
    "map_misc" : [],
    "scout" : [
        "vo/toughbreak/scout",
        "vo/scout",
        "vo/compmode/cm_scout",
        "vo/taunts/scout",
        "player/shove",
    ],
    "soldier" : [
        "vo/toughbreak/soldier",
        "vo/soldier",
        "vo/compmode/cm_soldier",
        "vo/taunts/soldier",
    ],
    "pyro" : [
        "vo/pyro",
        "vo/compmode/cm_pyro",
        "vo/taunts/pyro",
    ],
    "heavy" : [
        "vo/toughbreak/heavy",
        "vo/heavy",
        "vo/compmode/cm_heavy",
        "vo/taunts/heavy",
        "vo/sandwicheat",
    ],
    "engineer" : [
        "vo/taunts/engy",
        "vo/compmode/cm_engie",
        "vo/toughbreak/eng",
        "vo/taunts/eng",
        "vo/engineer",
        "vo/taunts/engineer",
    ],
    "demoman" : [
        "vo/toughbreak/demo",
        "vo/compmode/cm_demo",
        "vo/taunts/demo",
        "vo/demoman",
        "vo/burp",
    ],
    "medic" : [
        "vo/toughbreak/medic",
        "vo/medic_",
        "vo/taunts/medic",
    ],
    "sniper" : [
        "vo/toughbreak/sniper",
        "vo/sniper",
        "vo/compmode/cm_sniper",
        "vo/taunts/sniper",
    ],
    "spy" : [
        "vo/toughbreak/spy",
        "vo/spy",
        "vo/compmode/cm_spy",
        "vo/taunts/spy",
    ],
    "administrator" : [
        "vo/mvm_",
        "announcer",
        "cm_admin",
        "vo/intel_",
    ],
    "miss_pauling" : [
        "plng",
    ],
    "halloween" : [
        "vo/halloween_",
        "vo/wolf_howl",
    ],
    "vsh" : [
        "saxton_hale_dt_2025_1",
        "mercs_dt_2025_1",
        "mercs_tr_2025_1",
        "mercs_sm_2025_1",
        "mercs_ml_2025_1",
        "mercs_ns_2025_1",
        "mercs_ob_2025_1",
    ],
    "items" : ["items/"],
    "mvm_bots" : ["mvm/"],
    "weapons" : [
        "weapons/",
        "vo/sword",
    ],
    "misc" : [
        "physics/",
        "music/",
        "player/",
        "ambient/",
        "ambient_mp3/",
        "ambience/",
        "misc/",
        "ui/",
        "common/",
        "passtime/",
        "npc/",
        "doors/",
        "vehicles/",
        "vo/bot_worker",
        "vo/taunts/skateboard",
        "vo/puff",
        "vo/null",
        "vo/test",
        "vo/medic1",
        "vo/medic2",
        "replay/",
        "coach/",
        "commentary/",
        "pl_hoodoo/",
        "plats/",
    ],
}

class Named():
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return self.name == other
    def __hash__(self):
        return hash(self.name)

class FileState(Enum):
    USED = "used"
    UNUSED = "unused"
    MISSING = "missing"

class Rule(Named):
    def __init__(self, name, criteria, responses, contexts, applycontexttoworld):
        self.name = name
        self.criteria = criteria
        self.responses = responses
        self.contexts = contexts
        self.applycontexttoworld = applycontexttoworld
    def get_criteria(self):
        return self.responses + self.contexts

class Response(Named):
    def __init__(self, name, scenes = []):
        self.name = name
        self.scenes = scenes
        self.rules = []
        self.state = FileState.UNUSED

class Scene(Named):
    def __init__(self, name, events = []):
        self.name = name
        self.events = events
        self.responses = []
        self.state = FileState.UNUSED

class Event(Named):
    def __init__(self, name, audio_files = []):
        self.name = name
        self.audio_files = audio_files
        self.scenes = []
        self.state = FileState.UNUSED

class AudioFile(Named):
    def __init__(self, name):
        self.base_name = name.split("/")[-1][:-4]
        self.name = name
        self.events = []
        self.state = FileState.UNUSED
        self.transcript = ""
