import re, pathlib, json
from lark import Lark, Transformer, Discard
from parser_types import *
import download_transcripts

# Determine if transcript is of expected quality
#  (has quotes, brackets, or parentheses)
def is_good_transcript(transcript):
    l_bracket_count = transcript.count("[")
    r_bracket_count = transcript.count("]")
    bracket_count_matches = (l_bracket_count == r_bracket_count)
    has_brackets = bracket_count_matches and l_bracket_count > 0

    l_parenthesis_count = transcript.count("(")
    r_parenthesis_count = transcript.count(")")
    parentheses_count_matches = l_parenthesis_count == r_parenthesis_count
    has_parentheses = parentheses_count_matches and l_parenthesis_count > 0

    quote_count = transcript.count('"')
    has_quotes = quote_count > 1 and (quote_count % 2 == 0)

    return (has_brackets or has_parentheses or has_quotes)

transcript_lark = Lark(r'''
?start: (media | char)*
media.1: "[[Media:"i FILENAME "|" (BRACKETED_DIALOGUE | DIALOGUE) "]]"

# this took so so long to figure out.
#  basically, accept any character that isn't ]
#  and also accept any ] not followed by another ]
BRACKETED_DIALOGUE: "[" DIALOGUE "]"
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
        list_of_lines = T().transform(x)
        
        print(", found", len(list_of_lines), "lines")

        # Sanity check for parsed lines vs expected count
        if len(list_of_lines) != media_count:
            print("Mismatch! In",
                  t + ",",
                  len(list_of_lines),
                  "lines were parsed, expected",
                  media_count)

            for tl in ml:
                text_line = tl.lower().replace(" ","_")
                found = False
                for line in list_of_lines:
                    filename = line["file"]
                    if filename in text_line:
                        #print(filename, text_line)
                        found = True
                        break

                if not found:
                    print(tl)
            
            break

        for line in list_of_lines:
            lf = line["file"]
            lt = {}
            lt["transcript"] = line["transcript"]
            lt["wiki_transcript"] = line["wiki_transcript"]

            if lf in transcripts:
                existing_t = transcripts[lf]["wiki_transcript"]
                new_t = lt["wiki_transcript"]

                # Only replace transcript if new transcript is of better quality
                #  e.g. "laughs" would be replaced with "(Laugh)"
                is_old_transcript_bad = not is_good_transcript(existing_t)
                is_new_transcript_good = is_good_transcript(new_t)
                are_transcripts_different = existing_t.lower() != new_t.lower()
                should_replace = is_old_transcript_bad and is_new_transcript_good and are_transcripts_different

                if should_replace:
                    transcripts[lf] = lt
                    print("TRANSCRIPT REPLACED!", lf)
                    print(existing_t)
                    print(new_t)

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
    data = get_transcripts(False)
    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)
    output_path = "data/transcripts.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent = 4)
    print("Written to", output_path)
