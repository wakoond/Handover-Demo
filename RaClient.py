import socket
import sys

class RaClient:

    AR1 = 'radvd-ar1'
    AR2 = 'radvd-ar2'

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = False
        self._ar1_running = False
        self._ar2_running = False

    def Connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))

    def _ParseStatus(self, data):
        tokens = data.split('|')
        if len(tokens) < 5:
            raise Exception("Invalid reply format")
        if tokens[0] != 'STATUS':
            raise Exception("Not a STATUS message")
        for i in range(1, 4, 2):
            if tokens[i] == RaClient.AR1:
                if tokens[i+1] == 'stopped':
                    self._ar1_running = False
                elif tokens[i+1] == 'running':
                    self._ar1_running = True
            if tokens[i] == RaClient.AR2:
                if tokens[i+1] == 'stopped':
                    self._ar2_running = False
                elif tokens[i+1] == 'running':
                    self._ar2_running = True
        print 'Running: AR1 ' + str(self._ar1_running) + " AR2 " + str(self._ar2_running)

    def SendStart(self, ar):
        self._sock.send("START|" + str(ar) + "\n")
        data = self._sock.recv(512)
        self._ParseStatus(data)
    
    def SendStop(self, ar):
        self._sock.send("STOP|" + str(ar) + "\n")
        data = self._sock.recv(512)
        self._ParseStatus(data)

    def SendGet(self, ar):
        self._sock.send("GET\n")
        data = self._sock.recv(512)
        self._ParseStatus(data)
 
    def Close(self):
        self._sock.close()

    def IsAr1Running(self):
        return self._ar1_running
    
    def IsAr2Running(self):
        return self._ar2_running

