#!/bin/bash


for i in {1..5}
do
    DATE=`date +%F%T | awk '{print $1}' | sed 's/-//g' | sed 's/://g' `
    echo $DATE

    echo "Start to capture files for BWR upstream latency!"
    tcpdump -i ens192 'udp port 2152 and dst host 192.168.2.3' -c 200 -w bm-ccmts-capture-files/wan-ens192-$DATE.pcap &
    tcpdump -i ens256 'udp port 2152 and dst host 192.168.2.3' -c 200 -w bm-ccmts-capture-files/eNB-ens256-$DATE.pcap &
    sleep 10
    ENABLE_STR="enable"
    if [ "$1" == "$ENABLE_STR" ]; then
        #cat /dev/null > ../cdf/enable_mbwr.txt
        FILENAME="../cdf/enable_mbwr.txt"
        echo "clear enable file."
    else
        #cat /dev/null > ../cdf/disable_mbwr.txt
        FILENAME="../cdf/disable_mbwr.txt"
        echo "clear disable file."
    fi
    pcap_latency_analyzer/pcap_latency --latency-histo --disable-mmap  --file-diff  bm-ccmts-capture-files/eNB-ens256-$DATE.pcap bm-ccmts-capture-files/wan-ens192-$DATE.pcap --store-file $FILENAME --packet-trace

done

#echo "Start to capture files for normal upstream latency!"
#tcpdump -i ens192 'icmp and dst host 192.168.2.3' -c 201 -w normal-cpe-capture-files/intelcm-wan-ens192-$DATE.pcap &
#tcpdump -i ens256 'icmp and dst host 192.168.2.3' -c 201 -w normal-cpe-capture-files/intelcm-cpe-ens256-$DATE.pcap &
#sleep 20
#pcap_latency_analyzer/pcap_latency --latency-histo --file-diff  normal-cpe-capture-files/intelcm-cpe-ens256-$DATE.pcap normal-cpe-capture-files/intelcm-wan-ens192-$DATE.pcap --store-file ../cdf/disable_mbwr.txt --packet-trace

#tcpdump -i ens192 'udp port 1234 and dst host 192.168.2.3' -c 201 -w normal-cpe-capture-files/intelcm-wan-ens192-$DATE.pcap &
#tcpdump -i ens256 'udp port 1234 and dst host 192.168.2.3' -c 201 -w normal-cpe-capture-files/intelcm-cpe-ens256-$DATE.pcap &
#sleep 10
#pcap_latency_analyzer/pcap_latency --latency-histo --disable-mmap --file-diff  normal-cpe-capture-files/intelcm-cpe-ens256-$DATE.pcap normal-cpe-capture-files/intelcm-wan-ens192-$DATE.pcap --store-file disable_mbwr.txt

echo "Capture finished!"



#echo "Start to draw PDF/CDF..."

#python ../cdf/cdf.py