from pexpect import pxssh
import pexpect

hostname = "10.124.210.201"
username = "root"
key = '~/zhaohsun/autotest/cmts.pem'
passwd = "cisco123"
ret = -1
s = pxssh.pxssh()
s.PROMPT= '[$#] '
s.login(hostname, username, passwd, auto_prompt_reset=False)
cmd = "kubectl get pods -o wide | grep uss"
cmd = "ls"
s.sendline(cmd)   # run a command
s.prompt()
result = s.before

print result