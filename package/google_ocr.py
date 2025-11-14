from google.cloud import vision
from package.config_loader import get_config
import os
import cv2
from PIL import Image

class OCRClient:
        
    def __init__(self):
        self.CONFIG = get_config()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.CONFIG['google_vision_client']['credentials']
        self.client = vision.ImageAnnotatorClient()
    
    def get_annotations(self, image):
        _, encoded_image = cv2.imencode('.jpg', image)
        content = encoded_image.tobytes()

        # Send to Google Vision
        response = self.client.text_detection(image=vision.Image(content=content))
        return response.text_annotations


if __name__ == '__main__':
    ocr_client = OCRClient()
    image = cv2.imread('testing images/images/mahindra/DJI_0861.JPG')
    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    annotations = ocr_client.get_annotations(image)
    for annotation in annotations:
        print(annotation.description)
