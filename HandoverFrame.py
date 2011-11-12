
import wx
import sys
import numpy as num

from NetStatCore import NetStatCore, NetStatData
from NetStatPlotPanel import NetStatPlotPanel
from RaClient import RaClient
from VideoPanel import VideoPanel

class HandoverFrame (wx.Frame):
    def __init__(self, app, title, records, maximum, video_uri):
        self.app = app
        wx.Frame.__init__(self, None, wx.ID_ANY, title=title)
 
        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
 
        titleTxt = wx.StaticText(self.panel, wx.ID_ANY, title, style=wx.ALIGN_RIGHT)
 
        #points = num.zeros((1,records), dtype=num.int8)
        points = []
        for i in range(0, records):
            points.append(int(i / 2))
        points = [points]
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

        self.btnAr1Enable = wx.Button(self.panel, wx.ID_ANY, '-')
        self.btnAr1Enable.Bind(wx.EVT_BUTTON, self.OnAr1Enable)
        self.btnAr2Enable = wx.Button(self.panel, wx.ID_ANY, '-')
        self.btnAr2Enable.Bind(wx.EVT_BUTTON, self.OnAr2Enable)
        self.btnAr1Auto = wx.Button(self.panel, wx.ID_ANY, 'Automatic')
        self.btnAr2Auto = wx.Button(self.panel, wx.ID_ANY, 'Automatic')

        bmpStart = wx.EmptyBitmap(1, 1)
        bmpStart.LoadFile('start.jpg', wx.BITMAP_TYPE_ANY)
        bmpStop = wx.EmptyBitmap(1, 1)
        bmpStop.LoadFile('stop.jpg', wx.BITMAP_TYPE_ANY)

        self.ar1RaStart = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStart)
        self.ar2RaStart = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStart)
        self.ar1RaStop = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStop)
        self.ar2RaStop = wx.StaticBitmap(self.panel, wx.ID_ANY, bmpStop)

        video = VideoPanel(self.panel, "Video Stream", video_uri)

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

        self.ar1Sizer.Add(self.btnAr1Enable, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.ar1Sizer.Add(self.btnAr1Auto, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.ar1Sizer.Add(self.ar1RaStart, 0, wx.ALL|wx.ALIGN_CENTER, 20)
        self.ar1Sizer.Add(self.ar1RaStop, 0, wx.ALL|wx.ALIGN_CENTER, 20)
        
        self.ar2Sizer.Add(self.btnAr2Enable, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.ar2Sizer.Add(self.btnAr2Auto, 0, wx.ALL|wx.ALIGN_CENTER, 5)
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


        self.SetWhiteBackground()
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

    def GetAllWidgets(self):
        items = [self.panel]
        for item in self.panel.GetChildren():
            items.append(item)
            if hasattr(item, "GetChildren"):
                for child in item.GetChildren():
                    items.append(child)
        return items

    def SetWhiteBackground(self):
        widgets = self.GetAllWidgets()
        panel = widgets[0]
        for widget in widgets:
            widget.SetBackgroundColour("White")
            widget.SetForegroundColour("Balck")

    def Ar1PlotDataTrigger(self, ifname, dtype, data):
        self.plotAr1.UpdatePoints([data])
    
    def Ar2PlotDataTrigger(self, ifname, dtype, data):
        self.plotAr2.UpdatePoints([data])

    def RaStatusTrigger(self, ar1, ar2):
        if (ar1):
            self.ar1RaStart.Show()
            self.ar1RaStop.Hide()
            self.btnAr1Enable.SetLabel('Disable')
        else:
            self.ar1RaStart.Hide()
            self.ar1RaStop.Show()
            self.btnAr1Enable.SetLabel('Enable')
        if (ar2):
            self.ar2RaStart.Show()
            self.ar2RaStop.Hide()
            self.btnAr2Enable.SetLabel('Disable')
        else:
            self.ar2RaStart.Hide()
            self.ar2RaStop.Show()
            self.btnAr2Enable.SetLabel('Enable')

        self.ar1Sizer.Layout()
        self.ar2Sizer.Layout()

    def OnAr1Enable(self, evt):
        if self.btnAr1Enable.GetLabel() == 'Enable':
            self.rac.SendStart(RaClient.AR1)
        elif self.btnAr1Enable.GetLabel() == 'Disable':
            self.rac.SendStop(RaClient.AR1)

    def OnAr2Enable(self, evt):
        if self.btnAr2Enable.GetLabel() == 'Enable':
            self.rac.SendStart(RaClient.AR2)
        elif self.btnAr2Enable.GetLabel() == 'Disable':
            self.rac.SendStop(RaClient.AR2)

    def SetAr1Interface(self, ifname):
        self.nsc.AddData(ifname, NetStatData.IN_OCTETS, self.Ar1PlotDataTrigger)
    
    def SetAr2Interface(self, ifname):
        self.nsc.AddData(ifname, NetStatData.IN_OCTETS, self.Ar2PlotDataTrigger)

    def Start(self, host, port, agent, ra_host, ra_port):
        self.rac = RaClient(ra_host, ra_port)
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

