
from PyQt4 import QtGui, QtCore, QtNetwork

class SingleApplication(QtGui.QApplication):
    def __init__(self, argv, key):
        QtGui.QApplication.__init__(self, argv)
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(
                    self._memory.errorString().toLocal8Bit().data())

    def isRunning(self):
        return self._running

class SingleApplicationWithMessaging(SingleApplication):
    def __init__(self, argv, key):
        SingleApplication.__init__(self, argv, key)
        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.emit(QtCore.SIGNAL('messageAvailable'),
                      QtCore.QString.fromUtf8(socket.readAll().data()))
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString().toLatin1())

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                print(socket.errorString().toLocal8Bit().data())
                return False
            socket.write(unicode(message).encode('utf-8'))
            if not socket.waitForBytesWritten(self._timeout):
                print(socket.errorString().toLocal8Bit().data())
                return False
            socket.disconnectFromServer()
            return True
        return False

class Window(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.edit = QtGui.QLineEdit(self)
        self.edit.setMinimumWidth(300)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.edit)

    def handleMessage(self, message):
        self.edit.setText(message)
        flags = self.windowFlags()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.showNormal()
        self.show()
        self.setWindowFlags(flags)
        self.showNormal()
        self.show()

if __name__ == '__main__':

    import sys

    key = 'FOO_BAR'

    app = SingleApplicationWithMessaging(sys.argv, key)
    if app.isRunning():
        app.sendMessage('app is already running')
        sys.exit(1)

    window = Window()
    app.connect(app, QtCore.SIGNAL('messageAvailable'),
                window.handleMessage)
    window.show()

    sys.exit(app.exec_())

