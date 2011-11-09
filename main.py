#!/usr/bin/env python

import sys
import getopt

from NetStatSnmp import NetStatSnmp
from HandoverFrame import HandoverFrame
from HandoverApp import HandoverApp

def usage(txt = None):
    print 'Usage: ' + sys.argv[0]+ ' [hHPAIJpwh]'
    print
    print '-h --help            Display this text'
    print '-H --host            Set SNMP host'
    print '-P --port            Set SNMP port'
    print '-A --agent           Set SNMP agent name'
    print '-I --interface-ar1   Set AR1 interface for SNMP get'
    print '-J --interface-ar2   Set AR2 interface for SNMP get'
    print '-p --ra-port         Set radvd server port (to enable/disable radvd service)'
    print '-w --width           Set width of diagram (in records num)'
    print '-m --maximum         Set maximum of diagram (in octets)'
    print '-V --video           Set video URI'
    if txt != None:
        print
        print txt

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hH:P:A:I:J:p:w:m:V:", ["help", "host=", "port=", "agent=", "interface-ar1=", "interface-ar2", "ra-port=", "width=", "maximum=", "video="])
    except getopt.GetoptError, err:
        usage()
        exit(1)
   
    host = 'localhost'
    port = 161
    agent = 'public'
    if_ar1 = ''
    if_ar2 = ''
    ra_port = 162
    records = 200
    maximum = 10000
    video = None
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            exit(0)
        elif o in ("-H", "--host"):
            host = a
        elif o in ("-P", "--port"):
            port = int(a)
        elif o in ("-A", "--agent"):
            agent = a
        elif o in ("-I", "--interface-ar1"):
            if_ar1 = a
        elif o in ("-J", "--interface-ar2"):
            if_ar2 = a
        elif o in ("-p", "--ra-port"):
            ra_port = int(a)
        elif o in ("-w", "--width"):
            records = int(a)
        elif o in ("-m", "--maximum"):
            maximum = int(a)
        elif o in ("-V", "--video"):
            video = a

    if if_ar1 == '' or if_ar2 == '':
        usage('Need to specify interfaces for AR1 and AR2')
        exit(1)

    app = HandoverApp()
    frame = HandoverFrame(app, 'Handover Demo v0.1', records, maximum, video)
    frame.Show()
    frame.SetAr1Interface(if_ar1)
    frame.SetAr2Interface(if_ar2)
    frame.Start(host, port, agent, ra_port)
    app.MainLoop()


