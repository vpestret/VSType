
import sys, re, os.path
from PyQt4 import QtGui, QtCore, QtSvg, QtNetwork
from xml.etree import ElementTree as ET
from Tkinter import Tk # standard QT clipboard works strange with VNC client
import euclid
import math

class SingleEntity( QtGui.QApplication):
    def __init__( self, argv, id):
        QtGui.QApplication.__init__( self, argv)
        self.my_mem = QtCore.QSharedMemory( self)
        self.my_mem.setKey( id)
        if self.my_mem.attach():
            self.is_running = True
        else:
            self.is_running = False
            if not self.my_mem.create( 1):
                raise RuntimeError( 'SingleApplication.__init__: can\'t create memory')

    def isRunning(self):
        return self.is_running

class svg_parser:
    def __init__(self, file_name):
        self.rect_dict = {}
        self.href_dict = {}
        svg_root = ET.parse(file_name)
        self.parse_root(svg_root)

    def get_transform(self, attrib):
        # fill with identity matrix
        ret = euclid.Matrix3()
        # find attribute
        if 'transform' in attrib.keys():
            tr_str = attrib['transform']
        else:
            return ret
        # split
        spl_str = re.findall(r'(\s*\w+\([^\)]*\)\s*)', tr_str)
        # iterate over all transformations
        for loc_str in spl_str:
            # matrix
            match = re.search(r'\s*matrix\(([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+)'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))\)\s*', loc_str)
            if match:
                tr_a = float(match.group(1))
                tr_b = float(match.group(4))
                tr_c = float(match.group(7))
                tr_d = float(match.group(10))
                tr_e = float(match.group(13))
                tr_f = float(match.group(16))
                loc_mtx = euclid.Matrix3()
                loc_mtx.a = tr_a
                loc_mtx.b = tr_c
                loc_mtx.c = tr_e
                loc_mtx.e = tr_b
                loc_mtx.f = tr_d
                loc_mtx.g = tr_f
                ret = ret * loc_mtx
            # translate
            match = re.search(r'\s*translate\(([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+)'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))?\)\s*', loc_str)
            if match:
                tsl_x = float(match.group(1))
                tsl_y = 0.0 if match.group(4) == None else float(match.group(4))
                loc_mtx = euclid.Matrix3()
                loc_mtx.c = tsl_x
                loc_mtx.g = tsl_y
                ret = ret * loc_mtx
            # scale
            match = re.search(r'\s*scale\(([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+)'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))?\)\s*', loc_str)
            if match:
                scl_x = float(match.group(1))
                scl_y = scl_x if match.group(4)==None else float(match.group(4))
                loc_mtx = euclid.Matrix3()
                loc_mtx.a = scl_x
                loc_mtx.f = scl_y
                ret = ret * loc_mtx
            # rotate
            match = re.search(r'\s*rotate\(([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+)'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))?'+\
                        r'((\s*,\s*|\s+)([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+))?\)\s*', loc_str)
            if match:
                rot_an = float(match.group(1))
                rot_an = rot_an/180*math.pi
                loc_mtxa = euclid.Matrix3()
                loc_mtxa.a = math.cos(rot_an)
                loc_mtxa.b = -math.sin(rot_an)
                loc_mtxa.f = math.cos(rot_an)
                loc_mtxa.e = math.sin(rot_an)
                rot_x = 0.0 if match.group(4) == None else float(match.group(4))
                rot_y = 0.0 if match.group(7) == None else float(match.group(7))
                loc_mtx = euclid.Matrix3()
                loc_mtx.c = rot_x
                loc_mtx.g = rot_y
                ret = ret * loc_mtx * loc_mtxa
                loc_mtx.c = -rot_x
                loc_mtx.g = -rot_y
                ret = ret * loc_mtx
            # skewX
            match = re.search(r'\s*skewX\(([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+)\)\s*', loc_str)
            if match:
                rot_an = float(match.group(1))
                rot_an = rot_an/180*math.pi
                loc_mtxa = euclid.Matrix3()
                loc_mtxa.b = math.tan(rot_an)
                ret = ret * loc_mtxa
            # skewY
            match = re.search(r'\s*skewY\(([-+]?\d+|[-+]?\d+[.]|'+\
                              r'[-+]?[.]\d+|[-+]?\d+[.]\d+)\)\s*', loc_str)
            if match:
                rot_an = float(match.group(1))
                rot_an = rot_an/180*math.pi
                loc_mtxa = euclid.Matrix3()
                loc_mtxa.e = math.tan(rot_an)
                ret = ret * loc_mtxa

        return ret

    def transform_dicts(self, tr_mtx, hrefs, rects):
        r_hrefs = dict()
        r_rects = dict()
        for key in hrefs.keys():
            r_hrefs[key] = self.transform_points(tr_mtx, hrefs[key])
        for key in rects.keys():
            r_rects[key] = self.transform_points(tr_mtx, rects[key])
        return (r_hrefs, r_rects)
   
    def parse_root(self, svg_root):
        root = svg_root.getroot()
        (hrefs, rects) = self.parse_item(root)
        for key in hrefs.keys():
            if len(hrefs[key]) > 1:
                self.href_dict[self.bound_points(hrefs[key])] = key
        for key in rects.keys():
            if len(rects[key]) > 1:
                self.rect_dict[self.bound_points(rects[key])] = key

    def parse_item(self, item):
        hrefs = dict()
        rects = dict()
        tr_mtx = self.get_transform(item.attrib)
        # first check if there is a link
        if (re.search(r'\{.*\}a$', item.tag)):
            href = None
            for attr in item.attrib.keys():
                if re.search(r'\{.*\}href$', attr):
                    href = item.attrib[attr]
            if (href != None):
                points = self.get_points(item, False)
                hrefs[href] = points
                
            return self.transform_dicts(tr_mtx, hrefs, rects)
        # handle onckick attribute if available
        onclick_str = None
        if 'onclick' in item.attrib.keys():
            match = re.search(r'[^(]*\(\'([^\']*)\'\)', item.attrib['onclick'])
            if match and len(match.groups()) == 1:
                onclick_str = match.group(1)
        if onclick_str != None:
            print 'parse_item: onclick detected %s' % onclick_str
            points = self.get_points(item, False)
            rects[onclick_str] = points

            return self.transform_dicts(tr_mtx, hrefs, rects)
        # conventional way
        for loc_item in item:
            (loc_hrefs, loc_rects) = self.parse_item(loc_item)
            # merge
            for key in loc_hrefs.keys():
                if key in hrefs.keys():
                    hrefs[key].extend(loc_hrefs[key])
                else:
                    hrefs[key] = loc_hrefs[key]
            for key in loc_rects.keys():
                if key in rects.keys():
                    rects[key].extend(loc_rects[key])
                else:
                    rects[key] = loc_rects[key]
        # transform and return
        return self.transform_dicts(tr_mtx, hrefs, rects)

    def bound_points(self, arr):
        # protection
        if (len(arr) <=0):
            return QtCore.QRect(0,0,0,0)
        # initial value
        tr_point = arr[0]
        min_x = tr_point.x
        max_x = tr_point.x
        min_y = tr_point.y
        max_y = tr_point.y
        # process the rest
        for vect in arr:
            tr_vect = vect
            if min_x > tr_vect.x:
                min_x = tr_vect.x 
            if max_x < tr_vect.x:
                max_x = tr_vect.x 
            if min_y > tr_vect.y:
                min_y = tr_vect.y 
            if max_y < tr_vect.y:
                max_y = tr_vect.y 
        # form the output
        return QtCore.QRect(min_x,min_y,max_x-min_x,max_y-min_y)

    def transform_points(self, g_mtx, arr):
        # initial value
        ret_arr = []
        # process the rest
        for vect in arr:
            ret_arr.append(g_mtx*vect)
        # output
        return ret_arr

    def get_points(self, item, do_tr):
        if (do_tr):
            tr_mtx = self.get_transform(item.attrib)
        else:
            tr_mtx = euclid.Matrix3()
        points = []
        # scan yourself
        if (re.search(r'\{.*\}rect$', item.tag)):
            points = self.get_rect_points(item)
        elif (re.search(r'\{.*\}path$', item.tag)):
            points = self.get_path_points(item)
        # scan childs
        for loc_item in item:
            points.extend(self.get_points(loc_item, True))
        # transform everything
        return self.transform_points(tr_mtx, points)

    def get_rect_points(self, item):
        rect_x = float(item.attrib['x'])
        rect_y = float(item.attrib['y'])
        rect_w = float(item.attrib['width'])
        rect_h = float(item.attrib['height'])
        vect2tr = [euclid.Point2(rect_x, rect_y), \
                   euclid.Point2(rect_x+rect_w, rect_y), \
                   euclid.Point2(rect_x+rect_w, rect_y+rect_h), \
                   euclid.Point2(rect_x, rect_y+rect_h)]
        return vect2tr

    def get_path_points(self, item):
        return [] # not yet implemented

    def click(self, hit_point):
        # Rectangles under references
        for href in self.href_dict.keys():
            if href.contains(hit_point):
                print "Href rect hit:return %s" % self.href_dict[href]
                return [self.href_dict[href], 'href']
        # Common rectangles
        for rect in self.rect_dict.keys():
            if rect.contains(hit_point):
                print "Rect hit:return %s" % self.rect_dict[rect]
                return [self.rect_dict[rect], 'rect']
        return None
    
    def nav(self, cur_rect, direction):
        pt = cur_rect.center()
        min_detected = None
        href_rects = self.href_dict.keys()
        if (href_rects):
            href_rects.extend(self.rect_dict.keys())
            rects = href_rects
        else:
            rects = self.rect_dict.keys()
        if not(rects):
            print 'nav: No rects detected at all - stand still'
            return
        if direction == 'left':
            for rect in rects:
                pt2 = rect.center()
                dx = pt2.x() - pt.x()
                dy = pt2.y() - pt.y()
                if dx*dx + dy*dy < 10:
                    continue
                if dx < 0 and abs(dy) < abs(dx):
                    if min_detected == None:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
                    elif min_dist > dx*dx + dy*dy:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
        elif direction == 'up':
            for rect in rects:
                pt2 = rect.center()
                dx = pt2.x() - pt.x()
                dy = pt2.y() - pt.y()
                if dx*dx + dy*dy < 10:
                    continue
                if dy < 0 and abs(dx) < abs(dy):
                    if min_detected == None:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
                    elif min_dist > dx*dx + dy*dy:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
        elif direction == 'right':
            for rect in rects:
                pt2 = rect.center()
                dx = pt2.x() - pt.x()
                dy = pt2.y() - pt.y()
                if dx*dx + dy*dy < 10:
                    continue
                if dx > 0 and abs(dy) < dx:
                    if min_detected == None:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
                    elif min_dist > dx*dx + dy*dy:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
        elif direction == 'down':
            for rect in rects:
                pt2 = rect.center()
                dx = pt2.x() - pt.x()
                dy = pt2.y() - pt.y()
                if dx*dx + dy*dy < 10:
                    continue
                if dy > 0 and abs(dx) < dy:
                    if min_detected == None:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
                    elif min_dist > dx*dx + dy*dy:
                        min_dist = dx*dx + dy*dy
                        min_detected = rect
        else:
            print 'nav: Unknown direction %s - stand still' % direction
            return cur_rect

        if min_detected != None:
            return QtCore.QRectF(min_detected)
        else:
            print 'nav: No rects detected to step - stand still'
            return cur_rect

