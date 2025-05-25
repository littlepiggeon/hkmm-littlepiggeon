import hkmm
from hkmm import colored, info, error, warning, success

from cmd import Cmd
from argparse import ArgumentParser
import os

from colorama import Fore, Back, Style


class HKMM(Cmd):
    """A simple command line interface for the Hollow Knight Mod Manager."""

    prompt = "HKMM> "
    intro = colored(
        "Welcome to the Hollow Knight Mod Manager! Type help or ? to list commands.\n",
        Fore.BLACK,
        Back.WHITE,
        Style.BRIGHT,
    )

    def preloop(self):
        self.game_path = hkmm.get_HK_installation_path()
        if not self.game_path:
            warning(
                'Hollow Knight not found! Please set the path by command "gamepath path/to/game/".'
            )
        else:
            success(f"Hollow Knight found at {self.game_path}")

    def do_exit(self, args):
        """Exit the program."""
        print(colored("Goodbye!", Fore.LIGHTMAGENTA_EX))
        return True

    def do_gamepath(self, args):
        """Set the path to the Hollow Knight installation."""
        parser = ArgumentParser(
            prog="gamepath",
            description="Set the path to the Hollow Knight installation.",
        )
        parser.add_argument(
            "path", help="Path to the Hollow Knight installation directory."
        )
        args = parser.parse_args(args.split())
        if not args.path:
            error("Please provide a path.")
            return
        if not os.path.isdir(args.path):
            error("Invalid path. Please provide a valid path.")
            return
        self.game_path = args.path
        success(f"Game path set to {self.game_path}")

    def do_install_api(self, args):
        """Install the mod API for Hollow Knight."""
        if not self.game_path:
            warning(
                'Hollow Knight not found! Please set the path by command "gamepath path/to/game/".'
            )
            return
        info(f"Installing Mod API for Hollow Knight at {self.game_path}...")

        if hkmm.install_mod_api(self.game_path) == 0:
            print(colored("Mod API installed successfully!", Fore.GREEN))
        else:
            error("Error installing Mod API.")

    def do_list(self, args):
        """List installed mods."""
        if not self.game_path:
            warning(
                'Hollow Knight not found! Please set the path by command "gamepath path/to/game/".'
            )
            return
        print("Installed mods:")
        mods = hkmm.list_installed_mods(self.game_path)
        if mods:
            for mod in mods:
                colored(f"- {mod}", Fore.BLACK, Back.WHITE, Style.DIM)
        else:
            print("No mods installed.")

    def do_update(self, args):
        """Update the mod index"""
        if not self.game_path:
            warning(
                'Hollow Knight not found! Please set the path by command "gamepath path/to/game/".'
            )
            return
        info("Updating mod index...")
        if hkmm.update_mod_index(self.game_path) == 0:
            print(colored("Mod index updated successfully!", Fore.GREEN))
        else:
            error("Error updating mod index.")

    def do_install(self, args):
        """Install a mod."""
        if not self.game_path:
            warning(
                'Hollow Knight not found! Please set the path by command "gamepath path/to/game/".'
            )
            return
        parser = ArgumentParser(
            prog="install",
            description="Install a mod.",
        )
        parser.add_argument("mod", help="Mod name to install.")
        args = parser.parse_args(args.split())
        if not args.mod:
            error("Please provide a mod name.")
            return
        info(f"Installing mod {args.mod.replace('+',' ')}...")
        if hkmm.install_mod(self.game_path, args.mod.replace("+", " ")) == 0:
            success("Mod installed successfully!")
        else:
            error("Error installing mod.")


if __name__ == "__main__":
    HKMM().cmdloop()
