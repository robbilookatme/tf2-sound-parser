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

import zipfile,io,os
from parser_types import *
from tf2_parse_paths import *

map_dir = tf2_directory + "tf/maps"

def get_bsp_sounds():
    sounddict = {}
    for path,_,files in os.walk(map_dir):
        for file in files:
            if ".bsp" in file:
                print(file, end="")

                # Load bsp data
                bsp = path + "/" + file
                with open(bsp, "rb") as f:
                    fd = f.read()

                # Find the magic number where the .zip data starts
                offset = fd.find(b'\x00\x50\x4b\x03\x04') + 1
                if offset == 0:
                    print(", couldn't find zipped data")
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
                        print(", found " + str(len(soundlist)) + " sounds!", end="")
                        sounddict[file] = soundlist

                    print()
                except zipfile.BadZipFile:
                    # All base game maps should pass, some custom maps may not
                    print(", error in zip processing")
    return sounddict

if __name__ == "__main__":
    get_bsp_sounds()
