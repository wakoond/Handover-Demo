#!/usr/bin/env python

from NetStatSnmp import NetStatSnmp
from HandoverFrame import HandoverFrame
from HandoverApp import HandoverApp

if __name__ == '__main__':
    """theta = num.arange( 0, 45*2*num.pi, 0.02 )

    rad0 = (0.8*theta/(2*num.pi) + 1)
    r0 = rad0*(8 + num.sin( theta*7 + rad0/1.8 ))
    x0 = r0*num.cos( theta )
    y0 = r0*num.sin( theta )

    rad1 = (0.8*theta/(2*num.pi) + 1)
    r1 = rad1*(6 + num.sin( theta*7 + rad1/1.9 ))
    x1 = r1*num.cos( theta )
    y1 = r1*num.sin( theta )

    points = [[(xi,yi) for xi,yi in zip( x0, y0 )],
              [(xi,yi) for xi,yi in zip( x1, y1 )]]
    clrs = [[225,200,160], [219,112,147]]"""

    """nss = NetStatSnmp('eth0')
    nss.GetIfPdu()
    nss.SetInterval(10)
    nss.EnableInOctets()
    nss.EnableInUnicastPkts()
    nss.EnableInNUnicastPkts()
    #nss.run()"""

    app = HandoverApp()
    frame = HandoverFrame(app, 'Handover Demo v0.1', 300, 8000)
    frame.Show()
    frame.SetAr1Interface('eth0')
    frame.SetAr2Interface('lo')
    frame.Start('localhost', 161, 'public')
    app.MainLoop()


