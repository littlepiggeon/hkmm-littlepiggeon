import githubapi

import os
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from xml.etree import ElementTree

from colorama import Fore, Back, Style
import vdf, winreg
from requests import get as r_get
from urllib3 import disable_warnings
from urllib3.exceptions import SecurityWarning

disable_warnings(SecurityWarning)


def colored(text: str, fore: str, back: str = "", style: str = ""):
    """Color the text with the given color and style.

    Args:
        text (str): Text to color.
        fore (str): Foreground color.
        back (str, None): Background color. Defaults to None.
        style (str, None): Style to use. Defaults to None.

    Returns:
        str: Colored text.
    """
    print(f"{fore}{back}{style}{text}{Style.RESET_ALL}")


info = lambda text: colored(text, Fore.LIGHTBLACK_EX)
error = lambda text: colored(text, Fore.RED, style=Style.BRIGHT)
warning = lambda text: colored(text, Fore.YELLOW, style=Style.BRIGHT)
success = lambda text: colored(text, Fore.GREEN, style=Style.BRIGHT)


def get_HK_installation_path() -> str | None:
    """Get the installation path of Hollow Knight on Windows."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
        key.Close()
    except WindowsError:
        return

    with open(steam_path + r"\steamapps\libraryfolders.vdf", "r") as f:
        library_folders = vdf.load(f)

    for lib in library_folders["libraryfolders"].values():
        path = lib["path"]
        game_dir = os.path.join(path, "steamapps", "common", "Hollow Knight")
        if os.path.exists(game_dir):
            return game_dir
    return


def install_mod_api(game_path: str) -> int:
    """Install the mod API for Hollow Knight.

    Args:
        game_path (str): The path to the Hollow Knight installation directory.
    """
    with TemporaryDirectory() as temp_dir:
        if not (
            url := githubapi.get_latest_release_asset(
                "hk-modding", "api", "ModdingApiWin.zip"
            )
        ):
            error("Error getting the latest release from GitHub.")
            return 1

        with r_get(url, stream=True, verify=False) as r:
            if r.ok:
                total_size = int(r.headers.get("Content-Length", 0))
                got_size = 0
                with open(os.path.join(temp_dir, "ModdingApiWin.zip"), "wb") as f:
                    info(f"Downloading {r.url} ...")

                    for chunk in r:
                        got_size += f.write(chunk)
                        print(
                            f"{got_size/total_size*100:3.2f}%|{int(got_size/total_size*30)*'▮':<30}|",
                            end="\r",
                        )

                    print("\nDownload complete.")
            else:
                print(
                    error(f"Error downloading.Error code: {r.status_code}-{r.reason}")
                )
                return 1

        with ZipFile(os.path.join(temp_dir, "ModdingApiWin.zip"), "r") as zip_ref:
            info("Extracting ModdingApiWin.zip...")

            total = len(zip_ref.filelist) - 1
            got = 0
            for file in zip_ref.filelist:
                if not file.filename.startswith("README"):

                    zip_ref.extract(
                        file, os.path.join(game_path, "/hollow_knight_Data/Managed/")
                    )
                    got += 1
                    print(f"{got/total*100:3.2f}%({got} / {total})", end="\r")

            info("\nExtraction complete.")
            return 0


def list_installed_mods(game_path: str) -> list[str]:
    """List installed mods in the game directory.

    Args:
        game_path (str): The path to the Hollow Knight installation directory.

    Returns:
        list[str]: List of installed mods.
    """
    mod_dir = os.path.join(game_path, "hollow_knight_Data/Managed/Mods/")

    mods = [mod for mod in os.listdir(mod_dir) if mod != "Disabled"]
    return mods


def update_mod_index(game_path: str) -> int:
    """Update the mod index.

    Args:
        game_path (str): The path to the Hollow Knight installation directory.

    Returns:
        int: 0 if successful, 1 if failed.
    """
    index_dir = os.path.expanduser("~/AppData/Local/HKMM/")
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    with r_get(
        "https://github.com/hk-modding/modlinks/raw/refs/heads/main/ModLinks.xml",
        verify=False,
    ) as r:
        if r.ok:
            with open(os.path.join(index_dir, "ModLinks.xml"), "wd") as f:
                f.write(r.content)
        else:
            error(
                f"Error downloading mod index. Error code: {r.status_code}-{r.reason}"
            )
            return 1
        return 0


def install_mod(game_path: str, name: str) -> int:
    """Install a mod for Hollow Knight.

    Args:
        game_path (str): The path to the Hollow Knight installation directory.
        name (str): The name of the mod to install.

    Returns:
        int: 0 if successful, 1 if failed.
    """
    index_dir = os.path.expanduser("~/AppData/Local/HKMM/")
    with open(os.path.join(index_dir, "ModLinks.xml"), "r") as f:
        et = ElementTree.parse(f)
        for mod in et.findall("Manifest"):
            if mod.get("Name") == name:
                url = mod.get("Link")
                dependencies = mod.findall("Dependency")
                break
        else:
            error(f"Mod '{name}' not found in the mod index.")
            return 1

    with TemporaryDirectory() as temp_dir:
        with r_get(url, stream=True, verify=False) as r:  # type: ignore
            if r.ok:
                filename = (
                    r.headers.get("Content-Disposition", 'filename="mod"')
                    .split("filename=")[-1]
                    .strip('"')
                )

                total_size = int(r.headers.get("Content-Length", 0))
                got_size = 0
                with open(os.path.join(temp_dir, filename), "wb") as f:
                    info(f"Downloading {r.url} ...")

                    for chunk in r.iter_content(chunk_size=8192):
                        got_size += f.write(chunk)
                        print(
                            f"{got_size/total_size*100:3.2f}%|{int(got_size/total_size*30)*'▮':<30}|",
                            end="\r",
                        )

                    info("\nDownload complete.")
            else:
                error(f"Error downloading.Error code: {r.status_code}-{r.reason}")
                return 1

        if filename.endswith(".zip"):
            with ZipFile(os.path.join(temp_dir, filename), "r") as zip_ref:
                info(f"Extracting {filename}...")
                path = os.path.join(
                    game_path, f"hollow_knight_Data/Managed/Mods/{name}"
                )
                for file in zip_ref.filelist:
                    if not file.filename.startswith("README"):
                        zip_ref.extract(file, path)
                info("\nExtraction complete.")
                return 0
        else:
            info(
                f"Copying {filename} to {game_path}/hollow_knight_Data/Managed/Mods/{name}..."
            )
            path = os.path.join(game_path, f"hollow_knight_Data/Managed/Mods/{name}")
            if not os.path.exists(path):
                os.makedirs(path)
            with open(os.path.join(path, filename), "wb") as f:
                with open(os.path.join(temp_dir, filename), "rb") as mod_file:
                    f.write(mod_file.read())
            info("Copy complete.")
        
        for dependency in dependencies:
            dep_name = dependency.get("Name")
            if not dep_name:
                continue
            info(f"Installing dependency: {dep_name}")
            if install_mod(game_path, dep_name) != 0:
                warning(f"Failed to install dependency: {dep_name}")
            
