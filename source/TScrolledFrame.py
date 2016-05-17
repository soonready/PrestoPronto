
'''TScrolledFrame is a themed ScrolledFrame widget for Tkinter. Send feedback
and bug reports to Michael Lange <klappnase (at) freakmail (dot) de>

For the most part the code is stolen from the Python Mega Widget's
Pmw.ScrolledFrame widget. Pmw was originally written by Greg McFarlane and is
available at http://pmw.sourceforge.net .
Also most of the documentation is stolen from
http://pmw.sourceforge.net/doc/ScrolledFrame.html .

Pmw copyright:

Copyright 1997-1999 Telstra Corporation Limited, Australia Copyright 2000-2002
Really Good Software Pty Ltd, Australia

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import ttk
from types import StringType

class TScrolledFrame(ttk.Frame):
    '''A scrolled frame consists of a scrollable interior frame within a
    clipping frame. The programmer can create other widgets within the interior
    frame. If the frame becomes larger than the surrounding clipping frame, the
    user can position the frame using the horizontal and vertical scrollbars.
    The scrollbars can be dynamic, which means that a scrollbar will only be
    displayed if it is necessary. That is, if the frame is smaller than the
    surrounding clipping frame, the scrollbar will be hidden.
    OPTIONS:
        horizflex - Specifies how the width of the scrollable interior frame
                    should be resized relative to the clipping frame.
                    If 'fixed', the interior frame is set to the natural width,
                    as requested by the child widgets of the frame. If 'expand'
                    and the requested width of the interior frame is less than
                    the width of the clipping frame, the interior frame expands
                    to fill the clipping frame. If 'shrink' and the requested
                    width of the interior frame is more than the width of the
                    clipping frame, the interior frame shrinks to the width of
                    the clipping frame. If 'elastic', the width of the interior
                    frame is always set to the width of the clipping frame. The
                    default is 'expand'.
        vertflex  - Specifies how the height of the scrollable interior frame
                    should be resized relative to the clipping frame.
                    If 'fixed', the interior frame is set to the natural height,
                    as requested by the child widgets of the frame. If 'expand'
                    and the requested height of the interior frame is less than
                    the height of the clipping frame, the interior frame expands
                    to fill the clipping frame. If 'shrink' and the requested
                    height of the interior frame is more than the height of the
                    clipping frame, the interior frame shrinks to the height of
                    the clipping frame. If 'elastic', the height of the interior
                    frame is always set to the height of the clipping frame. The
                    default is 'expand'.
        hscrollmode - The horizontal scroll mode. If 'none', the horizontal
                    scrollbar will never be displayed. If 'static', the
                    scrollbar will always be displayed. If 'dynamic', the
                    scrollbar will be displayed only if necessary. The default
                    is 'dynamic'.
        vscrollmode - The vertical scroll mode. If 'none', the vertical
                    scrollbar will never be displayed. If 'static', the
                    scrollbar will always be displayed. If 'dynamic', the
                    scrollbar will be displayed only if necessary. The default
                    is 'dynamic'.
        hfraction - The fraction of the width of the clipper frame to scroll the
                    interior frame when the user clicks on the horizontal
                    scrollbar arrows. The default is 0.05.
        vfraction - The fraction of the height of the clipper frame to scroll
                    the interior frame when the user clicks on the vertical
                    scrollbar arrows. The default is 0.05.
        scrollmargin - Initialisation option. The distance between the
                    scrollbars and the clipping frame. The default is 1.
        usehullsize - Initialisation option. If true, the size of the megawidget
                    is determined solely by the width and height options of the
                    hull component. Otherwise, the size of the megawidget is
                    determined by the width and height of the clipper component,
                    along with the size and/or existence of the other components,
                    such as the scrollbars. All these affect the overall size of
                    the megawidget. The default is True.
    COMPONENTS:
        frame -     The frame within the clipper to contain the widgets to be
                    scrolled.
        clipper -   The frame which is used to provide a clipped view of the
                    frame component.
        hbar -      The horizontal scrollbar.
        vbar -      The vertical scrollbar.
    METHODS:
        component(which) - Return the subwidget instance WHICH. WHICH may be one
                    of "frame", "clipper", "hbar", "vbar".
        frame() - Return the frame within which the programmer may create
                    widgets to be scrolled. This is the same as component('frame').
        reposition() - Update the position of the frame component in the clipper
                    and update the scrollbars.
                    Usually, this method does not need to be called explicitly,
                    since the position of the frame component and the scrollbars
                    are automatically updated whenever the size of the frame or
                    clipper components change or the user clicks in the
                    scrollbars. However, if horizflex or vertflex is 'expand',
                    the megawidget cannot detect when the requested size of the
                    frame increases to greater than the size of the clipper.
                    Therefore, this method should be called when a new widget
                    is added to the frame (or a widget is increased in size)
                    after the initial megawidget construction.
        xview(mode = None, value = None, units = None) - Query or change the
                    horizontal position of the scrollable interior frame. If
                    mode is None, return a tuple of two numbers, each between
                    0.0 and 1.0. The first is the position of the left edge of
                    the visible region of the contents of the scrolled frame,
                    expressed as a fraction of the total width of the contents.
                    The second is the position of the right edge of the visible
                    region.
                    If mode == 'moveto', adjust the view of the interior so that
                    the fraction value of the total width of the contents is
                    off-screen to the left. The value must be between 0.0 and 1.0.
                    If mode == 'scroll', adjust the view of the interior left or
                    right by a fixed amount. If what is 'units', move the view
                    in units of horizfraction. If what is pages, move the view
                    in units of the width of the scrolled frame. If value is
                    positive, move to the right, otherwise move to the left.
        yview(mode = None, value = None, units = None) - Query or change the
                    vertical position of the scrollable interior frame. If mode
                    is None, return a tuple of two numbers, each between 0.0 and
                    1.0. The first is the position of the top edge of the
                    visible region of the contents of the scrolled frame,
                    expressed as a fraction of the total height of the contents.
                    The second is the position of the bottom edge of the visible
                    region.
                    If mode == 'moveto', adjust the view of the interior so that
                    the fraction value of the total height of the contents is
                    off-screen to the top. The value must be between 0.0 and 1.0.
                    If mode == 'scroll', adjust the view of the interior up or
                    down by a fixed amount. If what is 'units', move the view in
                    units of vertfraction. If what is pages, move the view in
                    units of the height of the scrolled frame. If value is
                    positive, move to down, otherwise move up.
