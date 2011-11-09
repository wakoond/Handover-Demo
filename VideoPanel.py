
import wx
import wx.media

class VideoPanel(wx.Panel):
    def __init__(self, parent, title, uri, **kwargs):
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        wx.Panel.__init__( self, parent, **kwargs )
        self.mc = None

        if uri != '' and uri != None:
            try:
                self.mc = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER,
                                            #szBackend=wx.media.MEDIABACKEND_DIRECTSHOW
                                            #szBackend=wx.media.MEDIABACKEND_QUICKTIME
                                            #szBackend=wx.media.MEDIABACKEND_WMP10
                                            )
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


    def DoLoadVideo(self, uri):
        if self.mc == None:
            return

        if not self.mc.LoadURI(uri):
            raise Exception("Unable to load %s: Unsupported format?" % uri)
        else:
            self.mc.SetInitialSize()
            self.mc.Play()
            self.GetSizer().Layout()
            print 'Video Loaded from ' + uri



