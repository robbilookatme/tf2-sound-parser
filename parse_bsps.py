'''
Code adapted from 1WHISKY's bsp-to-zip

MIT License

Copyright (c) 2021 1WHISKY

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import zipfile,io,os,json,pathlib
from lark import Lark, Transformer
from parser_types import *
from tf2_parser_config import *

mapname_lark = Lark(r'''
?start: mapname_line*

?mapname_line: "\"comment: mapname\"" "\"string\"" "\""  MAPNAME "\""
MAPNAME: ("_"|LETTER|DIGIT)+

%import common.LETTER
%import common.DIGIT
%import common.WS
%ignore WS
''')

map_dir = tf2_directory + "tf/maps"
player_stats_file = tf2_directory + "tf/tf2_playerstats.dmx"

def get_bsp_sounds():
    sounddict = {}
    bsp_dict = {}
    # Try to get map name list from tf2_playerstats.dmx
    try:
        with open(player_stats_file) as f:
            fl = f.readlines()
        for line in fl:
            if "mapname" in line and "Missing" not in line:
                map_name = str(mapname_lark.parse(line)) + ".bsp"
                map_file = map_dir + "/" + map_name
                bsp_dict[map_name] = map_file
        # Sanity check: we know there's over 200 base maps in TF2
        #  so if we're not close to that number, assume our player stats file sucks
        if len(bsp_dict) < 200:
            raise Exception()
    
    # Backup option is to search the map folder directly
    #  This is not optimal, as players may have added maps themselves
    except:
        print("Error in tf2_playerstats.dmx, loading from maps/ folder...")
        for path,_,files in os.walk(map_dir):
            for file in files:
                if ".bsp" in file:
                    bsp_dict[file] = path + "/" + file

    for map_name, file in bsp_dict.items():
        # Load bsp data
        with open(file, "rb") as f:
            fd = f.read()

        # Find the magic number where the .zip data starts
        offset = fd.find(b'\x00\x50\x4b\x03\x04') + 1
        if offset == 0:
            print(map_name + ", couldn't find zipped data")
            continue

        try:
            # Convert bsp zip data to a zip file object
            zdata = io.BytesIO(fd[offset:])
            zfile = zipfile.ZipFile(zdata)
            zinfolist = zfile.infolist()

            soundlist = []
            for i in zinfolist:
                zfilename = i.filename
                if "sound/" in zfilename or ".mp3" in zfilename or ".wav" in zfilename:
                    #print(zfilename)
                    soundlist.append(zfilename)
            
            if len(soundlist) > 0:
                print(map_name + ", found " + str(len(soundlist)) + " sounds!")
                sounddict[file] = soundlist
        except zipfile.BadZipFile:
            # All base game maps should pass, some custom maps may not
            print(map_name + ", error in zip processing")
    return sounddict

if __name__ == "__main__":
    data = get_bsp_sounds()
    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)
    output_path = "data/bsp_sounds.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent = 4)
    print("Written to", output_path)
