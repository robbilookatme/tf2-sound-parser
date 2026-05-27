from lark import Lark, Transformer, Discard
from parser_types import *
from tf2_parser_config import *

item_schema_file = tf2_directory + "tf/scripts/items/items_game.txt"
localization_file = tf2_directory + "tf/resource/tf_english.txt"

class LocalizationT(Transformer):
    def s(self,children):
        return [
                clean_string(children[0]),
                clean_string(children[1])
            ]
    def start(self,children):
        return children

class ItemSchemaT(Transformer):
    def start(self,children):
        return clean_string(children[1])

localization_lark = Lark(r'''
?start: "\"lang\"" "{" "\"Language\"" "\"English\"" "\"Tokens\"" "{" s+ "}" "}"

?s : STRING (SPLIT_STR | STRING)
SPLIT_STR: "\"" _STRING_ESC_INNER ("\n" _STRING_ESC_INNER)+ "\""
STRING : "\"" _STRING_ESC_INNER "\""

%import common._STRING_ESC_INNER
%import common.WS
%import common.CPP_COMMENT
%ignore CPP_COMMENT
%ignore WS
''')

item_schema_line_lark = Lark(r'''
?start: STRING STRING

%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
''')

def get_item_schema():
    print("Parsing localization file for taunt names...")
    with open(localization_file, encoding="utf-16") as f:
        fl = f.readlines()
        fd = "".join(fl)

    localization = {}
    loc_tree = localization_lark.parse(fd)
    loc_data = LocalizationT().transform(loc_tree)

    for li in loc_data:
        localization[li[0]] = li[1]
    
    print("Parsing item schema for taunt scenes...")
    with open(item_schema_file) as f:
        fl = f.readlines()

        taunt_vcds = {}
        previous_name = ""
        ist = ItemSchemaT()
        count = 0
        for l in fl:
            if ".vcd" in l or '"item_name"' in l:
                val_tree = item_schema_line_lark.parse(l)
                val = ist.transform(val_tree)
                
                if ".vcd" in l:
                    taunt_vcds[previous_name].append(val)
                    count += 1
                elif '"item_name"' in l:
                    previous_name = val[1:]
                    if previous_name in localization:
                        previous_name = localization[previous_name]
                    taunt_vcds[previous_name] = []

        vcds_2 = taunt_vcds
        taunt_vcds = {}
        for k,v in vcds_2.items():
            if len(v) > 0:
                taunt_vcds[k] = v

        return taunt_vcds

if __name__ == "__main__":
    get_item_schema()