'''

    def __init__(self, master=None, hscrollmode='dynamic', vscrollmode='dynamic',
                                    horizflex='expand', vertflex='expand',
                                    hfraction=0.05, vfraction=0.05,
                                    usehullsize=True, scrollmargin=1, **kw):
        if not kw.has_key('width'):
            kw['width'] = 400
        if not kw.has_key('height'):
            kw['height'] = 300
        ttk.Frame.__init__(self, master, **kw)

        self._scrolledframe_opts = {'hscrollmode' : hscrollmode,
                                    'vscrollmode' : vscrollmode,
                                    'horizflex' : horizflex,
                                    'vertflex' : vertflex,
                                    'hfraction' : hfraction,
                                    'vfraction' : vfraction,
                                    'usehullsize' : usehullsize,
                                    'scrollmargin' : scrollmargin
                                    }

        self._clipper = ttk.Frame(self, width=400, height=300)
        self._clipper.grid(row=2, column=2, sticky='news')

        self.grid_rowconfigure(2, weight=1, minsize=0)
        self.grid_columnconfigure(2, weight=1, minsize=0)
        if usehullsize:
            self.grid_propagate(0)

        self._hbar = ttk.Scrollbar(self, orient='horizontal', command=self.xview)
        self._vbar = ttk.Scrollbar(self, orient='vertical', command=self.yview)

        # Initialise instance variables.
        self._hbarOn = 0
        self._vbarOn = 0
        self.scrollTimer = None
        self._scrollRecurse = 0
        self._hbarNeeded = 0
        self._vbarNeeded = 0
        self.startX = 0
        self.startY = 0
        self._flexoptions = ('fixed', 'expand', 'shrink', 'elastic')

        # Create a frame in the clipper to contain the widgets to be
        # scrolled.
        self._frame = ttk.Frame(self._clipper)

        # Whenever the clipping window or scrolled frame change size,
        # update the scrollbars.
        self._frame.bind('<Configure>', self._reposition)
        self._clipper.bind('<Configure>', self._reposition)

        # Work around a bug in Tk where the value returned by the
        # scrollbar get() method is (0.0, 0.0, 0.0, 0.0) rather than
        # the expected 2-tuple.  This occurs if xview() is called soon
        # after the ScrolledFrame has been created.
        self._hbar.set(0.0, 1.0)
        self._vbar.set(0.0, 1.0)

        self._hscrollMode()
        self._vscrollMode()
        self._horizFlex()
        self._vertFlex()

    # hackish configure() implementation
    def _configure_scrolledframe(self, option, value):
        if not self._scrolledframe_opts.has_key(option):
            raise KeyError, 'unknown option: %s' % option
        if option in ('scrollmargin', 'usehullsize'):
            raise KeyError, 'Option cannot be configured: %s' % option
        self._scrolledframe_opts[option] = value
        if option == 'hscrollmode':
            self._hscrollMode()
        elif option == 'vscrollmode':
            self._vscrollMode()
        elif option == 'horizflex':
            self._horizFlex()
        elif option == 'vertflex':
            self._vertFlex()

    def configure(self, cnf=None, **kw):
        for opt in self._scrolledframe_opts.keys():
            if not cnf is None and cnf.has_key(opt):
                self._configure_scrolledframe(opt, cnf[opt])
                del cnf[opt]
            if kw.has_key(opt):
                self._configure_scrolledframe(opt, kw[opt])
                del kw[opt]
        return ttk.Frame.configure(self, cnf, **kw)
    config = configure

    def cget(self, key):
        if key in self._scrolledframe_opts.keys():
            return self._scrolledframe_opts[key]
        return ttk.Frame.cget(self, key)
    __getitem__ = cget

    def destroy(self):
        if self.scrollTimer is not None:
            self.after_cancel(self.scrollTimer)
            self.scrollTimer = None
        ttk.Frame.destroy(self)
    # ======================================================================

    # Configuration methods.

    def _hscrollMode(self):
        # The horizontal scroll mode has been configured.

        mode = self['hscrollmode']

        if mode == 'static':
            if not self._hbarOn:
                self._toggleHorizScrollbar()
        elif mode == 'dynamic':
            if self._hbarNeeded != self._hbarOn:
                self._toggleHorizScrollbar()
        elif mode == 'none':
            if self._hbarOn:
                self._toggleHorizScrollbar()
        else:
            message = 'bad hscrollmode option "%s": should be static, dynamic, or none' % mode
            raise ValueError, message

    def _vscrollMode(self):
        # The vertical scroll mode has been configured.

        mode = self['vscrollmode']

        if mode == 'static':
            if not self._vbarOn:
                self._toggleVertScrollbar()
        elif mode == 'dynamic':
            if self._vbarNeeded != self._vbarOn:
                self._toggleVertScrollbar()
        elif mode == 'none':
            if self._vbarOn:
                self._toggleVertScrollbar()
        else:
            message = 'bad vscrollmode option "%s": should be static, dynamic, or none' % mode
            raise ValueError, message

    def _horizFlex(self):
        # The horizontal flex mode has been configured.

        flex = self['horizflex']

        if flex not in self._flexoptions:
            message = 'bad horizflex option "%s": should be one of %s' % \
                    (flex, str(self._flexoptions))
            raise ValueError, message

        self.reposition()

    def _vertFlex(self):
        # The vertical flex mode has been configured.

        flex = self['vertflex']

        if flex not in self._flexoptions:
            message = 'bad vertflex option "%s": should be one of %s' % \
                    (flex, str(self._flexoptions))
            raise ValueError, message

        self.reposition()

    # ======================================================================

    # Public methods.
    def component(self, which):
        if not which in ('hbar', 'vbar', 'clipper', 'frame'):
            raise KeyError, 'Bad value for component: %s' % which
        if which == 'hbar': return self._hbar
        if which == 'vbar': return self._vbar
        if which == 'clipper': return self._clipper
        if which == 'frame': return self._frame

    def frame(self):
        return self._frame

    # Set timer to call real reposition method, so that it is not
    # called multiple times when many things are reconfigured at the
    # same time.
    def reposition(self):
        if self.scrollTimer is None:
            self.scrollTimer = self.after_idle(self._scrollBothNow)

    # Called when the user clicks in the horizontal scrollbar.
    # Calculates new position of frame then calls reposition() to
    # update the frame and the scrollbar.
    def xview(self, mode = None, value = None, units = None):
        if type(value) == StringType:
            value = float(value)
        if mode is None:
            return self._hbar.get()
        elif mode == 'moveto':
            frameWidth = self._frame.winfo_reqwidth()
            self.startX = value * float(frameWidth)
        else: # mode == 'scroll'
            clipperWidth = self._clipper.winfo_width()
            if units == 'units':
                jump = int(clipperWidth * self['hfraction'])
            else:
                jump = clipperWidth
            self.startX = self.startX + value * jump

        self.reposition()

    # Called when the user clicks in the vertical scrollbar.
    # Calculates new position of frame then calls reposition() to
    # update the frame and the scrollbar.
    def yview(self, mode = None, value = None, units = None):

        if type(value) == StringType:
            value = float(value)
        if mode is None:
            return self._vbar.get()
        elif mode == 'moveto':
            frameHeight = self._frame.winfo_reqheight()
            self.startY = value * float(frameHeight)
        else: # mode == 'scroll'
            clipperHeight = self._clipper.winfo_height()
            if units == 'units':
                jump = int(clipperHeight * self['vfraction'])
            else:
                jump = clipperHeight
            self.startY = self.startY + value * jump

        self.reposition()

    # ======================================================================
    # ======================================================================

    # Private methods.

    def _reposition(self, event):
        self.reposition()

    def _getxview(self):

        # Horizontal dimension.
        clipperWidth = self._clipper.winfo_width()
        frameWidth = self._frame.winfo_reqwidth()
        if frameWidth <= clipperWidth:
            # The scrolled frame is smaller than the clipping window.

            self.startX = 0
            endScrollX = 1.0

            if self['horizflex'] in ('expand', 'elastic'):
                relwidth = 1
            else:
                relwidth = ''
        else:
            # The scrolled frame is larger than the clipping window.

            if self['horizflex'] in ('shrink', 'elastic'):
                self.startX = 0
                endScrollX = 1.0
                relwidth = 1
            else:
                if self.startX + clipperWidth > frameWidth:
                    self.startX = frameWidth - clipperWidth
                    endScrollX = 1.0
                else:
                    if self.startX < 0:
                        self.startX = 0
                    endScrollX = (self.startX + clipperWidth) / float(frameWidth)
                relwidth = ''

        # Position frame relative to clipper.
        self._frame.place(x = -self.startX, relwidth = relwidth)
        return (self.startX / float(frameWidth), endScrollX)

    def _getyview(self):

        # Vertical dimension.
        clipperHeight = self._clipper.winfo_height()
        frameHeight = self._frame.winfo_reqheight()
        if frameHeight <= clipperHeight:
            # The scrolled frame is smaller than the clipping window.

            self.startY = 0
            endScrollY = 1.0

            if self['vertflex'] in ('expand', 'elastic'):
                relheight = 1
            else:
                relheight = ''
        else:
            # The scrolled frame is larger than the clipping window.

            if self['vertflex'] in ('shrink', 'elastic'):
                self.startY = 0
                endScrollY = 1.0
                relheight = 1
            else:
                if self.startY + clipperHeight > frameHeight:
                    self.startY = frameHeight - clipperHeight
                    endScrollY = 1.0
                else:
                    if self.startY < 0:
                        self.startY = 0
                    endScrollY = (self.startY + clipperHeight) / float(frameHeight)
                relheight = ''

        # Position frame relative to clipper.
        self._frame.place(y = -self.startY, relheight = relheight)
        return (self.startY / float(frameHeight), endScrollY)

    # According to the relative geometries of the frame and the
    # clipper, reposition the frame within the clipper and reset the
    # scrollbars.
    def _scrollBothNow(self):
        self.scrollTimer = None

        # Call update_idletasks to make sure that the containing frame
        # has been resized before we attempt to set the scrollbars.
        # Otherwise the scrollbars may be mapped/unmapped continuously.
        self._scrollRecurse = self._scrollRecurse + 1
        self.update_idletasks()
        self._scrollRecurse = self._scrollRecurse - 1
        if self._scrollRecurse != 0:
            return

        xview = self._getxview()
        yview = self._getyview()
        self._hbar.set(xview[0], xview[1])
        self._vbar.set(yview[0], yview[1])

        self._hbarNeeded = (xview != (0.0, 1.0))
        self._vbarNeeded = (yview != (0.0, 1.0))

        # If both horizontal and vertical scrollmodes are dynamic and
        # currently only one scrollbar is mapped and both should be
        # toggled, then unmap the mapped scrollbar.  This prevents a
        # continuous mapping and unmapping of the scrollbars.
        if (self['hscrollmode'] == self['vscrollmode'] == 'dynamic' and
                self._hbarNeeded != self._hbarOn and
                self._vbarNeeded != self._vbarOn and
                self._vbarOn != self._hbarOn):
            if self._hbarOn:
                self._toggleHorizScrollbar()
            else:
                self._toggleVertScrollbar()
            return

        if self['hscrollmode'] == 'dynamic':
            if self._hbarNeeded != self._hbarOn:
                self._toggleHorizScrollbar()

        if self['vscrollmode'] == 'dynamic':
            if self._vbarNeeded != self._vbarOn:
                self._toggleVertScrollbar()

    def _toggleHorizScrollbar(self):

        self._hbarOn = not self._hbarOn

        interior = self#.origInterior
        if self._hbarOn:
            self._hbar.grid(row = 4, column = 2, sticky = 'news')
            interior.grid_rowconfigure(3, minsize = self['scrollmargin'])
        else:
            self._hbar.grid_forget()
            interior.grid_rowconfigure(3, minsize = 0)

    def _toggleVertScrollbar(self):

        self._vbarOn = not self._vbarOn

        interior = self#.origInterior
        if self._vbarOn:
            self._vbar.grid(row = 2, column = 4, sticky = 'news')
            interior.grid_columnconfigure(3, minsize = self['scrollmargin'])
        else:
            self._vbar.grid_forget()
            interior.grid_columnconfigure(3, minsize = 0)





################################################################################
################################################################################

if __name__ == '__main__':
    import Tkinter
    root = Tkinter.Tk()
    sf = TScrolledFrame(root)
    sf.pack(fill='both', expand=1)
    for x in range(30):
        for y in range(20):
            Tkinter.Entry(sf.frame(), bd=0, highlightthickness=1,
                    highlightbackground='gray50').grid(row=x, column=y)
    root.mainloop()







