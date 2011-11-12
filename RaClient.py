import socket
import sys

class RaClient:

    AR1 = 'radvd-an1'
    AR2 = 'radvd-an2'

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = False
        self._connected = False
        self._ar1_running = False
        self._ar2_running = False
        self._status_cb = None

    def SetStatusCb(self, cb):
        self._status_cb = cb

    def Connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((self._host, self._port))
        except socket.error:
            print 'Unable to connect to RA server at ' + self._host + ':' + str(self._port)
            self._sock.close()
            self._connected= False
            return
        self._connected= True

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
        if self._status_cb != None:
            self._status_cb(self._ar1_running, self._ar2_running)

    def SendStart(self, ar):
        if not self._connected:
            return
        self._sock.send("START|" + str(ar) + "\n")
        data = self._sock.recv(512)
        self._ParseStatus(data)
    
    def SendStop(self, ar):
        if not self._connected:
            return
        self._sock.send("STOP|" + str(ar) + "\n")
        data = self._sock.recv(512)
        self._ParseStatus(data)

    def SendGet(self):
        if not self._connected:
            return
        self._sock.send("GET\n")
        data = self._sock.recv(512)
        self._ParseStatus(data)
 
    def Close(self):
        if not self._connected:
            return
        
        self._sock.close()
        self._connected = False

    def IsAr1Running(self):
        return self._ar1_running
    
    def IsAr2Running(self):
        return self._ar2_running

