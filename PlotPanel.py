import matplotlib
matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure

import wx

class PlotPanel (wx.Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a""" 
    """flag, and the actual resizing of the figure is triggered by an Idle event."""
    def __init__( self, parent, size, color=None, dpi=None, **kwargs ):

        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )

        # initialize matplotlib stuff
        self.figure = Figure( None, dpi )
        self.canvas = FigureCanvasWxAgg( self, -1, self.figure )
        self.SetColor( color )

        self._SetSize(size)
        #self.draw()

        self._resizeflag = False
        self._sizer = None

        self.Bind(wx.EVT_IDLE, self._onIdle)
        self.Bind(wx.EVT_SIZE, self._onSize)
        self.Bind(wx.EVT_PAINT, self._onPaint)

    def SetColor( self, rgbtuple=None ):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor( clr )
        self.figure.set_edgecolor( clr )
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )

    def _onSize( self, event ):
        self._resizeflag = True

    def _onIdle( self, evt ):
        if self._resizeflag:
            self._resizeflag = False
            self._SetSize()

    def _onPaint( self, evt ):
        self.draw()

    def _SetSize( self, size=None ):
        pixels = None
        if size:
            pixels = size
        elif self._sizer:
            sizerItem = self._sizer.GetItem(self)
            if sizerItem:
                pixels = sizerItem.GetMinSizeWithBorder().Get()
        if not pixels:
            return
        self.SetSize( pixels )
        self.canvas.SetSize( pixels )
        self.figure.set_size_inches( float(pixels[0])/self.figure.get_dpi(),
                                     float(pixels[1])/self.figure.get_dpi() )

    def setSizer (self, sizer ):
        self._sizer = sizer

    def draw(self): pass # abstract, to be overridden by child classes

