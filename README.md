# TF2 Sound Parser

This is a utility designed to document information about every sound in Team Fortress 2, particularly voice lines.

Outputs from my own runs of this utility are available at https://github.com/robbilookatme/tf2-voice-pack-reference

## Setup

First, extract the scenes out of TF2's 'scenes.image using VSIF2VCD, vsif2vcd.py, or any other tool. You can use the included "extract_scenes_image.py" script to get scenes.image out of the TF2 .vpk files. Or, if you trust me, you can also download them from https://github.com/robbilookatme/tf2-scenes

In config.txt, set the folders where TF2 is installed and where you extracted the game's scenes to. Finally, run "main.py".

## Output

The utility creates an "output" folder, which contains a "csv" and "json" folder. These folders contain .csv and .json formatted lists of every sound file in TF2 and how they are triggered by the dialogue system, if applicable.

## Intermediate Data

The utility also creates intermediate data in the "data" folder, and only parses data which is not present in that folder. This is mostly a time-saving feature if you need to re-run the utility for any reason, or if you want to view or process the dialogue system's data manually.
