import subprocess
import sys
import os

executable_path = os.path.dirname(sys.executable)
print(executable_path)import subprocess
import sys
import os

module = "matplotlib"
command = [sys.executable] + f"-m pip install {module}".split()

subprocess.check_call(command)

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
