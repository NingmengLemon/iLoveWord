from ocr import cut_img, ocr_paddle
import custom_adb as adb

# import trans_baidu
from stardict import StarDict
from fuzzywuzzy import fuzz

import re
import random
import time

# Configuration
# trans_baidu.appid = ''
# trans_baidu.appkey = ''

target_activity = "com.alibaba.android.rimet/com.alibaba.lightapp.runtime.activity.CommonWebViewActivitySwipe"
available_region = (0, 455, 1080, 1380)  # 视情况调整

sdict = StarDict("./stardict.db")


def calc_click_point(pos1: list, pos2: list, pos3: list, pos4: list) -> tuple:
    return (
        int(pos1[0] + (pos2[0] - pos1[0]) * (0.2) + available_region[0]),
        int((pos1[1] + pos4[1]) / 2 + available_region[1]),
    )


def ocr(img: str = "./screenshot.png") -> list:
    """
    返回一个列表, 包含若干个元组
    第一个元素是应当点击的坐标(也是个元组)
    第二个元素是识别结果
    """
    res = []
    for i in ocr_paddle(img):
        text = i[1][0].strip()
        # filter conditions here
        if len(text) < 3 or text.isdigit():
            continue
        res.append((calc_click_point(*i[0][:4]), text))
        print("OCR Line:", text)
    return res


def purify_text(text: str) -> str:
    text = re.sub(r"^[A-D]\.", "", text)  # 截掉选项前的序号
    if is_chi(text):
        return " ".join(re.findall(r"([\u4e00-\u9fa5]+)", text, re.IGNORECASE))
    else:
        return "".join(re.findall(r"([a-z]+)", text, re.IGNORECASE))


def is_chi(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fa5]", text))


def match(data):
    """
    data: 来自 ocr 函数的返回值
    返回匹配项在data中的索引, 失败返回-1
    """
    # 如果不出意外的话, data的第一项应该是题干
    main = purify_text(data[0][1])
    options = data[1:]
    if is_chi(main):
        # 将英文选项转为中文, 然后匹配……
        # Baidu Translate
        # pre_trans = '\n'.join([purify_text(i[1]) for i in options])
        # trans_res = [i['dst'] for i in trans_baidu.translate(pre_trans, 'en', 'zh')["trans_result"] if i['dst']]
        # Local Dict
        pre_trans = [purify_text(i[1]) for i in options]
        try:
            trans_res = [i["translation"] for i in sdict.query_batch(pre_trans)]
        except:
            return None
        print(repr(pre_trans), "->", repr(trans_res))
        mreses = []
        for i in range(len(options)):
            mres = fuzz.partial_ratio(trans_res[i], main)
            print(repr(trans_res[i]), "=", mres)
            mreses += [mres]
            # if mres >= 80: # 相似度阈值
            #     return options[i]
        return options[mreses.index(max(mreses))]
        # return None
    else:
        # 将题干转换为中文
        # trans_main = trans_baidu.translate(main,'en','zh')["trans_result"][0]['dst']
        try:
            trans_main = sdict.query(main)["translation"]
        except:
            return None
        print(repr(main), "->", repr(trans_main))
        mreses = []
        for i in range(len(options)):
            mres = fuzz.partial_ratio(options[i][1], trans_main)
            print(repr(options[i][1]), "=", mres)
            mreses += [mres]
            # if mres >= 80: # 相似度阈值
            #     return options[i]
        return options[mreses.index(max(mreses))]
        # return None


def main():
    count = 0
    succ = 0
    fail = 0
    while count < 100:
        adb.screencap("./screenshot.png")
        cut_img("./screenshot.png", available_region)
        data = ocr("./screenshot.png")
        sel = match(data)
        if not sel:
            sel = random.choice(data[-4:])
            fail += 1
        else:
            succ += 1
        print(data[0][1], "==", sel[1])
        print("Will tap:", sel)
        adb.tap(*sel[0])
        time.sleep(1)
        count += 1
    print("Succ:", succ)
    print("Fail:", fail)


if __name__ == "__main__":
    adb.screencap("./screenshot.png")
    print()
    input("Press ENTER to start.")
    main()
