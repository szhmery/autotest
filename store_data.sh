#!/bin/bash

array=()

for i in {0..200}
do
array[i]=$i
done


for data in ${array[@]}
do
    echo ${data}
done