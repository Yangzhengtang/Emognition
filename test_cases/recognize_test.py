import unittest
import sys
sys.path.append('../')
from Recognize.Recognize import Recognition	#	导入recognize模块

def recognize_func( model_json, model_h5, model_xml, labels, image):
    recog=Recognition( model_json, model_h5, model_xml, labels)
    target_image = 'marked' + image
    emo_list = recog.recognize(images, target_image)   # 保存识别结果
    return emo_list

class MyTest(unittest.TestCase):
    def test_recognize(self):
        self.assertEqual(
        	recognize_func(test.json, test.h5, test.xml, ['angry', 'disgust:', 'fear', 'happy', 'sad', 'surprise', 'neutral'], test1.png), 
        	['happy'])
        
if __name__=='__main__':
    unittest.main(verbosity=2)

