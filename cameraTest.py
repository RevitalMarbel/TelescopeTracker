import Telcontrol
import sys
#telescope=Telcontrol.Telcontrol()
import cv2
cap = cv2.VideoCapture(0)
#cap2 = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'DIVX')

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
out = cv2.VideoWriter('outputy9.avi', fourcc, 10, (w, h))

while(1):
    ret, frame = cap.read()
#    ret2, frame2 = cap2.read()
    out.write(frame )
    cv2.imshow('frame', frame)
#    cv2.imshow('frame2', frame2)
    #cv2.imshow('img',img)
    k = cv2.waitKey(1)
    if k==27:    # Esc key to stop
        print('esc')
        break
out.release()
cap.release()
#cap2.release()
cv2.destroyAllWindows()