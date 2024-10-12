# import pytesseract
from paddleocr import PaddleOCR
from PIL import Image
import logging

pocr = PaddleOCR(
    use_angle_cls=True, lang="ch"
)  # need to run only once to download and load model into memory


def cut_img(file: str, coor: tuple):  # coor=(left, upper, right, lower)
    with Image.open(file) as img:
        cut = img.crop(coor)
        cut.save(file)
        logging.info('Cut file "{}", {}->{}'.format(file, img.size, coor))


# def ocr_pyt(imgfile:str,langs:str='chi_sim',config:str='') -> str:
#     img = Image.open(imgfile)
#     text = pytesseract.image_to_string(img,lang=langs,config=config)
#     logging.info(f'OCR "{imgfile}", lang={langs}')
#     return text


def ocr_paddle(img_path: str = "./screenshot.png") -> list:
    """
    result 是一个 list, 包含了每个识别结果的列表

    list中的每个项的内容

    0 识别框box的四个顶点的坐标list的list, 从左上角点开始顺时针

    1 识别内容tuple, 0是文本内容, 1是置信度
    """
    result = pocr.ocr(img_path, cls=True)
    return result[0]


print()
