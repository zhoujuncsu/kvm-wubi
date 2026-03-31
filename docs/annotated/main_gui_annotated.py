import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyautogui
import keyboard
import time
import threading

from translate import WubiTranslator, resource_path

"""
main_gui.py（注释版）

职责：
- 提供一个文本框 + 发送按钮的 GUI
- 支持全局热键 F9（开始输入）与 Esc（中止）
- 内部调用 WubiTranslator 把文本转换为 token，再逐 token 模拟键盘输入到目标窗口

关键约定：
- 目标主机五笔输入法：开启“单字模式”
- 中/英切换：默认用 Shift（如果目标主机不是 Shift 切换，需要改这里）
- wubi token 的提交：
  - code 末尾不是数字：输入 code 后按 Space 提交上屏
  - code 末尾是数字（例如 qqu2）：认为数字已完成候选选择，不再追加 Space，避免多余空格
"""

pyautogui.PAUSE = 0.05


class WubiKVMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wubi KVM Voice Input (0.1)")
        self.root.geometry("700x700")

        try:
            # 打包后 wubi.json 在 exe 内部，使用 resource_path 定位
            self.translator = WubiTranslator(resource_path("wubi.json"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dictionary: {e}")
            self.root.destroy()
            return

        self.is_typing = False
        self.abort_typing = False

        self._setup_ui()
        self._setup_hotkeys()

    def _setup_ui(self):
        tk.Label(self.root, text="请输入文字，然后将输入法切换到五笔输入法中文模式", font=("Arial", 10)).pack(pady=5)
        tk.Label(self.root, text="Version: 0.1", font=("Arial", 9, "italic"), fg="gray").pack()

        self.text_area = scrolledtext.ScrolledText(self.root, height=10, font=("Microsoft YaHei", 10))
        self.text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        settings_frame = tk.Frame(self.root)
        settings_frame.pack(pady=5)
        tk.Label(settings_frame, text="按键延迟 (毫秒):", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.delay_var = tk.StringVar(value="50")
        self.delay_entry = tk.Entry(settings_frame, textvariable=self.delay_var, width=8)
        self.delay_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(settings_frame, text="(建议 20 - 100)", font=("Arial", 8, "italic"), fg="gray").pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        self.send_btn = tk.Button(
            btn_frame, text="发送到窗口 (F9)", command=self.start_typing_thread, bg="#4CAF50", fg="white", width=20
        )
        self.send_btn.pack(side=tk.LEFT, padx=10)

        self.clear_btn = tk.Button(btn_frame, text="Clear Text", command=self.clear_text, width=10)
        self.clear_btn.pack(side=tk.LEFT, padx=10)

        self.status_var = tk.StringVar(value="Ready. (Ensure IME is in Chinese mode)")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        tip_label = tk.Label(
            self.root,
            text='提示：目标主机的五笔输入法请开启“单字模式”以确保输入准确',
            fg="#D32F2F",
            font=("Arial", 9, "bold"),
            pady=2,
        )
        tip_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_hotkeys(self):
        # 全局热键：在目标窗口聚焦时仍可触发
        keyboard.add_hotkey("f9", self.start_typing_thread)
        keyboard.add_hotkey("esc", self.request_abort)

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

    def request_abort(self):
        if self.is_typing:
            self.abort_typing = True
            self.status_var.set("Aborting...")

    def start_typing_thread(self):
        if self.is_typing:
            return

        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            self.status_var.set("No text to send.")
            return

        self.send_btn.config(state=tk.DISABLED)
        self.is_typing = True
        self.abort_typing = False

        # 输入过程放线程，避免 GUI 卡死
        threading.Thread(target=self.process_and_type, args=(text,), daemon=True).start()

    def process_and_type(self, text):
        try:
            # UI 里是“毫秒”，sleep 需要“秒”
            try:
                char_delay = float(self.delay_var.get()) / 1000.0
            except ValueError:
                char_delay = 0.05
                self.delay_var.set("50")

            self.status_var.set("Translating...")
            tokens = self.translator.text_to_codes(text)
            self.status_var.set("Typing... (Hold Esc to stop)")

            current_mode = "chinese"
            for token in tokens:
                if self.abort_typing:
                    break

                token_type = token.get("type")
                code = token.get("code") or ""
                raw_text = token.get("text") or ""

                # 关键：切换中/英状态
                if token_type in ["wubi", "chinese_punct", "chinese_punct_shift"] and current_mode != "chinese":
                    pyautogui.press("shift")
                    current_mode = "chinese"
                    time.sleep(0.1)
                elif token_type == "raw" and current_mode != "english":
                    if code.strip():
                        pyautogui.press("shift")
                        current_mode = "english"
                        time.sleep(0.1)

                # 关键：按 token 类型发送按键
                if token_type == "wubi":
                    pyautogui.write(code, interval=0.01)
                    # 如果末尾是数字（如 qqu2），数字本身用于选词，不再追加空格
                    if not (code and code[-1].isdigit()):
                        pyautogui.press("space")
                elif token_type in ["chinese_punct", "chinese_punct_shift"]:
                    pyautogui.write(code)
                elif token_type == "raw":
                    if raw_text == "\n":
                        pyautogui.press("enter")
                    else:
                        pyautogui.write(code)

                time.sleep(char_delay)

            self.status_var.set("Input aborted." if self.abort_typing else "Success! Input finished.")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
        finally:
            self.is_typing = False
            self.send_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = WubiKVMApp(root)
    root.mainloop()

