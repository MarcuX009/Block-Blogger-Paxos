compile:

client1: 
	python3 -u client.py P1
client2: 
	python3 -u client.py P2
client3: 
	python3 -u client.py P3
client4: 
	python3 -u client.py P4
client5: 
	python3 -u client.py P5

clear:
	rm -rf __pycache__
	rm -f P1_log.txt
	rm -f P2_log.txt
	rm -f P3_log.txt
	rm -f P4_log.txt
	rm -f P5_log.txt