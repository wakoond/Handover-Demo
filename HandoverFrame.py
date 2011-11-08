
import wx
import sys
import numpy as num

from NetStatCore import NetStatCore, NetStatData
from NetStatPlotPanel import NetStatPlotPanel


class HandoverFrame (wx.Frame):
    def __init__(self, app, title, records, maximum):
        self.app = app
        wx.Frame.__init__(self, None, wx.ID_ANY, title=title)
 
        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
 
        title = wx.StaticText(self.panel, wx.ID_ANY, title, style=wx.RIGHT)
 
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

        ar1RaStart = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStart)
        ar1RaStart.Hide()
        ar2RaStart = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStart)
        ar2RaStart.Hide()
        ar1RaStop = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStop)
        ar1RaStop.Hide()
        ar2RaStop = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStop)
        ar2RaStop.Hide()

        topSizer        = wx.BoxSizer(wx.VERTICAL)
        titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        plotSizer       = wx.BoxSizer(wx.HORIZONTAL)
        ar1Sizer        = wx.BoxSizer(wx.VERTICAL)
        ar2Sizer        = wx.BoxSizer(wx.VERTICAL)
        ctrlSizer       = wx.BoxSizer(wx.HORIZONTAL)
        
        titleSizer.Add(title, 0, wx.ALL, 5)

        plotSizer.Add(self.plotAr1, 0, wx.ALIGN_CENTER|wx.EXPAND, 5)
        self.plotAr1.setSizer(plotSizer)
        plotSizer.Add(self.plotAr2, 0, wx.ALIGN_CENTER|wx.EXPAND, 5)
        self.plotAr2.setSizer(plotSizer)

        ar1Sizer.Add(btnAr1Enable, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        ar1Sizer.Add(btnAr1Auto, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        ar1Sizer.Add(ar1RaStart, 0, wx.ALL|wx.ALIGN_CENTER, 20)
        ar1RaStart.Show()
        
        ar2Sizer.Add(btnAr2Enable, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        ar2Sizer.Add(btnAr2Auto, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        ar2Sizer.Add(ar2RaStart, 0, wx.ALL|wx.ALIGN_CENTER, 20)
        ar2RaStart.Show()

        ctrlSizer.Add(ar1Sizer, 0, wx.ALIGN_LEFT, 5)
        ctrlSizer.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Video'), 0, wx.ALIGN_CENTER|wx.EXPAND, 5)
        ctrlSizer.Add(ar2Sizer, 0, wx.ALIGN_RIGHT, 5)

        topSizer.Add(titleSizer, 0,wx.ALIGN_CENTER|wx.EXPAND)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALIGN_CENTER|wx.EXPAND, 5)
        topSizer.Add(plotSizer, 0, wx.ALIGN_CENTER|wx.EXPAND, 5)
        topSizer.Add(ctrlSizer, 0, wx.ALIGN_CENTER|wx.EXPAND, 5)

        self.SetSizeHints(500,600,750,800)
        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)        

        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)


    def Ar1PlotDataTrigger(self, ifname, dtype, data):
        self.plotAr1.Update([data])
    
    def Ar2PlotDataTrigger(self, ifname, dtype, data):
        self.plotAr2.Update([data])

    def SetAr1Interface(self, ifname):
        self.nsc.AddData(ifname, NetStatData.IN_OCTETS, self.Ar1PlotDataTrigger)
    
    def SetAr2Interface(self, ifname):
        self.nsc.AddData(ifname, NetStatData.IN_OCTETS, self.Ar2PlotDataTrigger)

    def Start(self, host, port, agent):
        self.nsc.SetHost(host)
        self.nsc.SetPort(port)
        self.nsc.SetAgent(agent)
        self.nsc.Start()

    def onCloseWindow(self, evt):
        print 'Quiting...'
        self.nsc.Stop()
        self.Destroy()
        sys.exit(0)

