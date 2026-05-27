import tomllib, vpk

def clean_toml_directory(path):
    # in case they got freaky with windows slashes
    path = path.replace("\\","/")

    if not path.endswith("/"):
        path += "/"

    return path

with open("config.txt", "rb") as f:
    tomldata = tomllib.load(f)

tf2_directory = clean_toml_directory(tomldata["tf2_directory"])
tf2_scenes_directory = clean_toml_directory(tomldata["tf2_scenes_directory"])

# due to the way tf2 scenes are loaded, scenes HAVE to have the exact folder
#  path of "scenes/player/etc/etc". no way to guarantee that someone running
#  this script has the right folder layout, so basically this supports two
#  possibilities: user provided scenes folder, or user provided folder
#  containing scenes folder. Anything else will produce errors or bad output
if not tf2_scenes_directory.endswith("/scenes/"):
    tf2_scenes_directory += "scenes/"

tf2_misc_dir_vpk_path = tf2_directory + "tf/tf2_misc_dir.vpk"
tf2_sound_misc_dir_path = tf2_directory + "tf/tf2_sound_misc_dir.vpk"
tf2_sound_vo_english_dir_path = tf2_directory + "tf/tf2_sound_vo_english_dir.vpk"

tf2_force_renew_data = tomldata["force_renew_data"]
tf2_force_renew_transcripts = tomldata["force_renew_transcripts"]
