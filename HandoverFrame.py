
import wx
import sys
import numpy as num

from NetStatCore import NetStatCore, NetStatData
from NetStatPlotPanel import NetStatPlotPanel
from RaClient import RaClient
from VideoPanel import VideoPanel

class HandoverFrame (wx.Frame):
    def __init__(self, app, title, records, maximum):
        self.app = app
        wx.Frame.__init__(self, None, wx.ID_ANY, title=title)
 
        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
 
        titleTxt = wx.StaticText(self.panel, wx.ID_ANY, title, style=wx.ALIGN_RIGHT)
 
        points = num.zeros((1,records), dtype=num.int8)
        clrs = [[225,200,160]]
 
        self.plotAr1 = NetStatPlotPanel(self.panel, (350,250), points, clrs)
        self.plotAr1.SetRecords(records)
        self.plotAr1.SetMaximum(maximum)
        self.plotAr1.SetTitle('Access Router 1')
        self.plotAr1.SetXLabel('Title')
        self.plotAr2 = NetStatPlotPanel(self.panel, (350,250), points, clrs)
        self.plotAr2.SetRecords(records)
        self.plotAr2.SetMaximum(maximum)
        self.plotAr2.SetTitle('Access Router 2')
        self.plotAr2.SetXLabel('Title')

        self.nsc = NetStatCore(records)

        btnAr1Enable = wx.Button(self.panel, wx.ID_ANY, 'Enable')
        btnAr2Enable = wx.Button(self.panel, wx.ID_ANY, 'Enable')
        btnAr1Auto = wx.Button(self.panel, wx.ID_ANY, 'Automatic')
        btnAr2Auto = wx.Button(self.panel, wx.ID_ANY, 'Automatic')

        bmpStart = wx.EmptyBitmap(1, 1)
        bmpStart.LoadFile('start.jpg', wx.BITMAP_TYPE_ANY)
        bmpStop = wx.EmptyBitmap(1, 1)
        bmpStop.LoadFile('stop.jpg', wx.BITMAP_TYPE_ANY)

        self.ar1RaStart = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStart)
        self.ar2RaStart = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStart)
        self.ar1RaStop = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStop)
        self.ar2RaStop = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStop)

        video = VideoPanel(self.panel, "Video Stream", "http://172.16.162.1:8080")

        topSizer        = wx.BoxSizer(wx.VERTICAL)
        titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        plotSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.ar1Sizer   = wx.BoxSizer(wx.VERTICAL)
        self.ar2Sizer   = wx.BoxSizer(wx.VERTICAL)
        ctrlSizer       = wx.BoxSizer(wx.HORIZONTAL)
        
        titleSizer.Add(titleTxt, 1, wx.EXPAND, 5)

        plotSizer.Add(self.plotAr1, 0, wx.ALIGN_CENTER|wx.EXPAND, 5)
        self.plotAr1.setSizer(plotSizer)
        plotSizer.Add(self.plotAr2, 0, wx.ALIGN_CENTER|wx.EXPAND, 5)
        self.plotAr2.setSizer(plotSizer)

        self.ar1Sizer.Add(btnAr1Enable, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.ar1Sizer.Add(btnAr1Auto, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.ar1Sizer.Add(self.ar1RaStart, 0, wx.ALL|wx.ALIGN_CENTER, 20)
        self.ar1Sizer.Add(self.ar1RaStop, 0, wx.ALL|wx.ALIGN_CENTER, 20)
        
        self.ar2Sizer.Add(btnAr2Enable, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.ar2Sizer.Add(btnAr2Auto, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.ar2Sizer.Add(self.ar2RaStart, 0, wx.ALL|wx.ALIGN_CENTER, 20)
        self.ar2Sizer.Add(self.ar2RaStop, 0, wx.ALL|wx.ALIGN_CENTER, 20)

        ctrlSizer.Add(self.ar1Sizer, 0, wx.ALIGN_LEFT, 5)
        ctrlSizer.Add(video, 2, wx.ALIGN_CENTER_HORIZONTAL, 5)
        ctrlSizer.Add(self.ar2Sizer, 0, wx.ALIGN_RIGHT, 5)

        topSizer.Add(titleSizer, 0,wx.ALIGN_CENTER_HORIZONTAL)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND, 5)
        topSizer.Add(plotSizer, 1, wx.EXPAND, 5)
        topSizer.Add(ctrlSizer, 1, wx.EXPAND, 5)

        self.SetSizeHints(500,600,750,800)
        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)        

        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)


    def Ar1PlotDataTrigger(self, ifname, dtype, data):
        self.plotAr1.Update([data])
    
    def Ar2PlotDataTrigger(self, ifname, dtype, data):
        self.plotAr2.Update([data])

    def RaStatusTrigger(self, ar1, ar2):
        if (ar1):
            self.ar1RaStart.Show()
            self.ar1RaStop.Hide()
        else:
            self.ar1RaStart.Hide()
            self.ar1RaStop.Show()
        if (ar2):
            self.ar2RaStart.Show()
            self.ar2RaStop.Hide()
        else:
            self.ar2RaStart.Hide()
            self.ar2RaStop.Show()

        self.ar1Sizer.Layout()
        self.ar2Sizer.Layout()


    def SetAr1Interface(self, ifname):
        self.nsc.AddData(ifname, NetStatData.IN_OCTETS, self.Ar1PlotDataTrigger)
    
    def SetAr2Interface(self, ifname):
        self.nsc.AddData(ifname, NetStatData.IN_OCTETS, self.Ar2PlotDataTrigger)

    def Start(self, host, port, agent, ra_port):
        self.rac = RaClient(host, ra_port)
        self.rac.SetStatusCb(self.RaStatusTrigger)
        self.rac.Connect()
        self.rac.SendGet()

        self.nsc.SetHost(host)
        self.nsc.SetPort(port)
        self.nsc.SetAgent(agent)
        self.nsc.Start()

    def onCloseWindow(self, evt):
        print 'Quiting...'
        self.nsc.Stop()
        self.Destroy()
        sys.exit(0)

