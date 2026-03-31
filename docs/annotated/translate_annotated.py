import json
import os
import sys

"""
translate.py（注释版）

目标：
- 在目标主机五笔输入法开启“单字模式”的前提下，把文本逐字转换为五笔编码 token
- 额外处理：
  - 中文标点：在中文输入法状态下，通过对应物理按键打出全角标点
  - ASCII：交给执行层切换到英文模式直输
  - 重码纠错：通过外置 corrections.json 覆盖单字编码，必要时附带候选序号（例如 qqu2）

输出 token 结构：
{
  "text": 原字符,
  "code": 需要发送的按键串（五笔码 / 标点按键 / ASCII 字符）,
  "type": "wubi" | "chinese_punct" | "chinese_punct_shift" | "raw"
}
"""


def resource_path(relative_path):
    """
    返回“内置资源”的绝对路径（用于 PyInstaller 打包资源）。

    - 源码运行：返回项目当前目录下的文件路径
    - exe 运行：PyInstaller 会把内置资源解压到临时目录 sys._MEIPASS
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def external_path(relative_path):
    """
    返回“外置资源”的绝对路径（用于 corrections.json 这种跟 exe 同目录的文件）。

    - 源码运行：使用当前项目目录
    - exe 运行：使用 sys.executable 所在目录
    """
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class WubiTranslator:
    def __init__(self, dict_path, corrections_path=None):
        """
        dict_path：
          - 源码运行：通常传入 'wubi.json'
          - exe 运行：通常传入 resource_path('wubi.json')

        corrections_path：
          - 默认从 external_path('corrections.json') 读取（外置，便于用户随时修改）
        """

        self.wubi_dict = self._load_single_char_dict(dict_path)

        if corrections_path is None:
            corrections_path = external_path("corrections.json")

        self.corrections = {}
        if os.path.exists(corrections_path):
            try:
                with open(corrections_path, "r", encoding="utf-8") as f:
                    self.corrections = json.load(f)
            except Exception:
                self.corrections = {}

        """
        all_mappings 的 key 必须是“单字”
        - wubi_dict：来自 wubi.json 的单字编码
        - corrections：用户强制覆盖的编码（可附带候选序号，如 qqu2）
        """
        self.all_mappings = {**self.wubi_dict, **self.corrections}

        """
        中文标点映射说明：
        - 这里的 code 表示“要按下的物理按键字符”，执行层在中文模式下输入后，
          输入法通常会输出对应的全角标点。
        - 具体映射可能因输入法不同而略有差异，如果目标主机表现不一致，
          建议在目标主机记事本里验证：在五笔中文模式按下这些按键会输出什么。
        """
        self.chinese_punct_to_key = {
            "，": ",",
            "。": ".",
            "、": "\\",
            "；": ";",
            "‘": "'",
            "’": "'",
            "【": "[",
            "】": "]",
            "《": "<",
            "》": ">",
            "（": "(",
            "）": ")",
        }

        self.chinese_shift_punct_to_key = {
            "！": "!",
            "？": "?",
            "：": ":",
            "“": '"',
            "”": '"',
            "—": "_",
            "·": "~",
            "￥": "$",
            "¥": "$",
        }

    def _load_single_char_dict(self, dict_path):
        """
        只加载单字条目：len(k) == 1
        这是为了配合目标主机五笔“单字模式”，避免词组重码导致候选不稳定。
        """
        if not os.path.exists(dict_path):
            raise FileNotFoundError(f"Dictionary file not found: {dict_path}")
        with open(dict_path, "r", encoding="utf-8") as f:
            full_dict = json.load(f)
        return {k: v for k, v in full_dict.items() if len(k) == 1}

    def text_to_codes(self, text):
        """
        单字模式：逐字符转换
        """
        result = []
        for char in text:
            if char in self.all_mappings:
                result.append({"text": char, "code": self.all_mappings[char], "type": "wubi"})
            elif char in self.chinese_punct_to_key:
                result.append({"text": char, "code": self.chinese_punct_to_key[char], "type": "chinese_punct"})
            elif char in self.chinese_shift_punct_to_key:
                result.append(
                    {"text": char, "code": self.chinese_shift_punct_to_key[char], "type": "chinese_punct_shift"}
                )
            elif ord(char) < 128:
                result.append({"text": char, "code": char, "type": "raw"})
            else:
                # 对不在字库的字符：这里选择跳过（也可以改成输出 raw，并让执行层粘贴或用其他方案处理）
                pass
        return result

