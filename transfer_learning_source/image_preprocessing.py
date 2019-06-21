#Edited by Shi Wei
#To preprocess the image data
import numpy as np
import cv2
import sys
import json
import time
import os

root_path = './pic/'
model_path = root_path + 'model/'  # '/model_0.7/'
img_size = 48
emotion_labels = ['angry', 'disgust:', 'fear', 'happy', 'sad', 'surprise', 'neutral']
num_class = len(emotion_labels)

#Utilize opencv to detect the face
def face_detect(image_path):
    #open xml file
    cascPath = './pic/haarcascade_frontalface_alt.xml'
    faceCasccade = cv2.CascadeClassifier(cascPath)

    # load img and convert it to bgrgray
    img = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # face detection
    faces = faceCasccade.detectMultiScale(
        img_gray,
        scaleFactor=1.1,
        minNeighbors=1,
        minSize=(30, 30),
    )
    return faces, img_gray, img

#reshape the img
def compress(face_img):
    face_img = face_img * (1. / 255) #make it 255 times smaller
    resized_img = cv2.resize(face_img, (img_size, img_size))  #conver it into img_size*img_size
    rsz_img = []
    rsh_img = []
    results = []
    rsz_img.append(resized_img[:, :])  # resized_img[1:46,1:46]
    rsz_img.append(resized_img[2:45, :])
    rsz_img.append(cv2.flip(rsz_img[0], 1))
    i = 0

    #reshape part
    for rsz_image in rsz_img:
        rsz_img[i] = cv2.resize(rsz_image, (img_size, img_size))
        i += 1
    for rsz_image in rsz_img:
        rsh_img.append(rsz_image.reshape(1, img_size, img_size, 1))
    i = 0
    for rsh_image in rsh_img:
        list_of_list = model.predict_proba(rsh_image, batch_size=32, verbose=1)  
        result = [prob for lst in list_of_list for prob in lst]
        results.append(result)
    return results

#main function
if __name__ == '__main__':
    #open the directory
    images = []
    flag = 0
    if len(sys.argv) != 1:
        dir = './'+sys.argv[1]
        if os.path.isdir(dir):
            files = os.listdir(dir)
            print(files)
            for file in files:
                if file.endswith('jpg') or file.endswith('png') or file.endswith('PNG') or file.endswith('JPG'): #find graph file
                    images.append(dir + '/' + file)
        else:
            images.append(dir)
    else:
        print('there should be a parameter after .py')
    if len(sys.argv) == 3:
        flag = 1

   #do the reshaped work
    for image in images:
        print (image)
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
                resized_img = cv2.resize(face_img_gray, (img_size, img_size))
                print(image)
                print('save')
                cv2.imwrite(image,resized_img)
