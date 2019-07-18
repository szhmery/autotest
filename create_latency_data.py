import os
import random
import time

enable_file = '/root/zhaohsun/autotest/enable_bwr.txt'
disable_file = "/root/zhaohsun/autotest/disable_bwr.txt"
while 1:
    random_1 = random.uniform(0,1.4)
    e_data = 1.500+random_1/2
    e_data = round(e_data,3)
    random_2 = random.uniform(0,2)
    d_data = 5.500+random_2/1
    d_data = round(d_data,3)
    print(e_data, d_data)

    with open(enable_file,'w+') as f:
        print(f.read())
        f.write(str(e_data))


    with open(disable_file,'w+') as f:
        print(f.read())
        f.write(str(d_data))
    time.sleep(60)
