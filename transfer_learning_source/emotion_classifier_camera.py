#To do the categorize of facial expression in a video
#Edited by Yin Guanghao
import cv2
import sys
import gc
import json
import numpy as np
from keras.models import Sequential
from keras.models import model_from_json

root_path='./pic/'
model_path=root_path+'/model/'
img_size=48

#init
emo_labels = ['angry', 'disgust:', 'fear', 'happy', 'sad', 'surprise', 'neutral'] #the basic category of facial expression
num_class = len(emo_labels)
json_file=open(model_path+'model_json.json')
loaded_model_json = json_file.read() #load model structure
json_file.close() 
model = model_from_json(loaded_model_json)
model.load_weights(model_path+'model_weight.h5') #load weight

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage:%s camera_id\r\n" % (sys.argv[0]))
        sys.exit(0)
              
    #init     
    color = (0, 0, 2555) #color of capture rectangle 
    cap = cv2.VideoCapture(0) #video flow
    
    #face detection
    cascade_path = root_path+"haarcascade_frontalface_alt.xml" #open opencv face detection xml   
    while True:
        _, frame = cap.read()   #read one frame of video
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #conver the frame into gray graph
        cascade = cv2.CascadeClassifier(cascade_path)  #load face detect model              
        faceRects = cascade.detectMultiScale(frame_gray, scaleFactor = 1.1, #detect face
                                    minNeighbors = 1, minSize = (120, 120)) 
        #facial expression categorization        
        if len(faceRects) > 0:                 
            for faceRect in faceRects: 
                x, y, w, h = faceRect
                images=[]
                rs_sum=np.array([0.0]*num_class) #reshape into array
                image = frame_gray[y: y + h, x: x + w ]
                image=cv2.resize(image,(img_size,img_size)) #resize
                image=image*(1./255) #make it 255 time smaller
                images.append(image)
                images.append(cv2.flip(image,1))
                images.append(cv2.resize(image[2:45,:],(img_size,img_size)))
                for img in images:
                    image=img.reshape(1,img_size,img_size,1)
                    list_of_list = model.predict_proba(image,batch_size=32,verbose=1)#use the model to categorize facial expressions
                    result = [prob for lst in list_of_list for prob in lst]
                    rs_sum+=np.array(result)
                print(rs_sum)
                label=np.argmax(rs_sum) #get the label
                emo = emo_labels[label]
                print ('Emotion : ',emo)
                cv2.rectangle(frame, (x - 10, y - 10), (x + w + 10, y + h + 10), color, thickness = 2) #build the capture rectangle
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame,'%s' % emo,(x + 30, y + 30), font, 1, (255,0,255),4) #write the label of facial expression
        
        #wait for key interrupt
        k = cv2.waitKey(30)
        #wait for a q tu quit
        if k & 0xFF == ord('q'):
            break

    #release everything
    cap.release()
    cv2.destroyAllWindows()
