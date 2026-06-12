filename_special_characters = ["*","#","@",">","<","^",")","}","$","!","?","&","~","`","+","$","%","(","/"]
def clean_filename(st):
    out = clean_string(st).lower()

    # run three times, first two for modifier characters in soundscripts
    #  and third one to catch any starting slashes
    for i in range(3):
        if out[0] in filename_special_characters:
            out = out[1:]
    return out.replace("\\","/")

def clean_string(st):
    out = str(st)
    if out.startswith('"') and out.endswith('"'):
        out = out[1:-1]
    return out

def flat_iter(li):
    if isinstance(li, list):
        for i in li:
            yield from flat_iter(i)
    else:
        yield li

def flatten(li):
    return list(flat_iter(li))

# Transcript Types
transcript_names = [
    "Scout_voice_commands",
    "Soldier_voice_commands",
    "Pyro_voice_commands",
    "Demoman_voice_commands",
    "Heavy_voice_commands",
    "Engineer_voice_commands",
    "Medic_voice_commands",
    "Sniper_voice_commands",
    "Spy_voice_commands",
    "Scout_responses",
    "Soldier_responses",
    "Pyro_responses",
    "Demoman_responses",
    "Heavy_responses",
    "Engineer_responses",
    "Medic_responses",
    "Sniper_responses",
    "Spy_responses",
    "Scout_taunts",
    "Soldier_taunts",
    "Pyro_taunts",
    "Demoman_taunts",
    "Heavy_taunts",
    "Engineer_taunts",
    "Medic_taunts",
    "Sniper_taunts",
    "Spy_taunts",
    "Administrator_responses",
    "Halloween_Boss_voice_responses",
    "Wheatley_responses",
    "Miss_Pauling_responses"
]

# VCD Types
class SpeakEvent():
    def __init__(self, script):
        self.script = script
    def __repr__(self):
        return self.script

class SequenceEvent():
    def __init__(self, sequence):
        self.sequence = sequence
    def __repr__(self):
        return self.sequence

class EventParam():
    def __init__(self, param):
        self.param = param
    def __repr__(self):
        return self.param

class EventName():
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class EventSubtype():
    def __init__(self, subtype):
        self.subtype = subtype
    def __repr__(self):
        return self.subtype

# Reponse Rule Types
class Include():
    def __init__(self, path):
        self.path = path
    def __repr__(self):
        return "INCLUDE: " + self.path

class Criterion():
    def __init__(self, name):
        self.name = name
    def get(self):
        return {"name" : self.name}
    def __repr__(self):
        return "CRITERION: " + self.name

class Rule():
    def __init__(self, name, criteria, responses, contexts, applycontexttoworld):
        self.name = name
        self.criteria = criteria
        self.responses = responses
        self.contexts = contexts
        self.applycontexttoworld = applycontexttoworld
    def get(self):
        return {
            "name" : self.name,
            "criteria" : self.criteria,
            "responses" : self.responses,
            "contexts" : self.contexts,
            "applycontexttoworld" : self.applycontexttoworld
        }
    def __repr__(self):
        return "RULE: " + str([self.criteria, self.responses])

class Response():
    def __init__(self, name, scenes):
        self.name = name
        self.scenes = scenes

    def get():
        return {"name" : self.name, "scenes" : self.scenes}

    def __repr__(self):
        return "RESPONSE: " + str([self.name, self.scenes])

class ApplyContext():
    def __init__(self, context):
        self.context = context
    def get(self):
        return self.context
    def __repr__(self):
        return self.context

class ApplyContextToWorld():
    def __init__(self): pass
    def __repr__(self):
        return "ApplyContextToWorld"

class RuleCriteria():
    def __init__(self, criteria):
        self.criteria = criteria
    def get(self):
        return self.criteria
    def __repr__(self):
        return repr(self.criteria)

class RuleResponse():
    def __init__(self, response):
        self.response = response
    def get(self):
        return self.response
    def __repr__(self):
        return repr(self.response)
