#   Edited by 胡煜宗
#   Recognition类对象，用于后端表情识别，供前端调用
import numpy as np
import cv2
import sys
import json
from keras.models import model_from_json
from keras.backend import clear_session

class Recognition():
    def __init__(self,jsonfile,h5model_file,xml_file,labels):
        clear_session()
        self.img_size = 48
        self.emotion_labels = labels
        self.num_class = len(self.emotion_labels)
        json_file = open(jsonfile)
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weight
        self.model.load_weights(h5model_file)
        self.xml_file=xml_file

    def __del__(self):
        clear_session()

    def predict_emotion(self,face_img):
        face_img = face_img * (1. / 255)
        resized_img = cv2.resize(face_img, (self.img_size, self.img_size))
        rsz_img = []
        rsh_img = []
        results = []
        rsz_img.append(resized_img[:, :])
        rsz_img.append(resized_img[2:45, :])
        rsz_img.append(cv2.flip(rsz_img[0], 1))
        i = 0
        for rsz_image in rsz_img:
            rsz_img[i] = cv2.resize(rsz_image, (self.img_size, self.img_size))
            i += 1
        for rsz_image in rsz_img:
            rsh_img.append(rsz_image.reshape(1, self.img_size, self.img_size, 1))
        i = 0
        for rsh_image in rsh_img:
            list_of_list = self.model.predict_proba(rsh_image, batch_size=32, verbose=1)  # predict
            result = [prob for lst in list_of_list for prob in lst]
            results.append(result)
        return results

    def face_detect(self,image_path):
        cascPath = self.xml_file
        faceCasccade = cv2.CascadeClassifier(cascPath)

        img = cv2.imread(image_path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # face detection
        faces = faceCasccade.detectMultiScale(
            img_gray,
            scaleFactor=1.1,
            minNeighbors=1,
            minSize=(30, 30),
        )
        # print('img_gray:', type(img_gray))
        return faces, img_gray, img

    def recognize(self,image,out_path):  # 参数为路径
        faces, img_gray, img = self.face_detect(image)
        spb = img.shape
        emo_list = []
        for (x, y, w, h) in faces:
            face_img_gray = img_gray[y:y + h, x:x + w]
            results = self.predict_emotion(face_img_gray)  # face_img_gray
            result_sum = np.array([0] * self.num_class)
            for result in results:
                result_sum = result_sum + np.array(result)
            label = np.argmax(result_sum)
            emo = self.emotion_labels[label]
            emo_list.append(emo)
            # print('Emotion : ', emo)
            # 输出最大概率的情绪
            t_size = 2
            ww = int(spb[0] * t_size / 300)
            www = int((w + 10) * t_size / 100)
            www_s = int((w + 20) * t_size / 100) * 2 / 5
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), ww)
            cv2.putText(img, emo, (x + 2, y + h - 2), cv2.FONT_HERSHEY_SIMPLEX,
                        www_s, (255, 0, 255), thickness=www, lineType=1)
            cv2.imwrite(out_path, img)
            cv2.waitKey(0)
        return emo_list

