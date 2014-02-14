
# simple code by Krystian Samp - krychu (samp[dot]krystian[monkey]gmail.com), November 2006

import sys
from PyQt4 import QtGui, QtCore

class MyAnimation(QtGui.QGraphicsItemAnimation):
    def __init__(self):
        QtGui.QGraphicsItemAnimation.__init__(self)
        self.color = QtGui.QColor(0,0,255) # initial state
        self.pen = QtGui.QPen(self.color)
        self.pen.setWidth(3)
    
    def setItem(self, item_to_set):
        item_to_set.setPen(self.pen)
        QtGui.QGraphicsItemAnimation.setItem(self, item_to_set)

    def afterAnimationStep(self, step):
        self.color.setRgb(0,int(255*(0.5-abs(step-0.5))*2),int(255*abs(step-0.5)*2))
        self.pen.setColor(self.color)
        self.item().setPen(self.pen)

class spacekeyFilter(QtCore.QObject):
    def __init__(self, obj):
        QtCore.QObject.__init__(self, obj)
        self.bypass = obj

    def eventFilter(self,  obj,  event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Space:
                print 'space pressed'
                self.bypass.keyPressEvent(event)
                return True
        return False

class MyView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)

        open_but = QtGui.QPushButton('open', self)
        open_but.setGeometry(0,0,20,20)

        self.scene = QtGui.QGraphicsScene(self)
        self.item = QtGui.QGraphicsEllipseItem(-50, -30, 100, 60)
        self.scene.addItem(self.item)
        self.setScene(self.scene)

        sk_filter = spacekeyFilter(self)
        open_but.installEventFilter(sk_filter)

        # Remember to hold the references to QTimeLine and QGraphicsItemAnimation instances.
        # They are not kept anywhere, even if you invoke QTimeLine.start().
        self.tl = QtCore.QTimeLine(2000)
        self.tl.setFrameRange(0, 100)
        self.connect(self.tl, QtCore.SIGNAL('finished()'), \
            self.finished_callback)
        self.a = MyAnimation()
        self.a.setItem(self.item)
        self.a.setTimeLine(self.tl)
        self.tl.setLoopCount(2)

        # Each method determining an animation state (e.g. setPosAt, setRotationAt etc.)
        # takes as a first argument a step which is a value between 0 (the beginning of the
        # animation) and 1 (the end of the animation)
        #self.a.setPosAt(0, QtCore.QPointF(0, -10))
        self.a.setRotationAt(1, 360)

        self.tl.start()
    
    def finished_callback(self):
        #self.tl.start()
        self.a.color.setRgb(0,0,255,50)
        self.a.pen.setColor(self.a.color)
        self.item.setPen(self.a.pen)

    def keyPressEvent(self, e):
        print 'key pressed %d' % e.key()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = MyView()
    view.show()
    sys.exit(app.exec_())

