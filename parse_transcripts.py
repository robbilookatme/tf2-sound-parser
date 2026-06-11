import re
from lark import Lark, Transformer, Discard
from parser_types import *
import download_transcripts

transcript_lark = Lark(r'''
?start: (media | char)*
media.1: "[[Media:"i FILENAME "|" DIALOGUE "]]"

# this took so so long to figure out.
#  basically, accept any character that isn't ]
#  and also accept any ] not followed by another ]
DIALOGUE: (/[^\]]/ | /\][^\]]/)+

FILENAME: NAME (".wav"i|".mp3"i)
NAME: ("_"|LETTER|DIGIT|" "|"-"|".")+

char: /./ -> _f

WIKICOMMENT: "<!--" /.*?/ "-->"

%import common.LETTER
%import common.DIGIT
%import common.WS
%ignore WS
%ignore WIKICOMMENT
''')

class T(Transformer):
    def _f(self, _):
        return Discard

    def media(self, children):
        file = clean_string(children[0]).lower().replace(" ", "_")
        wiki_transcript = children[1]
        transcript = clean_string(wiki_transcript).replace("<nowiki>","").replace("</nowiki>","")

        # fix split quotes
        if transcript.count('"') == 1:
            transcript = transcript.replace('"', "")

        # fix wiki formatting that we don't use, double and triple apostrophes
        transcript = clean_string(transcript.replace("'''","").replace("''",""))
        
        if file.endswith(".mp3") or file.endswith(".wav"):
            file = file[:-4]
        else:
            print("Unexpected filetype:", file)
        
        return {
            "file" : file,
            "transcript" : transcript,
            "wiki_transcript" : wiki_transcript
        }
    def start(self, children):
        return flatten(children)

def get_transcripts(force_renew_transcripts):
    if force_renew_transcripts:
        print("Force renew transcripts flag enabled, downloading all transcripts...")
    download_transcripts.download_transcripts(force_renew_transcripts)
    
    print("Parsing transcripts...")
    transcripts = {}

    for t in transcript_names:
        print(t, end = "")
        t = "data/transcripts/" + t + ".txt"
        with open(t) as f:
            fd = f.read()

        # trim out trivia section, which may also have media tags
        fd = fd.split("== Trivia ==")[0]
        fl = fd.split("\n")

        # cut down to only lines with media tags
        ml = [x for x in fl if "media:" in x.lower()]
        fd = "\n".join(ml)

        # Count how many instances of [[Media:___|___]] exist
        reg = r"\[\[[Mm]edia:[^|]+\|([^\]]|\][^\]])+\]\]"
        res = re.findall(reg, fd)
        media_count = len(res)

        # Sanity check for media tags that don't have expected formatting
        for li in ml:
            li_res = re.findall(reg, li)
            rc = len(li_res)
            cc = li.count("media:") + li.count("Media:")
            if rc != cc and "|" in li:
                print("PROBLEM WITH LINE:")
                print(li)
                print(rc, cc)
                print(li_res)
                print()

        # Parse transcripts
        x = transcript_lark.parse(fd)
        y = T().transform(x)
        
        print(", found", len(y), "lines")

        # Sanity check for parsed lines vs expected count
        if len(y) != media_count:
            print("Mismatch! In", t + ",", len(y), "lines were parsed, expected", media_count)

            for tl in ml:
                text_line = tl.lower().replace(" ","_")
                found = False
                for line in y:
                    filename = line["file"]
                    if filename in text_line:
                        #print(filename, text_line)
                        found = True
                        break

                if not found:
                    print(tl)
            
            break

        for line in y:
            lf = line["file"]
            lt = {}
            lt["transcript"] = line["transcript"]
            lt["wiki_transcript"] = line["wiki_transcript"]

            if lf in transcripts:
                existing_t = transcripts[lf]["transcript"].lower()
                new_t = lt["transcript"].lower()

                # Print out conflicts for sounds transcribed more than once
                #  not recommended, because there are a lot of them
                if existing_t != new_t and False:
                    print("Conflicting transcript found")
                    print(lf)
                    print(existing_t)
                    print(new_t)
                    print()
            else:
                transcripts[lf] = lt
        

    return transcripts

if __name__ == "__main__":
    get_transcripts(False)
