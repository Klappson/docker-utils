import os
import threading
import subprocess
from time import sleep


class UserConfig:
    def __init__(self, default, user_copy, symlink):
        self.default = default
        self.user_copy = user_copy
        self.symlink = symlink
    
    def ident_string(self):
        return (f'{self.default} -> '
                f'{self.user_copy} -> {self.symlink}')
    
    def remove_symlink(self):
        if os.path.isfile(self.symlink):
            subprocess.run(['rm', '-f', self.symlink])
    
    def copy_default(self):
        if not os.path.isfile(self.user_copy):
            par_dir = os.path.dirname(self.user_copy)
            subprocess.run(['mkdir', '-p', par_dir])
            subprocess.run(['cp', self.default, self.user_copy])
    
    def create_symlink(self):
        par_dir = os.path.dirname(self.symlink)
        subprocess.run(['mkdir', '-p', par_dir])
        subprocess.run(['ln', '-s', self.user_copy, self.symlink])


class ContainerSetup:
    def __init__(self, container_name: str):
        self.container_name = container_name.replace(' ', '_')
        self.default_config_dir = "/root/default_configs"
        self.user_config_dir = f"/vol/config/{container_name}"

        self.mount_dirs: list[str] = []
        self.symlinks: list[UserConfig] = []
        self.programs: list[list[str]] = []
        self.program_threads: list[threading.Thread] = []

    def generate_userconfigs(self):
        retu = []

        for tup in os.walk(self.default_config_dir):
            for file in tup[2]:
                default_path = os.path.join(tup[0], file)
                rel_path = default_path[len(self.default_config_dir):]

                while rel_path[0] == '/':
                    rel_path = rel_path[1:]

                user_copy = os.path.join(self.user_config_dir, rel_path)

                usco = UserConfig(
                    default=default_path,
                    user_copy=user_copy,
                    symlink=os.path.join('/', rel_path)
                )
                retu.append(usco)

                print((f"Auto-Generated UserConfig {usco.ident_string()}"))

        return retu
    
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
                f'[CONTAINERSETUP/SYMLINKS]\t{symlink.ident_string()}'))
            symlink.remove_symlink()
            symlink.copy_default()
            symlink.create_symlink()

    def _print_networkinfo():
        subprocess.run(['ip', 'a'])
    
    def setup(self):
        ContainerSetup._print_networkinfo()

        self.mount_dirs.append(self.user_config_dir)
        self._create_dirs()
        self._create_symlinks()
        self._run_programms()
