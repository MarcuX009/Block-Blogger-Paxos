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
	
	rm -f P1_BC.json
	rm -f P2_BC.json
	rm -f P3_BC.json
	rm -f P4_BC.json
	rm -f P5_BC.json

	rm -f P1_info.json
	rm -f P2_info.json
	rm -f P3_info.json
	rm -f P4_info.json
	rm -f P5_info.json
	
	rm -f P1_blog.json
	rm -f P2_blog.json
	rm -f P3_blog.json
	rm -f P4_blog.json
	rm -f P5_blog.json