
import numpy as np
import csv
import cv2
import Person
import time
import firebase_admin as fa
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('C:\\Users\\Kshitij Agrawal\\Desktop\\HackBattle\\fir-work-88327-firebase-adminsdk-0v04r-2364f31b59.json')
fa.initialize_app(cred)

db = firestore.client()


cnt_up   = 0
cnt_down = 0
st=0
f=0


cap = cv2.VideoCapture(0)


w = cap.get(3)
h = cap.get(4)
frameArea = h*w
areaTH = frameArea/100
print ('Area Threshold'), areaTH

line_up = int(2*(h/5))
line_down   = int(3*(h/5))

up_limit =   int(1*(h/5))
down_limit = int(4*(h/5))

print ("Red line y:"),str(line_down)
print ("Blue line y:"), str(line_up)
line_down_color = (255,0,0)
line_up_color = (0,0,255)
pt1 =  [0, line_down];
pt2 =  [w, line_down];
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_up];
pt4 =  [w, line_up];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))

pt5 =  [0, up_limit];
pt6 =  [w, up_limit];
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, down_limit];
pt8 =  [w, down_limit];
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))


fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = True)

kernelOp = np.ones((3,3),np.uint8)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

font = cv2.FONT_HERSHEY_SIMPLEX
persons = []
max_p_age = 5
pid = 1
fire_detected = False

while(cap.isOpened()):
    ret, frame = cap.read()

    for i in persons:
        i.age_one() 
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)


    try:
        ret,imBin= cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
        ret,imBin2 = cv2.threshold(fgmask2,200,255,cv2.THRESH_BINARY)
        
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kernelOp)
      
        mask =  cv2.morphologyEx(mask , cv2.MORPH_CLOSE, kernelCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernelCl)
    except:
        print('EOF')
        print ('UP:'),cnt_up
        print ('DOWN:'),cnt_down
        break
    _, contours0, hierarchy = cv2.findContours(mask2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        area = cv2.contourArea(cnt)
        if area > areaTH:
            
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv2.boundingRect(cnt)

            new = True
            if cy in range(up_limit,down_limit):
                for i in persons:
                    if abs(cx-i.getX()) <= w and abs(cy-i.getY()) <= h:
                        new = False
                        i.updateCoords(cx,cy)   
                        if i.going_UP(line_down,line_up) == True:
                            cnt_up += 1;
                            
                        elif i.going_DOWN(line_down,line_up) == True:
                            cnt_down += 1;
                            
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                        
                        index = persons.index(i)
                        persons.pop(index)
                        del i     
                if new == True:
                    p = Person.MyPerson(pid,cx,cy, max_p_age)
                    persons.append(p)
                    pid += 1     
        
            cv2.circle(frame,(cx,cy), 5, (0,0,255), -1)
            img = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            
            
            
   

    for i in persons:
        cv2.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv2.LINE_AA)
        
   
    str_up = 'UP: '+ str(cnt_up)
    str_down = 'DOWN: '+ str(cnt_down)
    st=int(str(cnt_up))-int(str(cnt_down))
    frame = cv2.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
    frame = cv2.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
    frame = cv2.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
    frame = cv2.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
    cv2.putText(frame, str_up ,(10,40),font,0.5,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame, str_up ,(10,40),font,0.5,(0,0,255),1,cv2.LINE_AA)
    cv2.putText(frame, str_down ,(10,90),font,0.5,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame, str_down ,(10,90),font,0.5,(255,0,0),1,cv2.LINE_AA)

    cv2.imshow('frame',frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Final count is",st)
        break
print("UP: ",str(cnt_up))
print("DOWN: ",str(cnt_down))
if (st<0):
    print ('The room is empty')
    st=0
cap= cv2.VideoCapture(0)
 
while True:
    (grabbed, frame) = cap.read()
    if not grabbed:
        break
 
    blur = cv2.GaussianBlur(frame, (21, 21), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
 
    lower = [18, 50, 50]
    upper = [35, 255, 255]
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")
    mask = cv2.inRange(hsv, lower, upper)
    
 
 
    output = cv2.bitwise_and(frame, hsv, mask=mask)
    no_red = cv2.countNonZero(mask)
    cv2.imshow("output", output)
    
    if int(no_red) > 5000:
        f=1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        if f==1:
            print("Fire Not detected.")
            fire_detected = False
        break    

    
cap.release()
cv2.destroyAllWindows()

Final_count={"R1":[st]}

doc_ref = db.collection(u'Safety First').document(u'Room 1')
doc_ref.set({"People inside Room 1":st, "Fire detected":fire_detected})
for row in zip(*([key] + (value) for key, value in sorted(Final_count.items()))):
    print(*row)

myData=[["Room1 count"],
        [st]]
myFile=open('Person_Count.csv','w')
with myFile:
    writer=csv.writer(myFile)
    writer.writerows(myData)
print("Writing to database complete.")
