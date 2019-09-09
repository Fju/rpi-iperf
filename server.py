# Server program
# This program will query the client(s) in regular intervals

# the file client.py has more comments regarding the these modules
import asyncio
import subprocess
import argparse
from protocol import *


PORT = 3000


loop = asyncio.get_event_loop()

# global client list
clients = []

async def query_client(ip):
	reader, writer = await asyncio.open_connection(ip, PORT, loop=loop)
	
	writer.write(QUERY_IPERF)
	writer.write_eof()

	await writer.drain()
	
	# response code auslesen
	res = await reader.read(1)

	# daten auslesen, leer falls nur response code gesendet wird
	data = await reader.read()

	if res == RESPONSE_OK:
		print(data.decode())
	else:
		print("fehler")

	writer.close()

# perform a nmap scan to find all devices in the local network
# that listen for TCP packages on the port 3000
async def list_clients():
	# this is important
	global clients

	# execute nmap script
	result = subprocess.run(["./scripts/nmap.sh"], capture_output=True)
	if result.returncode == 0:
		# reset client list
		clients = []
		for c in result.stdout.decode().split("\n"):
			if c == "":
				# skip invalid fields
				continue
			# save ip and hostname
			ip, hostname = c.split(" ")
			print("Found client %s (%s)" % (hostname, ip))
			clients.append([ip, hostname])

# go through all known clients and send a iperf query
async def query_all():
	for client in clients:
		print("querying %s" % client[1])
		await query_client(client[0])


async def do_loop():
	# run forever
	while True:
		print("Start new cycle")
		try:
			await list_clients()
			await query_all()
			# wait 5 seconds, because why not	
			await asyncio.sleep(5)
		except Exception as e:
			# prints the exception but the loop will continue
			# except there is an interrupt by the keyboard
			print(e)

try:
	# this asynchronous function will run forever
	loop.run_until_complete(do_loop())
except KeyboardInterrupt:
	# Ctrl+C was pressed
	loop.close()
	print("Ende im Gelände")


