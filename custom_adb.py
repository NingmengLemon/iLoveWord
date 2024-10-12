import os
import subprocess
import psutil
import logging


def linux_escape(text):
    esmap = ["$", "#", "~", ".", "&", "!", "^", "(", ")", " ", ";", "'", '"']
    for es in esmap:
        text = text.replace(es, "\\" + es)
    return text


def check_process():
    for i in psutil.process_iter():
        if i.name() == "adb.exe":
            return True
    return False


class AdbException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def _popen(cmd):
    p = subprocess.Popen(
        cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    stdout, stderr = p.communicate()
    stdout = stdout.decode("utf-8")
    if stderr:
        print(stderr.decode("utf-8"))
    return stdout, stderr


def popen_readline(cmd):
    stdout, stderr = _popen(cmd)
    lines = stdout.split("\r\n")
    for line in lines:
        yield line


def popen_read(cmd):
    stdout, stderr = _popen(cmd)
    return stdout


def check_connected_devices():
    if not check_process():
        rv = os.system("adb devices")
        assert rv == 0, "Abnormal adb return value: %d" % rv
    p = popen_read("adb devices | findstr device")
    ls = p.strip().split("\r\n")
    ls.remove("List of devices attached")
    return [tuple(l.split("\t")) for l in ls]


def check_connect():
    with os.popen("adb devices") as pipe:
        rv = pipe.read()
    if "offline" in rv or rv == "List of devices attached\n\n":
        return False
    else:
        return True


def walk_adb(path):
    root = path
    pipe = popen_readline('adb shell ls -l "%s"' % linux_escape(path))
    head = next(pipe)
    folders = []
    files = []
    if head.startswith("adb.exe:"):
        raise AdbException(head)
    for line in pipe:
        if not line:
            continue
        info = line.split(maxsplit=7)
        # print(info)
        attr, node, user, ugroup, size, mdate, mtime, name = info
        type_ = attr[0]
        if type_ == "-":  # 普通文件
            files.append(name)
        elif type_ == "d":  # 目录
            folders.append(name)
    yield (path, folders, files)
    for folder in folders:
        for obj in walk_adb(os.path.join(path, folder).replace("\\", "/")):
            yield obj


def screencap(file="./screenshot.png"):
    assert os.system("adb exec-out screencap -p > " + file) == 0
    logging.info('Save screenshot as "%s"' % file)


def get_activity():
    with os.popen("adb shell dumpsys window | findstr mCurrentFocus") as pipe:
        rv = pipe.read()
    if "mCurrentFocus" in rv:
        act = rv.strip().split(" ")[-1][:-1]
        logging.info("Current activity is " + act)
        return act


def get_screensize():
    with os.popen("adb shell wm size") as pipe:
        rv = pipe.read()
    if rv.startswith("Physical size: "):
        size = tuple([int(i) for i in rv[15:-1].split("x")])
        logging.info(f"The screen size of the device is {size}")
        return size
    else:
        return None


def inputkey(keycode: str):  # KEYCODE_VOLUME_UP KEYCODE_VOLUME_DOWN
    assert os.system("adb shell input keyevent " + keycode) == 0
    logging.info("Sent key: " + keycode)


def inputstr(string):
    assert os.system("adb shell input text  " + string) == 0
    logging.info("Sent string: " + string)


def tap(x, y):
    assert os.system(f"adb shell input tap {x} {y}") == 0
    logging.info(f"Click ({x},{y})")
