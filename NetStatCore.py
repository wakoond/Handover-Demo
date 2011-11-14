
from NetStatSnmp import NetStatSnmp

class NetStatData:
    IN_OCTETS = 10
    IN_UNICAST_PKTS = 11
    IN_N_UNICAST_PKTS = 12
    IN_DISCARD = 13
    IN_ERRORS = 14
    IN_UNKNOWN_PROTOS = 15
    OUT_OCTETS = 16
    OUT_UNICAST_PKTS = 17
    OUT_N_UNICAST_PKTS = 18
    OUT_DISCARD = 19
    OUT_ERRORS = 20

    def __init__(self, ifname, dtype, poolsize, cb):
        self._ifname = ifname
        self._dtype = dtype
        self._data = []
        self._cb = cb
        self._baseval = 0
        self._poolsize = poolsize

        for i in range(0, self._poolsize):
            self._data.append(0)

    def DtypeTriggerNeeded(self, ifname):
        if self._ifname != ifname:
            return False

        return True

    def UpdateData(self, ifname, dtype, val):
        if self._ifname != ifname:
            return
        if self._dtype != dtype:
            return

        xval = int(val)
        #print self._ifname + ' - ' + str(xval) +  ' (' + str(self._baseval) + ') = ' + str(xval - self._baseval)

        if self._baseval == 0:
            self._baseval = xval
            return

        self._data.pop(0)
        self._data.append(xval - self._baseval)
        self._baseval = xval

        self._cb(self._ifname, self._dtype, self._data)

    def GetIfname(self):
        return self._ifname

    def GetDtype(self):
        return self._dtype

class NetStatCore:
    def __init__(self, poolsize):
        self._datas = []
        self._interfaces = []
        self._nsss = []
        self._poolsize = poolsize
        self._host = 'localhost'
        self._port = 161
        self._agent = 'plublic'

    def AddData(self, ifname, dtype, cb):
        self._datas.append(NetStatData(ifname, dtype, self._poolsize, cb))
        t_if = False
        for i in self._interfaces:
            if i == ifname:
                t_if = True
                break
        if not t_if:
            self._interfaces.append(ifname)

    def SetHost(self, host):
        self._host = host

    def SetPort(self, port):
        self._port = port

    def SetAgent(self, agent):
        self._agent = agent

    def Start(self):
        for i in self._interfaces:
            print 'NetStatSnmp: ' + i
            nss = NetStatSnmp(i)
            nss.SetHost(self._host)
            nss.SetPort(self._port)
            nss.SetAgent(self._agent)
            self._nsss.append(nss)
            nss.GetIfPdu()
            print 'NetStatSnmp: ' + i + ' GetIfPdu done'
            nss.SetInterval(1)
            for d in self._datas:
                if d.DtypeTriggerNeeded(i):
                    dt = d.GetDtype()
                    if dt == NetStatData.IN_OCTETS:
                        nss.EnableInOctets(self.InOctetsTrigger)
                    elif dt == NetStatData.IN_UNICAST_PKTS:
                        nss.EnableInUnicastPkts(self.InUnicastPktsTrigger)
                    elif dt == NetStatData.IN_N_UNICAST_PKTS:
                        nss.EnableInNUnicastPkts(self.InNUnicastPktsTrigger)
                    elif dt == NetStatData.IN_DISCARD:
                        nss.EnableDiscard(self.InDiscardTrigger)
                    elif dt == NetStatData.IN_ERRORS:
                        nss.EnableInErrors(self.InErrorsTrigger)
                    elif dt == NetStatData.IN_UNKNOWN_PROTOS:
                        nss.EnableInUnknownProtos(self.InUnknownProtosTrigger)
                    elif dt == NetStatData.OUT_OCTETS:
                        nss.EnableOutOctets(self.OutOctetsTrigger)
                    elif dt == NetStatData.OUT_UNICAST_PKTS:
                        nss.EnableOutUnicastPkts(self.OutUnicastPktsTrigger)
                    elif dt == NetStatData.OUT_N_UNICAST_PKTS:
                        nss.EnableOutNUnicastPkts(self.OutNUnicastPktsTrigger)
                    elif dt == NetStatData.OUT_DISCARD:
                        nss.EnableDiscard(self.OutDiscardTrigger)
                    elif dt == NetStatData.OUT_ERRORS:
                        nss.EnableOutErrors(self.OutErrorsTrigger)
            nss.start()

    def Stop(self):
        for nss in self._nsss:
            nss.Stop()

    def InOctetsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.IN_OCTETS, val)

    def InUnicastPktsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.IN_UNICAST_PKTS, val)

    def InNUnicastPktsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.IN_N_UNICAST_PKTS, val)

    def InDiscardTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.IN_DISCARD, val)

    def InErrorsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.IN_ERRORS, val)

    def InUnknownProtosTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.IN_UNKNOWN_PROTOS, val)

    def OutOctetsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.OUT_OCTETS, val)

    def OutUnicastPktsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.OUT_UNICAST_PKTS, val)

    def OutNUnicastPktsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.OUT_N_UNICAST_PKTS, val)

    def OutDiscardTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.OUT_DISCARD, val)

    def OutErrorsTrigger(self, ifname, oid, val):
        for d in self._datas:
            d.UpdateData(ifname, NetStatData.OUT_ERRORS, val)


