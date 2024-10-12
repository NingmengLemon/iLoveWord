# iLoveWord

大概是一个我爱记单词自动答题脚本

最初写于2023年11月大概，是托大的，准备最近重写一下（如果有兴趣的话

> ↑ 如果上面那句话还没改的话说明还没重写呢（逃

## 大致原理

1. 通过adb抓取手机屏幕画面，用pillow裁剪出有效区域
2. PaddleOCR提取文本
3. 将英语单词内容交给词典，将返回的查询结果与中文内容作比较，选择相似度最高的选项
   > 如果题干是中文就查询每个选项，反之则查询题干。因为中文不方便查词典（）
4. 使用adb模拟点击此选项的屏幕位置
5. 等待我爱记单词自动跳到下一题
6. 回到步骤1，除非已循环100遍

> 因为通过adb操作设备所以仅支持安卓呢亲w
>
> 没有在Linux上测试过 ~~，我觉得是跑不通的~~

## 使用方法

### 配置

1. 从 [ECDICT](https://github.com/skywind3000/ECDICT) 仓库的 Release 中下载词典数据库，解压后放置于脚本根目录命名为 `stardict.db`
2. 打开手机或虚拟设备的USB调试，在电脑上安装 [platform-tools](https://developer.android.com/tools/releases/platform-tools?hl=zh-cn) 并添加到 PATH 环境变量，将安卓设备与电脑连接，在安卓设备上允许电脑对其进行调试
   > 对于部分厂商，需要进一步允许USB调试模拟点击（点名表扬小米）
3. 设置虚拟环境，安装 `requirements.txt` 中的第三方库
4. 根据屏幕尺寸调整 `main.py` 中的裁剪区域（`available_region` 变量的内容），确保只包含了题目内容
   > 裁剪后的图像应该像这样，除了题干与选项外不包含其他文本内容：
   >
   > ![After Cropping](images/sample_en2zh.png)

### 使用

1. 运行 `main.py`
2. 打开我爱记单词
   > 如果是首次运行，先点击自测，确保一切无误后再考试（首次运行时Paddle可能会下载一些必需内容）
3. 当程序提示 `Press ENTER to start` 时，进入答题页面，然后在终端中按下 Enter 键
4. 等待程序运行，如果运行结束后仍有未完成的题可以再次运行
   > 如果需要提前结束，按 `Ctrl+C` 终止程序即可
5. 作答完成，**手动提交**，超时未交会被判没分

## 注意事项

经测试 PaddleOCR 似乎无法在过高版本的 Python 中运行，程序在 3.10.* 中通过测试，推荐使用w

如果使用了一些难以辨认的字体，正确率可能大幅下降

## 效果

平均3分钟左右完成，80分以上

## 免责声明

此程序仅供学习、交流和研究使用。作者编写该脚本的目的是为了提供编程和自动化任务的学习示例，并不鼓励或支持在任何实际情况下使用该脚本来违反任何规定或规章制度。使用者应自行判断和承担使用本脚本的后果。

作者对此脚本的使用结果不承担任何责任。因使用本脚本而造成的任何直接或间接后果均由使用者自行承担。

## 杂项

TODO:

- 重构我写的这托史
- 换用效率更高的安卓自动化库（计划使用 uiautomator2）
- 使程序更加简单易用
