from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from time import sleep, time
from threading import Thread
import threading

import wx

pMod = api.protoModules[api.protoVersion1]

class NetStatSnmp (Thread):
    def __init__(self, ifname):
        Thread.__init__(self)
        self._ifname = ifname
        self._host = 'localhost'
        self._port = 161
        self._agent = 'public'
        self._interval = 5
        self._stop = threading.Event()
        self._CbLastChange = None
        self._CbInOctets = None
        self._CbInUnicastPkts = None
        self._CbInNUnicastPkts = None
        self._CbInDiscard = None
        self._CbInErrors = None
        self._CbInUnknownProtos = None
        self._CbOutOctets = None
        self._CbOutUnicastPkts = None
        self._CbOutNUnicastPkts = None
        self._CbOutDiscard = None
        self._CbOutErrors = None

    def SetHost(self, host):
        self._host = host

    def SetPort(self, port):
        self._port = port

    def SetAgent(self, agent):
        self._agent = agent

    def SetInterval(self, interval):
        self._interval = interval

    def Stop(self):
        self._stop.set()
        self.join()

    def _IsStopped(self):
        return self._stop.isSet()

    def EnableLastChange(self, cb):
        self._CbLastChange = cb
    
    def EnableInOctets(self, cb):
        self._CbInOctets = cb

    def EnableInUnicastPkts(self, cb):
        self._CbInUnicastPkts = cb

    def EnableInNUnicastPkts(self, cb):
        self._CbInNUnicastPkts = cb

    def EnableInDiscards(self, cb):
        self._CbInDiscards = cb

    def EnableInErrors(self, cb):
        self._CbInErrors = cb

    def EnableInUnknownProtos(self, cb):
        self._CbInUnknownProtos = cb

    def EnableOutOctets(self, cb):
        self._CbOutOctets = cb

    def EnableOutUnicastPkts(self, cb):
        self._CbOutUnicastPkts = cb

    def EnableOutNUnicastPkts(self, cb):
        self._CbOutNUnicastPkts = cb

    def EnableOutDiscards(self, cb):
        self._CbOutDiscards = cb

    def EnableOutErrors(self, cb):
        self._CbOutErrors = cb

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
        if self._CbLastChange != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,9,self.SNMPIndex), pMod.Null()))
        if self._CbInOctets != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,10,self.SNMPIndex), pMod.Null()))
        if self._CbInUnicastPkts != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,11,self.SNMPIndex), pMod.Null()))
        if self._CbInNUnicastPkts != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,12,self.SNMPIndex), pMod.Null()))
        if self._CbInDiscard != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,13,self.SNMPIndex), pMod.Null()))
        if self._CbInErrors != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,14,self.SNMPIndex), pMod.Null()))
        if self._CbInUnknownProtos != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,15,self.SNMPIndex), pMod.Null()))
        if self._CbOutOctets != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,16,self.SNMPIndex), pMod.Null()))
        if self._CbOutUnicastPkts != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,17,self.SNMPIndex), pMod.Null()))
        if self._CbOutNUnicastPkts != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,18,self.SNMPIndex), pMod.Null()))
        if self._CbOutDiscard != None:
            pduList.append(((1,3,6,1,2,1,2,2,1,19,self.SNMPIndex), pMod.Null()))
        if self._CbOutErrors != None:
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

        while not self._IsStopped():
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
                        try:
                            if oid == (1,3,6,1,2,1,2,2,1,9,self.SNMPIndex) and self._CbLastChange != None:
                                self._CbLastChange(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,10,self.SNMPIndex) and self._CbInOctets != None:
                                self._CbInOctets(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,11,self.SNMPIndex) and self._CbInUnicastPkts != None:
                                self._CbInUnicastPkts(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,12,self.SNMPIndex) and self._CbInNUnicastPkts != None:
                                self._CbInNUnicastPkts(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,13,self.SNMPIndex) and self._CbInDiscard != None:
                                self._CbInDiscard(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,14,self.SNMPIndex) and self._CbInErrors != None:
                                self._CbInErrors(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,15,self.SNMPIndex) and self._CbInUnknownProtos != None:
                                self._CbInUnknownProtos(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,16,self.SNMPIndex) and self._CbOutOctets != None:
                                self._CbOutOctets(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,17,self.SNMPIndex) and self._CbOutUnicastPkts != None:
                                self._CbOutUnicastPkts(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,18,self.SNMPIndex) and self._CbOutNUnicastPkts != None:
                                self._CbOutNUnicastPkts(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,19,self.SNMPIndex) and self._CbOutDiscard != None:
                                self._CbOutDiscard(self._ifname, oid, val)
                            elif oid == (1,3,6,1,2,1,2,2,1,20,self.SNMPIndex) and self._CbOutErrors != None:
                                self._CbOutErrors(self._ifname, oid, val)
                        except wx.PyDeadObjectError, err: pass
                transportDispatcher.jobFinished(1)
        return wholeMsg

