import json, pathlib
from lark import Lark, Transformer, Discard
from parser_types import *
from tf2_parser_config import *

class ResponseRulesT(Transformer):
    def _f(self, _):
        return Discard

    def start(self, children):
        return children

    def include(self, children):
        return Include(clean_string(children[0]).lower())

    def criterion(self, children):
        return Criterion(clean_string(children[0]))

    def response(self, children):
        name = children[0]
        scenes = children[1]

        return Response(name, scenes)

    def response_name(self, children):
        return clean_string(children[0])

    def response_scene_list(self, children):
        return children

    def response_scene(self, children):
        return clean_filename(children[0])

    def rule(self, children):
        name = children[0]
        criteria = None
        responses = []
        contexts = []
        applycontexttoworld = False
        for i in range(1, len(children)):
            val = children[i]
            if type(val) == RuleCriteria and criteria == None:
                criteria = val.get()
            elif type(val) == RuleResponse:
                responses.append(val.get())
            elif type(val) == ApplyContext:
                contexts.append(val.get())
            elif type(val) == ApplyContextToWorld:
                applycontexttoworld = True
            else:
                print("BAD RULE FORMAT????")
                print(type(val))
                print(val)
                print(children)
        
        return Rule(name, criteria, responses, contexts, applycontexttoworld)

    def rule_name(self, children):
        return clean_string(children[0])

    def rule_response(self, children):
        return RuleResponse(clean_string(children[0]))

    def rule_criteria(self, children):
        return RuleCriteria(children)

    def rule_criterion(self, children):
        return clean_string(children[0])

    def rule_applycontext(self, children):
        return ApplyContext(clean_string(children[0]))

    def rule_applycontexttoworld(self, children):
        return ApplyContextToWorld()

response_rules_lark = Lark(r'''
?start: (include | enum | criterion | rule | response)*
include: "#include" STRING

?enum : "enumeration" STRING "{" (STRING STRING)* "}" -> _f
?criterion: ("criterion" | "Criterion") criterion_name criterion_value*
?criterion_name: STRING
?criterion_value: STRING
|                "required"
|                "weight" INT

rule : ("Rule" | "rule") rule_name "{" rule_data* "}"
rule_name : NAME
?rule_data : rule_criteria
|           rule_response
|           rule_applycontext
|           "applycontexttoworld" -> rule_applycontexttoworld
rule_criteria : "criteri" ("a" | "on") rule_criterion* -> rule_criteria
rule_criterion : NAME
rule_response.1 : "Response"i NAME
rule_applycontext.1 : "ApplyContext"i STRING

response : "response"i response_name "{" response_scene_list "}" -> response
response_name : NAME
response_scene_list : response_scene*
response_scene : "scene" STRING (predelay)?
predelay : "predelay" STRING -> _f

NAME : "\""? NAME_WORD "\""?
NAME_WORD : ("_"|LETTER|DIGIT)+

%import common.LETTER
%import common.DIGIT
%import common.CPP_COMMENT -> COMMENT
%import common.ESCAPED_STRING -> STRING
%import common.CNAME
%import common.INT
%import common.WS
%ignore WS
%ignore COMMENT
''')

response_rules_file_path = "scripts/talker/response_rules.txt"

def get_responserules():
    print("Parsing response-rules files...")
    response_rules_files = []

    tf2_misc_dir_vpk = vpk.open(tf2_misc_dir_vpk_path)
    files_to_read = [response_rules_file_path]

    rules = {}
    responses = {}
    criteria = []

    while len(files_to_read) > 0:
        fp = files_to_read.pop()
        if not fp.startswith("scripts/"):
            fp = "scripts/" + fp
        print(fp)
        f = tf2_misc_dir_vpk.get_file(fp)
        fd = f.read().decode("utf-8")
        x = response_rules_lark.parse(fd)
        #print(x.pretty())
        y = ResponseRulesT().transform(x)

        for t in y:
            if type(t) == Rule:
                rules[t.name] = t.get()
            elif type(t) == Response:
                responses[t.name] = t.scenes
            elif type(t) == Criterion:
                criteria.append(t.name)
            elif type(t) == Include:
                files_to_read.append(t.path)

    return {
        "rules" : rules,
        "responses" : responses,
        "criteria" : criteria
    }

if __name__ == "__main__":
    data = get_responserules()
    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)
    output_path = "data/responserules.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent = 4)
    print("Written to", output_path)
