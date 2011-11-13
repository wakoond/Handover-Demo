#!/usr/bin/env python

import wx
import numpy as num

from PlotPanel import PlotPanel
from threading import Lock

class NetStatPlotPanel (PlotPanel):
    """Plots several lines in distinct colors."""
    def __init__( self, parent, size, point_lists, clr_list, **kwargs ):
        self._inited = False
        self.parent = parent
        self._point_lists = point_lists
        self._clr_list = clr_list
        self._records = 500
        self._maximum = 200
        self._point_lists_lock = Lock()
        self._title = 'Plot Panel'
        self._xlabel = 'X'

        # initiate plotter
        PlotPanel.__init__( self, parent, size, **kwargs )
        self.SetColor( (255,255,255) )

    def SetRecords(self, records):
        self._records = records

    def SetMaximum(self, maximum):
        self._maximum = maximum

    def SetTitle(self, title):
        self._title = title

    def SetXLabel(self, xlabel):
        self._xlabel = xlabel

    def UpdatePoints(self, point_lists):
        if self._inited:
            self._point_lists_lock.acquire()
            self._point_lists = point_lists
            #print self._title + ':' + str(self._point_lists)
            self._point_lists_lock.release()
            self.Refresh()

    def draw( self ):
        """Draw data."""
        if hasattr( self, 'subplot' ):
            self.figure.clear()
            self.subplot = None
        self.subplot = self.figure.add_subplot( 111 )
           
        self._point_lists_lock.acquire()
        _self_point_lists = self._point_lists
        self._point_lists_lock.release()
        x_pts = num.array( range(0, self._records) )
        for i, pt_list in enumerate( _self_point_lists ):
            plot_pts = num.array( pt_list )
            clr = [float( c )/255. for c in self._clr_list[i]]
            self.subplot.plot( x_pts, plot_pts, color=clr, linewidth=3 )

        self.subplot.set_xlim( (0, self._records) )
        self.subplot.set_xticks( [] )
        self.subplot.set_ylim( (0, self._maximum) )
        self.subplot.set_yticks( (0, self._maximum) )
        self.subplot.set_xlabel( self._xlabel, fontsize=10 )
        self.subplot.set_title ( self._title, fontsize=10 )

        self._inited = True

