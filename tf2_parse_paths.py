import tomllib, vpk

def clean_toml_directory(path):
    if "/" in path and not path.endswith("/"):
        path += "/"
    elif "\\" in path and not path.endswith("\\"):
        path += "\\"

    # in case they got freaky with windows slashes
    path = path.replace("\\","/")

    return path

with open("config.txt", "rb") as f:
    tomldata = tomllib.load(f)

tf2_directory = clean_toml_directory(tomldata["tf2_directory"])
tf2_scenes_directory = clean_toml_directory(tomldata["tf2_scenes_directory"])

tf2_misc_dir_vpk_path = tf2_directory + "tf/tf2_misc_dir.vpk"
tf2_sound_misc_dir_path = tf2_directory + "tf/tf2_sound_misc_dir.vpk"
tf2_sound_vo_english_dir_path = tf2_directory + "tf/tf2_sound_vo_english_dir.vpk"
