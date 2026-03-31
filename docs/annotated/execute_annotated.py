import json
import pyautogui
import keyboard
import time
import os

"""
execute.py（注释版）

说明：
- 这是早期“文件驱动”版本：读取 output.json 并自动输入
- 当前推荐使用 main_gui.py（GUI 直接调用 translate.py，不需要 output.json）

保留这个文件的目的：
- 给读者一个最小可运行的执行层样例
- 展示 token.type 的执行策略（wubi/raw/中文标点等）
"""

pyautogui.PAUSE = 0.05


def load_output(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_input(data):
    current_mode = "chinese"
    for item in data:
        if keyboard.is_pressed("esc"):
            return

        text = item.get("text", "")
        code = item.get("code", "")
        token_type = item.get("type", "raw")

        if token_type in ["wubi", "chinese_punct", "chinese_punct_shift"] and current_mode != "chinese":
            pyautogui.press("shift")
            current_mode = "chinese"
            time.sleep(0.1)
        elif token_type == "raw" and current_mode != "english":
            if code.strip():
                pyautogui.press("shift")
                current_mode = "english"
                time.sleep(0.1)

        if token_type == "wubi":
            pyautogui.write(code, interval=0.01)
            if not (code and code[-1].isdigit()):
                pyautogui.press("space")
        elif token_type in ["chinese_punct", "chinese_punct_shift"]:
            pyautogui.write(code)
        else:
            if text == "\n":
                pyautogui.press("enter")
            elif text == "\r":
                pass
            else:
                pyautogui.write(code)

        time.sleep(0.02)


def main():
    output_path = "output.json"

    is_running = False

    def trigger():
        nonlocal is_running
        if is_running:
            return
        is_running = True
        try:
            data = load_output(output_path)
            run_input(data)
        finally:
            is_running = False

    keyboard.add_hotkey("f9", trigger)
    keyboard.wait("esc")


if __name__ == "__main__":
    main()

