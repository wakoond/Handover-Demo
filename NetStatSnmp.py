from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from time import sleep, time
from threading import Thread

pMod = api.protoModules[api.protoVersion1]

class NetStatSnmp (Thread):
    def __init__(self, ifname, poollen = 50):
        Thread.__init__(self)
        self._ifname = ifname
        self._poollen = poollen
        self._host = 'localhost'
        self._port = 161
        self._agent = 'public'
        self._interval = 5
        self._en_LastChange = False
        self._en_InOctets = False
        self._en_InUnicastPkts = False
        self._en_InNUnicastPkts = False
        self._en_InDiscard = False
        self._en_InErrors = False
        self._en_InUnknownProtos = False
        self._en_OutOctets = False
        self._en_OutUnicastPkts = False
        self._en_OutNUnicastPkts = False
        self._en_OutDiscard = False
        self._en_OutErrors = False

    def SetHost(self, host):
        self._host = host

    def SetPort(self, port):
        self._port = port

    def SetAgent(self, agent):
        self._agent = agent

    def SetInterval(self, interval):
        self._interval = interval

    def EnableLastChange(self):
        self._en_LastChange = True
    
    def EnableInOctets(self):
        self._en_InOctets = True

    def EnableInUnicastPkts(self):
        self._en_InUnicastPkts = True

    def EnableInNUnicastPkts(self):
        self._en_InNUnicastPkts = True

    def EnableInDiscards(self):
        self._en_InDiscards = True

    def EnableInErrors(self):
        self._en_InErrors = True

    def EnableInUnknownProtos(self):
        self._en_InUnknownProtos = True

    def EnableOutOctets(self):
        self._en_OutOctets = True

    def EnableOutUnicastPkts(self):
        self._en_OutUnicastPkts = True

    def EnableOutNUnicastPkts(self):
        self._en_OutNUnicastPkts = True

    def EnableOutDiscards(self):
        self._en_OutDiscards = True

    def EnableOutErrors(self):
        self._en_OutErrors = True

    def _get(self, pdu):
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
            cmdgen.CommunityData('my-agent', self._agent, 0),
            cmdgen.UdpTransportTarget((self._host, self._port)),
            pdu)

        if errorIndication:
            raise Exception(errorStatus.prettyPrint())

        for oid, val in varBinds:
            if oid == pdu:
                return val

        return nil

    def GetIfPdu(self):
        self.IfNum = self._get((1,3,6,1,2,1,2,1,0))     # Interface Number
        #print 'Interfaces: ' + str(self.IfNum)

        for ifid in range(1, self.IfNum + 1):
            name = self._get((1,3,6,1,2,1,2,2,1,2,ifid))     # Interface Descr
            if (name == self._ifname):
                self.SNMPIndex = ifid;
                break
        #print 'SNMP Index: ' + str(self.SNMPIndex)

    def GetIndex(self):
        return self._get((1,3,6,1,2,1,2,2,1,1,self.SNMPIndex))
    
    def GetType(self):
        return self._get((1,3,6,1,2,1,2,2,1,3,self.SNMPIndex))
    
    def GetMtu(self):
        return self._get((1,3,6,1,2,1,2,2,1,4,self.SNMPIndex))
    
    def GetSpeed(self):
        return self._get((1,3,6,1,2,1,2,2,1,5,self.SNMPIndex))

    def GetPhysAddress(self):
        return self._get((1,3,6,1,2,1,2,2,1,6,self.SNMPIndex))

    def GetAdminStatus(self):
        return self._get((1,3,6,1,2,1,2,2,1,7,self.SNMPIndex))

    def GetOperStatus(self):
        return self._get((1,3,6,1,2,1,2,2,1,8,self.SNMPIndex))


    def run(self):
        # Build PDU
        reqPDU =  pMod.GetRequestPDU()
        pMod.apiPDU.setDefaults(reqPDU)
        pduList = []
        if self._en_LastChange:
            pduList.append(((1,3,6,1,2,1,2,2,1,9,self.SNMPIndex), pMod.Null()))
        if self._en_InOctets:
            pduList.append(((1,3,6,1,2,1,2,2,1,10,self.SNMPIndex), pMod.Null()))
        if self._en_InUnicastPkts:
            pduList.append(((1,3,6,1,2,1,2,2,1,11,self.SNMPIndex), pMod.Null()))
        if self._en_InNUnicastPkts:
            pduList.append(((1,3,6,1,2,1,2,2,1,12,self.SNMPIndex), pMod.Null()))
        if self._en_InDiscard:
            pduList.append(((1,3,6,1,2,1,2,2,1,13,self.SNMPIndex), pMod.Null()))
        if self._en_InErrors:
            pduList.append(((1,3,6,1,2,1,2,2,1,14,self.SNMPIndex), pMod.Null()))
        if self._en_InUnknownProtos:
            pduList.append(((1,3,6,1,2,1,2,2,1,15,self.SNMPIndex), pMod.Null()))
        if self._en_OutOctets:
            pduList.append(((1,3,6,1,2,1,2,2,1,16,self.SNMPIndex), pMod.Null()))
        if self._en_OutUnicastPkts:
            pduList.append(((1,3,6,1,2,1,2,2,1,17,self.SNMPIndex), pMod.Null()))
        if self._en_OutNUnicastPkts:
            pduList.append(((1,3,6,1,2,1,2,2,1,18,self.SNMPIndex), pMod.Null()))
        if self._en_OutDiscard:
            pduList.append(((1,3,6,1,2,1,2,2,1,19,self.SNMPIndex), pMod.Null()))
        if self._en_OutErrors:
            pduList.append(((1,3,6,1,2,1,2,2,1,20,self.SNMPIndex), pMod.Null()))

        pMod.apiPDU.setVarBinds(reqPDU, pduList)
        self._reqPDU = reqPDU
        
        # Build message
        reqMsg = pMod.Message()
        pMod.apiMessage.setDefaults(reqMsg)
        pMod.apiMessage.setCommunity(reqMsg, self._agent)
        pMod.apiMessage.setPDU(reqMsg, reqPDU)

        transportDispatcher = AsynsockDispatcher()
        transportDispatcher.registerTransport(
            udp.domainName, udp.UdpSocketTransport().openClientMode()
            )
        transportDispatcher.registerRecvCbFun(self._cbRecvFun)
    
        while True:
            if not transportDispatcher.transportsAreWorking():
                transportDispatcher.sendMessage(
                    encoder.encode(reqMsg), udp.domainName, (self._host, self._port)
                    )
                transportDispatcher.jobStarted(1)
                transportDispatcher.runDispatcher()
            sleep(self._interval)

    def _cbRecvFun(self, transportDispatcher, transportDomain, transportAddress,
                wholeMsg, reqPDU=()):
        reqPDU = self._reqPDU
        while wholeMsg:
            rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
            rspPDU = pMod.apiMessage.getPDU(rspMsg)
            # Match response to request
            if pMod.apiPDU.getRequestID(reqPDU)==pMod.apiPDU.getRequestID(rspPDU):
                # Check for SNMP errors reported
                errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
                if errorStatus:
                    print errorStatus.prettyPrint()
                else:
                    for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
                        print '%s = %s' % (oid.prettyPrint(), val.prettyPrint())
                transportDispatcher.jobFinished(1)
        return wholeMsg

