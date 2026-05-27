from lark import Lark, Transformer, Discard
import os
from parser_types import *
from tf2_parser_config import *

class T(Transformer):
    def _f(self,val):
        return Discard

    def channel(self, children):
        if len(children) < 1:
            return Discard
        else:
            return children
    
    def start(self,children):
        return children
    def actor(self,children):
        return children

    def param(self, children):
        return EventParam(children[0])

    def event_name(self,children):
        return EventName(children[0])

    def speak(self,children):
        return EventSubtype("speak")

    def time(self, children):
        t1 = float(children[0])
        t2 = float(children[1])

        # if t2 is less than t1, this COULD be a bad vcd
        #  but not necessarily! depends on if there are other
        #  events with valid timestamps
        # that's hard to figure out from here, so just assume
        #  it's fine

        return Discard

    def event(self,children):
        event_subtype = None
        name = None
        param = None
        for c in children:
            if type(c) == EventSubtype:
                event_subtype = c.subtype
            elif type(c) == EventParam:
                param = clean_string(c.param).lower()
            elif type(c) == EventName:
                name = c.name

        if event_subtype != "speak":
            return Discard

        return clean_string(param)

l = Lark(r'''
start: (event | actor | scene_ramp | scene_property | scalesettings)*

onoff : "on" -> on
|       "off" -> off

actor : "actor" actor_name "{" channel* "}"
actor_name : STRING -> _f
channel : "channel" channel_name "{" (event | active)* "}"
channel_name : STRING -> _f

active : "active" STRING -> _f

event: "event" event_subtype event_name "{" event_property* "}"
event_subtype : "speak" -> speak
| "expression" -> _f
| "sequence" -> _f
| "stoppoint" -> _f
| "flexanimation" -> _f
| "unspecified" -> _f
| "loop" -> _f

event_name : STRING | (/"/ /end/ "\\" /"/)

event_property : ("time" FLOAT FLOAT)     -> time
|                ("param" STRING)         -> param
|                "param2" STRING          -> _f
|                "fixedlength"            -> _f
|                "playoverscript"         -> _f
|                "cc_noattenuate"         -> _f
|                "resumecondition"        -> _f
|                "distancetotarget" FLOAT -> _f
|                "cctype" STRING          -> _f
|                "cctoken" STRING         -> _f
|                event_ramp               -> _f
|                flex_animations          -> _f
|                "loopcount" STRING       -> _f
|                tags                     -> _f
|                "active" (STRING|INT)    -> _f

flex_animations: "flexanimations" ("samples_use_time")? ("defaultcurvetype=" curve_type)? "{" flex* "}"

tags : "tags" "{" (STRING FLOAT)* "}"

flex : STRING "combo"? "disabled"? ("{" flex_data* "}")+
flex_data : FLOAT FLOAT (STRING | curve_type)?

curve_type : "curve_catmullrom_normalize_x_to_curve_catmullrom_normalize_x"
|            "curve_linear_interp_to_curve_linear_interp"
|            "curve_easein_to_curve_easeout"
|            "curve_easein_to_curve_easein"
|            "curve_easeout_to_curve_easeout"
|            "curve_bspline_to_curve_bspline"

event_ramp : "event_ramp" "{" ramp "}" -> _f
scene_ramp : "scene_ramp" "{" ramp "}" -> _f

ramp : (FLOAT FLOAT)*

scalesettings: "scalesettings" "{" (STRING STRING)* "}" -> _f

scene_property : (fps | snap | ignore_phonemes) -> _f

fps : "fps" INT
snap : "snap" onoff
ignore_phonemes : "ignorePhonemes" onoff

FLOAT : "-"? FFLOAT

%import common.CPP_COMMENT -> COMMENT
%import common.WORD
%import common.ESCAPED_STRING -> STRING
%import common.INT
%import common.WS
%import common.FLOAT -> FFLOAT
%import common.NEWLINE
%ignore WS
%ignore COMMENT
''')

def get_vcds():
    vcds = {}

    print("reading vcds... be patient, there's like five thousand...")

    z = 0
    
    for path, _, files in os.walk(tf2_scenes_directory):
        for file in files:
            fp = path + "/" + file

            if ".vcd" not in fp.lower():
                continue
            
            z += 1

            # Progress info
            if z % 500 == 0:
                print("vcd files read:", z)

            outlist = []

            with open(fp) as f:
                #print(fp)
                fd = f.read()
            
            try:
                x = l.parse(fd)
            except Exception as e:
                print("error in", fp)
                print(e)
                quit()
            
            outlist = flatten(T().transform(x))

            if len(outlist) > 0:
                fp = "scenes/" + fp.lower()[len(tf2_scenes_directory):]
                vcds[fp] = outlist
            elif fd.count("speak") > len(outlist):
                print("Scene found with invalid speak events:")
                print(fp, outlist)

    return vcds

if __name__ == "__main__":
    get_vcds()
