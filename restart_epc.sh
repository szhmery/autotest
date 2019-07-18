#!/bin/bash

echo "Stop mme!"

MME_ID=$(ps -axu | grep mme | awk '{print $2}' )
echo $MME_ID

for ID in $MME_ID
    do
    echo $ID
    RESULT=`kill -9 $ID`
    echo $RESULT
done
echo "Run mme again!"
/root/zhaohsun/epc/openair-cn/scripts/run_mme > mme.log &