class cursor_animation(QtGui.QGraphicsItemAnimation):
    def __init__(self, svg_item):
        QtGui.QGraphicsItemAnimation.__init__(self)
        self.color = QtGui.QColor(0,0,255) # initial state
        self.pen = QtGui.QPen(self.color)
        self.pen.setWidth(2)
        self.svg_item = svg_item
        self.tl = QtCore.QTimeLine(1000)
        self.tl.setFrameRange(0, 100)
        self.tl.setLoopCount(5)
        self.setTimeLine(self.tl)
        self.connect(self.tl, QtCore.SIGNAL('finished()'), \
            self.finished_callback)
    
    def setItem(self, item_to_set):
        item_to_set.setPen(self.pen)
        QtGui.QGraphicsItemAnimation.setItem(self, item_to_set)

    def afterAnimationStep(self, step):
        self.color.setRgb(0,int(255*(0.5-abs(step-0.5))*2),\
                          int(255*abs(step-0.5)*2))
        self.pen.setColor(self.color)
        self.item().setPen(self.pen)

    def finished_callback(self):
        self.color.setRgb(0,0,255,0)
        self.pen.setColor(self.color)
        self.item().setPen(self.pen)

class svg_scene(QtGui.QGraphicsScene):
    def __init__(self):
        QtGui.QGraphicsScene.__init__(self)
        self.cursor = None
    
    def addCursor(self, item):
        cursor = cursor_animation(item)
        # first of all find if there is something to embrace with cursor
        if len(cursor.svg_item.parser.href_dict.keys()) != 0:
            rect = cursor.svg_item.parser.href_dict.keys()[0]
        elif len(cursor.svg_item.parser.rect_dict.keys()) != 0:
            rect = cursor.svg_item.parser.rect_dict.keys()[0]
        else:
            print 'nothing to embrace with cursor'
            return

        self.cursor = cursor
        self.cursor_item = QtGui.QGraphicsRectItem(QtCore.QRectF(rect))
        self.addItem(self.cursor_item)
        self.cursor.setItem(self.cursor_item)

    def focusInEvent(self, evt):
        QtGui.QGraphicsScene.focusInEvent(self, evt)
        if (self.cursor):
            self.cursor.tl.stop()
            self.cursor.tl.start()

    def focusOutEvent(self, evt):
        QtGui.QGraphicsScene.focusOutEvent(self, evt)
        if (self.cursor):
            self.cursor.tl.stop()
            self.cursor.finished_callback()

    def setCallback(self):
        if (self.cursor):
            self.cursor.tl.start()

    def unsetCallback(self):
        if (self.cursor):
            self.cursor.tl.stop()

    def keyCallback(self, e):
        if self.cursor == None:
            return

        cur_rect = self.cursor_item.rect()
        new_rect = cur_rect
        intercepted = True
        if e.key() == QtCore.Qt.Key_H:
            new_rect = self.cursor.svg_item.parser.nav(cur_rect, 'left')
        elif e.key() == QtCore.Qt.Key_J:
            new_rect = self.cursor.svg_item.parser.nav(cur_rect, 'down')
        elif e.key() == QtCore.Qt.Key_K:
            new_rect = self.cursor.svg_item.parser.nav(cur_rect, 'up')
        elif e.key() == QtCore.Qt.Key_L:
            new_rect = self.cursor.svg_item.parser.nav(cur_rect, 'right')
        elif e.key() == QtCore.Qt.Key_Space:
            self.cursor.svg_item.mouseHit(cur_rect.center())
        else:
            intercepted = False

        if intercepted:
            self.cursor.tl.stop()
            self.cursor_item.setRect(new_rect)
            self.cursor.setItem(self.cursor_item)
            self.cursor.tl.start()

