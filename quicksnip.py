#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 18:10:26 2012

@author: jsousa
"""
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import QX11Info,QClipboard
from PyQt4.QtCore import Qt

import sys,os

BASEDIR = '~/.quicksnip/'

def warning(par,s):
    QtGui.QMessageBox.warning(par,"Warning",s)

def popup(par,t,s,*args,**kwargs):
    return QtGui.QMessageBox.information(par,t,s,*args,**kwargs)
    
def exitApp(status=0):
    sys.exit(status)

class NoteTaker(QtGui.QWidget):

    def __init__(self,nw, *args):
        QtGui.QWidget.__init__(self,*args)

        self.state = 0
        
        #set window attributes
        #self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setWindowOpacity(0.0)
        
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        #maximize window
        screen = QtGui.QDesktopWidget().screenGeometry()        
        self.setGeometry(screen)


        #set cross cursor
        self.setCursor(Qt.CursorShape(Qt.CrossCursor))
        
        #display        
        self.show()

        #create rubberband
        self.rb = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle)

        #link to NoteWindow (which was already initialized and 
        #should be hidden)            
        self.notewin = nw
        
    def mousePressEvent(self,ev):
        if ev.button() != Qt.LeftButton:
            self.abort()
            
        if self.state == 0:        
            self.state = 1                        
            self.origin = ev.globalPos()
            #selection Area            
            self.rb.setGeometry(QtCore.QRect(self.origin,ev.globalPos()).normalized())
            self.rb.show()
    
    def mouseMoveEvent(self,ev):
        if self.state == 1:
            self.rb.setGeometry(QtCore.QRect(self.origin,ev.globalPos()).normalized())
    
    def mouseReleaseEvent(self,ev):
        if self.state == 1:
            self.state = 2
            self.end = ev.globalPos()        
            self.rb.hide()
            self.doSnip()
   
    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Escape: 
            self.abort()
    
    def doSnip(self):     

        #print self.origin
        #print self.end
        
        x = min(self.origin.x(),self.end.x())
        y = min(self.origin.y(),self.end.y())
        w = abs(self.origin.x() - self.end.x())
        h = abs(self.origin.y() - self.end.y())
        print x,y,w,h
        pm = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),x,y,w,h)
        #self.changeWindow(x,y,w,h,pm)
        self.notewin.applyImg(x,y,pm)
        self.close()
        #self.hide()
    
    def abort(self):
        """close both windows and exit program"""
        print "Aborting"
#        self.notewin.close()                
#        self.close()
        exitApp(-1)

#    def changeWindow(self,x,y,w,h,pixmap):
        #self.state = 2
        #self.lbl.setPixmap(pixmap)
        #self.lbl.show()
        #self.resize(pixmap.width(),pixmap.height())
        #self.setGeometry(x,y,w,h)
        #self.setCursor(Qt.CursorShape(Qt.ArrowCursor))

class NoteWindow(QtGui.QLabel):
    def __init__(self,*args):
        QtGui.QLabel.__init__(self,*args)
        self.setAlignment(Qt.AlignCenter)
        #     QtGui.QWidget.__init__(self,*args)
        #super(NoteWindow,self).__init__(self,*args)
        #self.lbl = QtGui.QLabel(self)
#        self.setCursor(Qt.CursorShape(Qt.ArrowCursor))

        self.menu = menu = QtGui.QMenu(self)
        self.saveAction = menu.addAction("Save")
        self.copyAction = menu.addAction("Copy to Clipboard")
        self.quitAction = menu.addAction("Quit")
        
        self.basedir = basedir = os.path.expanduser(BASEDIR)
        if not os.path.exists(basedir):
            os.mkdir(basedir)
        elif os.path.isfile(basedir):
            warning(self,"Can't create directory %s. Saving will not work" % basedir)        
        
        self.setWindowTitle("snip")

    def applyImg(self,x,y,pixmap):
        self.basePixmap = pixmap
        self.move(x,y)
        self.doResize(pixmap.size())        
#        self.setPixmap(pixmap)
#        self.setGeometry(x,y,pixmap.width(),pixmap.height())
         
        #set always on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.show()
    
    def doResize(self,size):
        self.resize(size)        
        pixmap = self.basePixmap.scaled(size,Qt.KeepAspectRatio)      
        self.setPixmap(pixmap)
        
        
    def saveImg(self):
        """Save image to drive"""
        
        ext = 'png'
        for i in range(99999):       
            p = os.path.join(self.basedir,'snip%05i' % i + '.' + ext)
            if not os.path.exists(p):
                if self.basePixmap.save(p,ext):
                    ans =  popup(self,"Saved","Saved image to " + p,'Open &Dir','&Ok')
                    if ans==0:
                        QtGui.QDesktopServices.openUrl( QtCore.QUrl.fromLocalFile(self.basedir))
                else:
                    warning(self,"Problem saving "+ p)
                return
                
        warning(self,"Error saving image. Is snips directory full?")
        
    def copyImg(self):
        """Copy image to clipboard"""
        clip = QtCore.QCoreApplication.instance().clipboard()
        clip.setPixmap(self.basePixmap,0)
        

    def resizeEvent(self,ev):
        self.doResize(ev.size())        
        #size = ev.size()
        #self.resize(size)
        #newpixmap = self.basePixmap.scaled(size,Qt.KeepAspectRatio)
        #self.setPixmap(newpixmap)
    
    def mousePressEvent(self,ev):
        if (ev.button() == Qt.MidButton): #reset size
            self.doResize(self.basePixmap.size())
        
        if (ev.button() == Qt.LeftButton): #drag start
            print "Drag start"
            #itemData = QtCore.QByteArray()
            #dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
            #dataStream << pixmap << QtCore.QPoint(event.pos() - child.pos())

            mimeData = QtCore.QMimeData()
            mimeData.setImageData(self.basePixmap)
            #mimeData.setData("application/x-dnditemdata", itemData)
            
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            
#           in principle we could use the following lines to make a pixmap
#           to display when dragging, but I can't get it to show transparency so nevermidn
            #dragpm.setMask(dragpm.createMaskFromColor(QtGui.QColor(0,0,0,0)))
#            dpm = self.basePixmap.scaledToWidth(64)
#            drag.setPixmap(dpm)
#            drag.setHotSpot(ev.pos())
            
            drag.start()
#           some reference said to use this instead of drag.start
#            if drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
#                self.close()

    def wheelEvent(self,ev):
        if ev.orientation()==Qt.Vertical:
            #print float(ev.delta())*0.01/8
            delta = ev.delta()
            newsize = self.size() + QtCore.QSize(delta,delta)
            self.doResize(newsize)
        else:
            ev.ignore()
            
    def contextMenuEvent(self, event):
        action = self.menu.exec_(self.mapToGlobal(event.pos()))
        if action == self.quitAction:
            print "Exiting"
            #QtCore.QCoreApplication.instance().quit()
            #QtGui.QApplication.quit()       
            #self.close() #qt quit() method doesn't seem to work all the time, just close
            exitApp()
            
        
        elif action == self.copyAction:
            self.copyImg()
            
        elif action == self.saveAction:
            self.saveImg()
        
        
if __name__ == '__main__':
    if QX11Info.isCompositingManagerRunning() == 'False':
        raise SystemError('This program requires Compositing to work')
        
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("quicksnip")
    note = NoteWindow()
    win = NoteTaker(nw=note)
#    app.quit()
    status = app.exec_()
    print "Exit Status: ", status
    sys.exit(status)


