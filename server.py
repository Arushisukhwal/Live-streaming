import socket
import numpy
import cv2 
import threading
sk = socket.socket()
sk.bind(("", 1234))
sk.listen()
session, address = sk.accept() #accepting request from any server
print(session.recv(2046)) 
cameraIndex = 'http://192.168.0.101:8080/video' # using camera from IPWebcam App
camera = cv2.VideoCapture(cameraIndex)

def sender():
    while True:
        status, photo = camera.read()
        photo = cv2.resize(photo, (640, 480))
        print(photo.shape)
        if status:
            session.send(numpy.ndarray.tobytes(photo))
        else: print("Could not get frame")

def receiver():
    framesLost = 0
    print("Entered")
    while True:
        framesLost += 1
        data = session.recv(100000000)
        if(data == b'finished'):
            print("Finished")
            camera.release()
            session.close()
        else:
            photo =  numpy.frombuffer(data, dtype=numpy.uint8)
            if len(photo) == 640*480*3:
                cv2.imshow('From Client', photo.reshape(480, 640, 3))
                if cv2.waitKey(1) == 13:
                    session.send(b'finished')
                    camera.release()
                    cv2.destroyAllWindows()
                    break
            else:
                print("Lost {} frames".format(framesLost) )
                
threading.Thread(target=sender).start()
threading.Thread(target=receiver).start()
