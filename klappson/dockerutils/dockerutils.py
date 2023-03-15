import os
import threading
import subprocess
from time import sleep


class UserConfig:
    def __init__(self, default, user_copy, symlink):
        self.default = default
        self.user_copy = user_copy
        self.symlink = symlink
    
    def remove_symlink(self):
        if os.path.isfile(self.symlink):
            subprocess.run(['rm', '-f', self.symlink])
    
    def copy_default(self):
        if not os.path.isfile(self.user_copy):
            subprocess.run(['cp', self.default, self.user_copy])
    
    def create_symlink(self):
        subprocess.run(['ln', '-s', self.user_copy, self.symlink])


class ContainerSetup:
    def __init__(self):
        self.default_config_dir = "/root/default_configs"

        self.mount_dirs: list[str] = []
        self.symlinks: list[UserConfig] = []
        self.programs: list[list[str]] = []
        self.program_threads: list[threading.Thread] = []
    
    def _run_programms(self, start_delay=3):
        '''Start calling programms defined in self.programs
        '''
        print('\n[CONTAINERSETUP/PROGRAMMS] Running Commands...')

        for program in self.programs:
            print(
                f'[CONTAINERSETUP/PROGRAMMS]\tStarting "{" ".join(program)}"')
            
            thr = threading.Thread(
                target=subprocess.run,
                kwargs={'args': program},
                name=' '.join(program),
                daemon=False,
            )

            self.program_threads.append(thr)
            thr.start()
            sleep(start_delay)
    
    def _create_dirs(self):
        '''Create dirs defined in self.mount_dirs
        '''
        print('\n[CONTAINERSETUP/DIRS] Creating Dirs...')

        for mkdir in self.mount_dirs:
            print(f'[CONTAINERSETUP/DIRS]\tCreating "{mkdir}"')
            subprocess.run(
                ['mkdir', '-p', mkdir]
            )
    
    def _create_symlinks(self):
        '''Create the Symlinks defined in self.symlinks
        '''
        print('\n[CONTAINERSETUP/SYMLINKS] Creating Symlink...')

        for symlink in self.symlinks:
            print((
                f'[CONTAINERSETUP/SYMLINKS]\t{symlink.default} -> '
                f'{symlink.user_copy} -> {symlink.symlink}'))
            symlink.remove_symlink()
            symlink.copy_default()
            symlink.create_symlink()

    def _print_networkinfo():
        subprocess.run(['ip', 'a'])
    
    def setup(self):
        ContainerSetup._print_networkinfo()

        self._create_dirs()
        self._create_symlinks()
        self._run_programms()
