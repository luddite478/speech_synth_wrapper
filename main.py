import json
from synth_handler import synthesize
import socket
import threading

localIP     = "127.0.0.1"
localPort   = 9999
bufferSize  = 4096

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")


while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    request = json.loads(message.decode('utf-8'))
    t = threading.Thread(target=synthesize, args=(request,))
    t.start()

    # result of the thread is the file on a disk
    # so we do not need to return value
    # and join it
    # we can make heavy audio processing for many 
    # requests at the same time using threads
 
# cd ../../projects/text_to_speech && python main.py

    









