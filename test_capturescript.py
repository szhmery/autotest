import subprocess
import time
import commands
import os
cmd_cli = './start_capture.sh'

print cmd_cli
result = os.system(cmd_cli)
# p = subprocess.Popen(cmd_cli ,stdin=subprocess.PIPE ,stdout=subprocess.PIPE ,stderr=subprocess.PIPE ,shell=True)
#
# p.wait()
# result = p.communicate()
print result
