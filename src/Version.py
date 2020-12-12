import subprocess
import os
import __main__

def botVersion():
    git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode("utf-8").strip()
    main_file = os.path.relpath(__main__.__file__)
    return git_hash + "/" + main_file
