import serial
#from threading import *
import threading as tr
import time
import math

two_inTwentyFour=16777216

class Telcontrol(tr.Thread):
#everythin in degrees
    def __init__(self,port="COM14", baudrate="9600", maxdx=0.2, maxdy=0.2,myElv=0, myAz=0):
        tr.Thread.__init__(self);
        self.ser = serial.Serial(port, baudrate)  # need to check the com
        # x = ser.is_open
        self.initProtocol()
        self.maxdx=maxdx
        self.maxdy=maxdy
        self.myElv=myElv
        self.myAz=myAz
        self.isReady=True
        self.whileLock = tr.Semaphore(value=0)
        self.readyLock = tr.Lock()
        #self.lock.acquire()
        self.diffaz = 0
        self.diffelv = 0
        self.start()

        self.resetAzmTelescope()
        self.resetAltTelescope()
        self.oldx=0
        self.oldy=0


    def angle_to_24bit(self,ang):
        num = int((ang / 360) * two_inTwentyFour)
        #print(num)
        high = int(num / 65536)
        res = num % 65536
       # print(res)
        medium = int(res / 256)
        res = res % 256
        low = res
        return [high, medium, low]

    def resetAltTelescope(self):
        to_send = chr(80) + chr(4) + chr(17) + chr(4) + chr(0) + chr(0) + chr(0) + chr(0)
        self.ser.write(to_send.encode())

    def resetAzmTelescope(self, resetang=[0, 0, 0]):
        to_send = chr(80) + chr(4) + chr(16) + chr(4) + chr(0) + chr(0) + chr(0) + chr(0)
        self.ser.write(to_send.encode())

    def setAzimut(self, ang):
        if(ang<0):
            ang=360+ang
        if (ang > 360):
            ang = ang-360
        angtosend = self.angle_to_24bit(ang)
        to_send = chr(80) + chr(4) + chr(16) + chr(23) + chr(angtosend[0]) + chr(angtosend[1]) + chr(angtosend[2]) + chr(0)
        self.ser.write(to_send.encode())

    def setAltitude(self,ang):
        if(ang<0):
            ang=0
        if(ang>180):
            ang=0
        angtosend = self.angle_to_24bit(ang)
        to_send = chr(80) + chr(4) + chr(17) + chr(23) + chr(angtosend[0]) + chr(angtosend[1]) + chr(angtosend[2]) + chr(0)
        self.ser.write(to_send.encode())


    def connect(self):
        if not self.ser.is_open:
            self.ser.open()

    def disconnect(self):
        if not self.ser.closed:
            self.ser.close()

    def initProtocol(self):
        self.midLeft = chr(80) + chr(2) + chr(16) + chr(36) + chr(6) + chr(142) + chr(56) + chr(0)  # go left slow speed
        self.midRight = chr(80) + chr(2) + chr(16) + chr(36) + chr(6) + chr(142) + chr(56) + chr(0)  # going right at speed of 4
        self.stop_rl = chr(80) + chr(2) + chr(16) + chr(36) + chr(0) + chr(0) + chr(0) + chr(0)  # Stop

        command3 = chr(80) + chr(2) + chr(16) + chr(37) + chr(7) + chr(142) + chr(56) + chr(0)  # left (reset)
        self.midUp = chr(80) + chr(2) + chr(17) + chr(36) + chr(6) + chr(142) + chr(56) + chr(0)  # up
        self.midDown = chr(80) + chr(2) + chr(17) + chr(37) + chr(6) + chr(142) + chr(56) + chr(0)  # down
        self.Stop_ud = chr(80) + chr(2) + chr(17) + chr(37) + chr(0) + chr(0) + chr(0) + chr(0)  # stop

        self.StopX = (b':K1\r=\r')
        self.StopY = (b':K2\r=\r')
        self.ImmidiateStop= (b'4c0a\r')

    def getIsReady(self):
        self.readyLock.acquire()
        ans = self.isReady
        self.readyLock.release()
        return ans

    def setReady(self ,isReady):
        self.readyLock.acquire()
        self.isReady=isReady
        self.readyLock.release()

    def setCorrection(self,az=0,elv=0):
        if self.getIsReady():
            self.oldx=self.myAz
            self.oldy = self.myElv
            self.diffelv=elv
            self.diffaz=az
            self.myAz=self.myAz+az
            if (self.myElv < 0):
                self.myElv=self.myElv+elv
            if (self.myAz<0):
                self.myAz=360-self.myAz
            if(self.myAz>360):
                self.myAz=self.myAz-360


            # self.myAz = self.myAz +0.1
            # self.myElv = self.myElv + 0.1
            self.setReady(False)
            self.whileLock.release()
        print("my elv",self.myElv ,"my az",  self.myAz)

    def correct(self, rl=0, ud=0):#  right + left - up+ down -
        print("correct")
        #print(math.fabs(self.diffaz), "fabs")
        if( rl>self.maxdx):

            self.ser.write(self.midRight.encode())
            #time.sleep(5)
            self.ser.write(self.stop_rl.encode())
            #self.ser.write(self.stop_rl.encode())
            print(" move right ", self.myAz)
        if (rl < -self.maxdx):s

            self.ser.write(self.midLeft.encode())
            #time.sleep(5)
            self.ser.write(self.stop_rl.encode())
            #self.ser.write(self.stop_rl.encode())
            print(" move left ",self.myAz)
        if (ud > self.maxdy):

            self.ser.write(self.midUp.encode())
            #time.sleep(5)
            #self.ser.write(self.Stop_ud.encode())
            print(" move up ", self.myAz)
        if (ud < -self.maxdy):

            self.ser.write(self.midDown.encode())
            #time.sleep(5)

            #self.ser.write(self.Stop_ud.encode())
            print(" move down  ", self.myAz)
        if(ud > -self.maxdy  or ud < self.maxdy ):
            self.ser.write(self.Stop_ud.encode())
        if (rl > -self.maxdx or rl< self.maxdx):
            self.ser.write(self.Stop_ud.encode())

            #time.sleep(0.1)
        #time.sleep(math.abs(self.dy / self.maxdy))
        #print("up down")


    # def correct(self):
    #     print("correct")
    #     print(math.fabs(self.diffaz), "fabs")
    #     if ( math.fabs(self.diffaz)> self.maxdx):
    #         self.setAzimut(self.myAz)
    #         self.diffaz=0
    #         print("myaz- move",self.myAz)
    #         #time.sleep(0.1)
    #     if (math.fabs(self.diffelv)> self.maxdy):
    #         self.setAltitude(self.myElv)
    #         self.diffelv=0
    #         print("myelv-move",self.myElv)
    #         #time.sleep(0.1)
    #     #time.sleep(math.abs(self.dy / self.maxdy))
    #     #print("up down")

    # move up
    def run(self):
        while True:
            self.whileLock.acquire()
            self.correct()
            self.setReady(True)

    def stopTelescope(self):
        self.ser.write(self.StopX)
        self.ser.write(self.StopY)
        self.disconnect()
        print("Telescope stopped")

    def manualRight(self):
        self.ser.write(self.goRight_9)
        time.sleep(0.2)
        self.ser.write(self.StopX)
    def manualLeft(self):
        self.ser.write(self.goLeft_9)
        time.sleep(0.2)
        self.ser.write(self.StopX)
    def manualUp(self):
        self.ser.write(self.goUp)
        time.sleep(0.2)
        self.ser.write(self.StopX)
    def manualDown(self):
        self.ser.write(self.goDown)
        time.sleep(0.2)
        self.ser.write(self.StopX)
    def imidiateStop(self):
        self.ser.write(chr(76).encode())