class svg_item(QtSvg.QGraphicsSvgItem):
    def __init__(self, file_name):
        QtSvg.QGraphicsSvgItem.__init__(self, file_name)
        self.parser = svg_parser(file_name)

    def mousePressEvent(self, event):
        hit_point = event.pos()
        self.mouseHit(hit_point)
        event.accept()

    def mouseHit(self, hit_point):
        ret = self.parser.click(QtCore.QPoint(hit_point.x(), hit_point.y()))
        if ret:
            (ret_str, ret_type) = ret
            if ret_type == 'rect':
                self.emit(QtCore.SIGNAL("rect_hit"), ret_str)
            elif ret_type == 'href':
                self.emit(QtCore.SIGNAL("href_hit"), ret_str)
            else:
                print 'Unknown click type %s' % ret_type

class line_edit(QtGui.QLineEdit):
    def __init__(self, parent):
        QtGui.QLineEdit.__init__(self, parent)

    def focusInEvent(self, event):
        QtGui.QLineEdit.focusInEvent(self, event)
        self.emit(QtCore.SIGNAL('focusInSignal(QString)'),\
            self.displayText())

class spacekeyFilter(QtCore.QObject):
    def __init__(self, obj):
        QtCore.QObject.__init__(self, obj)
        self.bypass = obj

    def eventFilter(self,  obj,  event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Space:
                self.bypass.keyPressEvent(event)
                return True
        return False

class tabkeyFilter(QtCore.QObject):
    def __init__(self, obj):
        QtCore.QObject.__init__(self, obj)
        self.bypass = obj
        self.signal = QtCore.SIGNAL("tab_key_hit")

    def eventFilter(self,  obj,  event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Tab:
                self.emit(self.signal)
                return True
        return False

class app_view(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        # needed for obtaining clipboard
        if os.name == 'nt':
            self.tk = Tk()
            self.tk.withdraw()
        elif os.name != 'posix':
            raise RuntimeError('Unsupported os.name: %s' % os.name)
        # scenes dictionary and history
        self.oldScene = None
        self.scenes = {}
        self.scenes_history = []
        # show splash screen
        self.show_scene('resources/splash.svg')
        # buttons 
        sk_filter = spacekeyFilter(self)
        open_but = QtGui.QPushButton(QtGui.QIcon('resources/open-file.png'),\
            '', self)
        open_but.setGeometry(0,0,20,20)
        open_but.installEventFilter(sk_filter)
        back_but = QtGui.QPushButton(QtGui.QIcon('resources/go-back.png'),\
            '', self)
        back_but.setGeometry(20,0,20,20)
        back_but.installEventFilter(sk_filter)
        reload_but = QtGui.QPushButton(QtGui.QIcon('resources/reload.png'),\
            '', self)
        reload_but.setGeometry(40,0,20,20)
        reload_but.installEventFilter(sk_filter)
        clear_but = QtGui.QPushButton(QtGui.QIcon('resources/clean-up.png'),\
            '', self)
        clear_but.setGeometry(60,0,20,20)
        clear_but.installEventFilter(sk_filter)
        # buttons callbacks
        self.connect(open_but, QtCore.SIGNAL('clicked()'), \
            self.open_but_callback)
        self.connect(back_but, QtCore.SIGNAL('clicked()'), \
            self.back_but_callback)
        self.connect(reload_but, QtCore.SIGNAL('clicked()'), \
            self.reload_but_callback)
        self.connect(clear_but, QtCore.SIGNAL('clicked()'), \
            self.clear_but_callback)
        # line edit  
        self.lineedit = line_edit(self)
        self.lineedit.setGeometry(80,0,200,20)
        self.connect(self.lineedit, QtCore.SIGNAL('textEdited(QString)'), \
            self.set_clipboard)
        self.connect(self.lineedit, \
                     QtCore.SIGNAL('focusInSignal(QString)'), \
                     self.set_clipboard)
        # File load dialog
        self.file_open_dlg = QtGui.QFileDialog()
        # Ctrl+z and Ctrl+y bypass
        shortcut = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Z'), self);
        self.connect(shortcut, QtCore.SIGNAL('activated()'), \
            self.ctrl_z_callback)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Y'), self);
        self.connect(shortcut, QtCore.SIGNAL('activated()'), \
            self.ctrl_y_callback)

    def setScene(self, scene):
        if self.oldScene != None:
             self.oldScene.unsetCallback()
        QtGui.QGraphicsView.setScene(self, scene)
        self.oldScene = scene
        scene.setCallback()

    def show_scene(self, file_name):
        print 'Request to open %s' % file_name
        file_name = self._show_scene(file_name)
        if file_name:
            self.scenes_history.append(file_name)

    def _show_scene(self, file_name):
        # canonize first
        file_name = os.path.abspath(file_name)
        try:
            # check if it should open from scratch
            if not(file_name in self.scenes.keys()):
                # create scene
                scene = svg_scene()
                # item
                item = svg_item(file_name)
                item.setPos(QtCore.QPointF(0,0))
                self.connect(item, QtCore.SIGNAL('rect_hit'), \
                    self.append_clipboard)
                self.connect(item, QtCore.SIGNAL('href_hit'), \
                    self.follow_link)
                scene.addItem(item)
                # cursor item
                scene.addCursor(item)
                # filter to intercept Tab
                tk_filter = tabkeyFilter(self)
                scene.installEventFilter(tk_filter)
                self.connect(tk_filter, QtCore.SIGNAL('tab_key_hit'), \
                    self.tabkey_hit_callback)
                # add to scenes array
                self.scenes[file_name] = scene
            # look up
            scene = self.scenes[file_name]
            # show
            self.setScene(scene)
        except(IOError):
            return None
        return file_name

    def open_but_callback(self):
        file_name = self.file_open_dlg.getOpenFileName(self,\
            'Open .svg file ...','','')
        file_name = str(file_name)
        self.show_scene(file_name)

    def back_but_callback(self):
        if len(self.scenes_history) > 1:
            self.scenes_history.pop(-1)
            self._show_scene(self.scenes_history[-1])

    def reload_but_callback(self):
        file_to_reload = self.scenes_history.pop(-1)
        # the only thing to left is to wipe out from scenes
        # before call to show again
        del self.scenes[file_to_reload]
        self.show_scene(file_to_reload)

    def follow_link(self, href):
        curr_path = (os.path.split(self.scenes_history[-1]))[0]
        self.show_scene(os.path.abspath(curr_path + '/' + href))

    def clear_but_callback(self):
        self.lineedit.setText('')
        self.set_clipboard('')

    def ctrl_z_callback(self):
        self.lineedit.undo()
    
    def ctrl_y_callback(self):
        self.lineedit.redo()

    def tabkey_hit_callback(self):
        self.lineedit.setFocus()

    # called by lineedit which is not updated in the case
    def set_clipboard(self, line2set):
        if os.name == 'nt':
            self.tk.clipboard_clear()
            self.tk.clipboard_append(line2set)
        elif os.name == 'posix':
            outf = os.popen('xsel -i', 'w')
            outf.write(line2set)
            outf.close()
        else:
            raise RuntimeError('Unsupported os.name: %s' % os.name)

    def append_clipboard(self, line2append):
        self.lineedit.insert(line2append)
        cur_pos = self.lineedit.cursorPosition()
        self.lineedit.home(False)
        self.lineedit.backspace()
        self.lineedit.setCursorPosition(cur_pos)
        ret_str = self.lineedit.displayText()
        self.set_clipboard(ret_str)
    
    def handleMessage(self, message):
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.showNormal()
        self.show()
    
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_S:
            self.back_but_callback()
        elif e.key() == QtCore.Qt.Key_D:
            self.reload_but_callback()
        elif e.key() == QtCore.Qt.Key_F:
            self.clear_but_callback()
        else:
            self.oldScene.keyCallback(e)

def main():
    key = 'vstype_unique_key'

    app = SingleEntity(sys.argv, key)
    if app.isRunning():
        sys.exit(1)

    # view/scene
    view = app_view()
    app.connect(app, QtCore.SIGNAL('messageAvailable'),
                view.handleMessage)
    view.setWindowIcon(QtGui.QIcon('resources/splash.png'))
    view.setWindowTitle( 'VSType <<version>>')
    view.show()
    # bye
    sys.exit(app.exec_())
    if os.name == 'nt':
        view.tk.destroy()
    elif os.name != 'posix':
        raise RuntimeError('Unsupported os.name: %s' % os.name)

if __name__ == '__main__':
    main()

