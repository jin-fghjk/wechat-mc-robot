"""
图片文字识别工具
"""
import cv2
import pytesseract
from PIL import Image


class OCRProcessor:
    def __init__(self):
        pass

    def process_image(self, image_path: str) -> str:
        """处理图片并识别文字"""
        try:
            # 读取图片
            img = cv2.imread(image_path)

            # 图像预处理
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # 使用Tesseract进行OCR
            text = pytesseract.image_to_string(thresh, lang='chi_sim')

            return text
        except Exception as e:
            print(f"OCR处理失败: {e}")
            return ""