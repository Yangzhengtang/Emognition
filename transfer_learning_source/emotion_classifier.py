#To classify the facial expression based basic model
#Edited by Yin Guanghao
import numpy as np
import cv2
import sys
import json
import time
import os
from keras.models import model_from_json

#set the value of some parameters
root_path = './pic/' 
model_path = root_path + 'model/'  #path fo model
img_size = 48 #img size: 48*48
emotion_labels = ['angry', 'disgust:', 'fear', 'happy', 'sad', 'surprise', 'neutral'] #basic categories of facial expression
num_class = len(emotion_labels)

# load model structure and weight
json_file = open(model_path + 'model_json.json')# load model structure
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
model.load_weights(model_path + 'model_weight.h5') #load model weight

#classify facial expression
def predict_emotion(face_img):
    #some reshape work
    face_img = face_img * (1. / 255) #make it 255 time smaller
    resized_img = cv2.resize(face_img, (img_size, img_size))  #reshape into 48*48
    rsz_img = []
    rsh_img = []
    results = []
    rsz_img.append(resized_img[:, :])  # resized_img[1:46,1:46]
    rsz_img.append(resized_img[2:45, :])
    rsz_img.append(cv2.flip(rsz_img[0], 1))
    i = 0
    for rsz_image in rsz_img:
        rsz_img[i] = cv2.resize(rsz_image, (img_size, img_size))
        i += 1
    for rsz_image in rsz_img:
        rsh_img.append(rsz_image.reshape(1, img_size, img_size, 1))
    i = 0
 
    #classify facial expression
    for rsh_image in rsh_img:
        list_of_list = model.predict_proba(rsh_image, batch_size=32, verbose=1)  # classify facial expression
        result = [prob for lst in list_of_list for prob in lst]
        results.append(result)
    return results

#detect face
def face_detect(image_path):

    #some init work
    cascPath = './pic/haarcascade_frontalface_alt.xml'
    faceCasccade = cv2.CascadeClassifier(cascPath)    #load opencv face detect xml
    img = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # load the img and convert it to bgrgray

    # face detection
    faces = faceCasccade.detectMultiScale(
        img_gray,
        scaleFactor=1.1,
        minNeighbors=1,
        minSize=(30, 30),
    )
    return faces, img_gray, img


if __name__ == '__main__':
    #load all images in the directory
    images = []
    flag = 0
    if len(sys.argv) != 1:
        dir = root_path + sys.argv[1]
        if os.path.isdir(dir):
            files = os.listdir(dir)
            print(files)
            for file in files:
                if file.endswith('jpg') or file.endswith('png') or file.endswith('PNG') or file.endswith('JPG'): #find graph files
                    images.append(dir + '/' + file)
        else:
            images.append(dir)
    else:
        print('there should be a parameter after .py')
    if len(sys.argv) == 3:
        flag = 1

    #face detection and facial expression classifier
    for image in images:
        faces, img_gray, img = face_detect(image)
        spb = img.shape
        sp = img_gray.shape
        height = sp[0]
        width = sp[1]
        size = 600
        if flag == 0:
            emo = ""
            face_exists = 0
            for (x, y, w, h) in faces:
                face_exists = 1
                face_img_gray = img_gray[y:y + h, x:x + w]
                results = predict_emotion(face_img_gray)  # classify the facial expression
                result_sum = np.array([0]*num_class)
                for result in results:
                    result_sum = result_sum + np.array(result)
                    print(result)
                angry, disgust, fear, happy, sad, surprise, neutral = result_sum #print all possible categories
                print(result_sum) 
                print('angry:', angry, 'disgust:', disgust, ' fear:', fear, ' happy:', happy, ' sad:', sad,
                      ' surprise:', surprise, ' neutral:', neutral) #print all possible categories
                label = np.argmax(result_sum)
                emo = emotion_labels[label]
                print('Emotion : ', emo)
                
                #build a capture rectangle and write some text to show the result on the graph
                t_size = 2
                ww = int(spb[0] * t_size / 300)
                www = int((w + 10) * t_size / 100)
                www_s = int((w + 20) * t_size / 100) * 2 / 5
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), ww)
                cv2.putText(img, emo, (x + 2, y + h - 2), cv2.FONT_HERSHEY_SIMPLEX,
                            www_s, (255, 0, 255), thickness=www, lineType=1)

            #release all
            if face_exists:
                cv2.HoughLinesP
                cv2.namedWindow(emo, 0)
                cent = int((height * 1.0 / width) * size)
                cv2.resizeWindow(emo, (size, cent))
                cv2.imshow(emo, img)
                k = cv2.waitKey(0)
                cv2.destroyAllWindows()
                if k & 0xFF == ord('q'):
                    break

        elif flag == 1:
            img = cv2.imread(image)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            results = predict_emotion(img_gray)  # classify the facial expression
            result_sum = np.array([0]*num_class)
            for result in results:
                result_sum = result_sum + np.array(result)
                print(result)
            angry, disgust, fear, happy, sad, surprise, neutral = result_sum
            print(result_sum)
            print('angry:', angry, 'disgust:', disgust, ' fear:', fear, ' happy:', happy, ' sad:', sad,
                  ' surprise:', surprise, ' neutral:', neutral) #print all possible categories
            label = np.argmax(result_sum)
            emo = emotion_labels[label]
            print('Emotion : ', emo)

             #build a capture rectangle and write some text to show the result on the graph
            cv2.HoughLinesP
            cv2.namedWindow(emo, 0)
            size = 400
            cent = int((height * 1.0 / width) * size)
            cv2.resizeWindow(emo, (size, cent))

            cv2.imshow(emo, img)
            cv2.waitKey(0)

