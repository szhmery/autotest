from pexpect import pxssh
import pexpect
import time

hostname = "10.74.21.154"
username = "root"
passwd = "ysl900h11F"
ret = -1
s = pxssh.pxssh(timeout=60)
s.PROMPT = '[root@ubuntu:~#] '
s.login(hostname, username, passwd, login_timeout=200,auto_prompt_reset=False)

cmd = "telnet 192.168.0.1"
s.sendline(cmd)   # run a command
s.prompt()
print s.before
s.sendline("root")
s.prompt()
print s.before
s.sendline("sercomm.cd1")
s.prompt()
print s.before
s.sendline("reboot")
s.prompt()
print s.before
time.sleep(1)
s.sendline("ping 192.168.2.3 -s 200")
s.prompt()
print s.before
result = s.before
print result