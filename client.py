# Client program
# sets up a TCP server that listens on a specified port
# (the port is also used for scanning for clients in the local network)
# the client accepts certain messages, which are defined in protocol.py
# the response contains a response code, also defined in protocol.py, and optionally
# a body containing the data of the executed command.
# Since the program handles TCP messages asynchronously, it can also send a status while an iperf
# measurement is running. Which is pretty convinient.
# IMPORTANT: a message should end with EOF (end of file) character since the server reads
#            the client's response until a EOF is received. Otherwise the server will wait
#            until a timeout occurs and the message gets discarded.
#

# asyncio can be installed via: pip install -U aiohttp
# python version 3 is required!
import asyncio
# argparse and subprocess should be installed/available by default
import argparse
import subprocess

# load the constants into the global namespace so that
# protocol.QUERY_STATUS becomes just QUERY_STATUS
from protocol import *

# parse command line arguments for debugging purposes
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
parser.add_argument("--port", type=int, default=3000)

# this variable is a dictionary of all arguments
# if the argument name is specified as "--abc" the value can be
# read using `cli_args["abc"]`
cli_args = parser.parse_args()

# wrapper for `print` function
def debug(*args):
	if not(cli_args.debug):
		# prevent printing if not in debug mode
		return
	print(*args)

# message handler, called by the co-routine when there is an incoming
# TCP message on the correct port
async def handle_messages(reader, writer):
	# read request code, which is only one byte
	req = await reader.read(1)

	debug("%s: req %s" % (writer.get_extra_info("peername")[0], req.decode()))

	# check request code
	if req == QUERY_STATUS:
		# just return state
		# this can be extended of course, e. g. return whether an iperf measurement is
		# still running
		writer.write(RESPONSE_OK)
	elif req == QUERY_IPERF:
		# technically the server could also send its or any IP address, which the 
		# client will try to connect to for the iperf measurement.
		

		
		# TIP: if you want to log the output of this and further commands you could use
		# ```
		# logfile = open("path/to/logfile", "w")
		# result = subprocess.run([...], stdout=logfile)
		# ```
		# which will simply redirect/write the STDOUT of the command into the file object

		# TIP: another good practice is to write a bash script which contains all commands
		# that should be executed and then execute this script once. This simplifies checking
		# for exit code (only one check required) and reduces code complexity. However,
		# you need to keep in mind how to pass variables like iperf server IP to the script.
		# I think the best practise is to set an enviroment variable for example:
		# ``` script.sh
		# iperf3 -c $IPERF_SRV ...
		# ```
		# execute with: IPERF_SRV=192.168.0.15 ./script.sh
		# Read more: https://www.digitalocean.com/community/tutorials/how-to-read-and-set-environmental-and-shell-variables-on-a-linux-vps
		
		# this command call is NOT asynchronous
		# the program will wait until iperf returns an exit code
		result = subprocess.run(["iperf3", "-c", "iperf3-srv", "-i", "1", "-t", "5"], capture_output=True)
		if result.returncode == 0:
			writer.write(RESPONSE_OK)
			debug("Erfolgreiche iperf3 Messung")
			# send reponse
			writer.write(result.stdout)
		else:
			debug("iperf3 Messung fehlgeschlagen")
			#writer.write(result.stderr)		
	elif req == QUERY_PROVOKE_ERROR:
		# this is a debug scenario, this should NEVER make the program exit
		raise Exception("Intentional Exception")
	else:
		# let the server know that the sent command is invalid or not yet implemented
		writer.write(RESPONSE_UNKNOWN)

	# end response with EOF character and drain/flush the stream
	writer.write_eof()
	await writer.drain()

	# close the writer stream
	writer.close()
	debug("Antwort versendet")


# this basically sets up the server and attaches the handle_message function
# to the server loop
loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_messages, port=cli_args.port, loop=loop)
server = loop.run_until_complete(coro)
debug("Server läuft")

try:
	loop.run_forever()
except KeyboardInterrupt:
	# exit when Ctrl+C is pressed
	debug("Server wird geschlossen")
	server.close()
	loop.run_until_complete(server.wait_closed())
	loop.close()

