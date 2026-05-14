from lark import Lark, Transformer, Discard
from parser_types import *
from tf2_parse_paths import *

class ResponseRulesTxtT(Transformer):
    def _f(self, _):
        return Discard

    def start(self, children):
        for i in range(len(children)):
            children[i] = clean_string(children[i].children[0])
        return children

class ResponseRulesT(Transformer):
    def _f(self, _):
        return Discard

    def start(self, children):
        return children

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
?criterion: ("criterion" | "Criterion") criterion_value* -> _f
criterion_value: STRING
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

def get_responserules():
    print("Parsing response-rules files...")
    response_rules_files = []

    tf2_misc_dir_vpk = vpk.open(tf2_misc_dir_vpk_path)
    response_rules_file = tf2_misc_dir_vpk.get_file("scripts/talker/response_rules.txt")

    # read through response_rules.txt first to get all #includes
    fd = response_rules_file.read().decode("utf-8")
    x = response_rules_lark.parse(fd)
    response_rules_files = ResponseRulesTxtT().transform(x)
    
    rules = {}
    responses = {}
    
    for file in response_rules_files:
        fp = "scripts/" + file.lower()
        print(fp)
        f = tf2_misc_dir_vpk.get_file(fp)
        fd = f.read().decode("utf-8")
        x = response_rules_lark.parse(fd)
        #print(x.pretty())
        y = ResponseRulesT().transform(x)

        # split rules and responses into separate things
        for i in y:
            if type(i) == Rule:
                rules[i.name] = i.get()
            elif type(i) == Response:
                responses[i.name] = i.scenes

    return {"rules" : rules, "responses" : responses}

if __name__ == "__main__":
    get_responserules()
