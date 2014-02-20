#!/bin/bash  

function testing1() {
	# test.txt
	echo "Sending test.txt"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 3000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -w 3000 -l 0.0
	echo ""
	echo "Sending test.txt"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 3000 bytes, Loss Rate: 10%" 
	echo ""
	python ./transfer.py -w 3000 -l 0.1
	echo ""
	echo "Sending test.txt"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 3000 bytes, Loss Rate: 20%" 
	echo ""
	python ./transfer.py -w 3000 -l 0.2
	echo ""
	echo "Sending test.txt"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 3000 bytes, Loss Rate: 50%" 
	echo ""
	python ./transfer.py -w 3000 -l 0.5
	echo ""
}

function testing2() {
	# internet-architecture.pdf
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 10000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 10000 -l 0.0
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 10000 bytes, Loss Rate: 10%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 10000 -l 0.1
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 10000 bytes, Loss Rate: 20%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 10000 -l 0.2
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 10000 bytes, Loss Rate: 50%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 10000 -l 0.5
	echo ""
}

function experiments() {
	# experiments
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 1000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 1000 -e
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 2000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 2000 -e
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 5000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 5000 -e
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 10000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 10000 -e
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 15000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 15000 -e
	echo ""
	echo "Sending internet-architecture.pdf"
	echo "Bandwidth: 10 Mbps, Propagation Delay: 10ms"
	echo "Window Size: 20000 bytes, Loss Rate: 0%" 
	echo ""
	python ./transfer.py -f internet-architecture.pdf -w 20000 -e
	echo ""
}

if [ "$1" == "testing1" ]; then
	testing1
elif [ "$1" == "testing2" ]; then
	testing2
elif [ "$1" == "experiments" ]; then
	experiments
elif [ "$1" == "all" ]; then
	testing1
	testing2
	experiments
else
	echo "Please pass argument: 'testing1', 'testing2', 'experiments', or 'all'"
fi
