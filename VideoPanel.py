
import sys
import wx
import wx.media

from threading import Thread
import threading
from time import sleep

class VideoPanelCheckThread(Thread):
    def __init__(self, mc):
        self.mc = mc
        Thread.__init__(self)
        self._stop = threading.Event()

    def Stop(self):
        self._stop.set()
        self.join()

    def _IsStopped(self):
        return self._stop.isSet()

    def run(self):
        prev_st = wx.media.MEDIASTATE_PLAYING
        st = wx.media.MEDIASTATE_PLAYING
        while not self._IsStopped():
            st = self.mc.GetState()
            if prev_st != wx.media.MEDIASTATE_PLAYING and st != wx.media.MEDIASTATE_PLAYING:
                print 'Execute Play command again'
                self.mc.Play()
            prev_st = st
            sleep(5)

class VideoPanel(wx.Panel):
    def __init__(self, parent, title, uri, **kwargs):
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        wx.Panel.__init__( self, parent, **kwargs )
        self.mc = None

        if uri != '' and uri != None:
            backend = None
            if sys.platform == 'linux2':
                backend = wx.media.MEDIABACKEND_GSTREAMER
            elif sys.platform == 'darwin':
                backend = wx.media.MEDIABACKEND_QUICKTIME
            elif sys.platform == 'win32':
                backend = wx.media.MEDIABACKEND_DIRECTSHOW
            if backend != None:
                try:
                    self.mc = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER, szBackend = backend)
                except NotImplementedError:
                    self.Destroy()
                    raise

        sizer = wx.BoxSizer(wx.VERTICAL)

        if self.mc != None:
            sizer.Add(wx.StaticText(self, wx.ID_ANY, title + " " + uri, style=wx.ALIGN_CENTRE), 0, wx.ALIGN_CENTER_HORIZONTAL)
            sizer.Add(self.mc, 2, wx.EXPAND)
        else:
            sizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(sizer)

        if self.mc != None:
            wx.CallAfter(self.DoLoadVideo, uri)
            self.mc.Bind(wx.media.EVT_MEDIA_STATECHANGED, self.OnStateChange)

    def DoLoadVideo(self, uri):
        if self.mc == None:
            return

        if not self.mc.LoadURI(uri):
            raise Exception("Unable to load %s: Unsupported format?" % uri)
        else:
            self.mc.SetInitialSize()
            self.mc.Play()
            self.chkth = VideoPanelCheckThread(self.mc)
            self.chkth.start()
            self.GetSizer().Layout()
            print 'Video Loaded from ' + uri

    def OnStateChange(self, evt):
        st = self.mc.GetState()

        if st == wx.media.MEDIASTATE_STOPPED:
            print 'New video state: STOPPED'
            self.mc.Play()
        elif st == wx.media.MEDIASTATE_PAUSED:
            print 'New video state: PAUSED'
            self.mc.Play()
        elif st == wx.media.MEDIASTATE_PLAYING:
            print 'New video state: PLAYING'
        else:
            print 'New video state: unknown(' + str(st) + ')'

    def Close(self):
        if hasattr(self, 'chkth'):
            self.chkth.Stop()

