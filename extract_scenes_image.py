import pathlib
from tf2_parser_config import *

def extract_scenes_image():
    tf2_misc_dir_vpk = vpk.open(tf2_misc_dir_vpk_path)
    scenes_image = tf2_misc_dir_vpk.get_file("scenes/scenes.image")

    fd = scenes_image.read()

    pathlib.Path("data/").mkdir(parents=True, exist_ok=True)

    with open("data/scenes.image", "wb") as f:
        f.write(fd)

if __name__ == "__main__":
    extract_scenes_image()
