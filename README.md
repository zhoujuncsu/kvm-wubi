# kvm-wubi
绕过远程环境剪贴板和文件传输限制，用中文五笔输入法自动输入汉字

将文本转换为五笔编码，并通过模拟键盘输入发送到 KVM/远程窗口的工具。

### 功能

- 单字模式五笔转换：中文按单字查表输出五笔编码
- 中文标点映射：在中文输入法状态下，通过对应物理按键输出全角标点
- 中英自动切换：遇到 ASCII 内容自动切到英文模式，中文/标点/五笔再切回中文模式
- 发送控制：GUI 按钮发送，同时支持全局热键 F9；Esc 中止
- 外置纠错表：通过 corrections.json 对个别重码字做“编码 + 候选序号”纠错（例如 qqu2）

### 快速开始（源码运行）

1. 安装依赖

```bash
pip install -r requirements.txt
```

1. 启动 GUI

```bash
python main_gui.py
```

1. 使用说明

- 目标主机输入法：切换到五笔并开启“单字模式”
- 在 GUI 文本框粘贴/输入内容
- 切到要输入的目标窗口（KVM 控制台、远程桌面窗口、记事本等）
- 按 F9 开始输入；Esc 中止
- “按键延迟（毫秒）”可按目标主机响应调整（例如 20\~100）

### 外置纠错表（corrections.json）

用于解决单字重码导致的候选顺序问题：

- 值可以是纯编码：例如 `"高": "ymkf"`
- 或编码 + 数字：例如 `"多": "qqu2"`（表示输入 qqu 后选第 2 个候选）

当编码以数字结尾时，GUI 会认为已经完成选词，不再额外发送空格，避免出现多余空格。

### 打包为 exe

参见 [docs/build-exe.md](file:///c:/Users/zhouj/Desktop/kvm-wubi/docs/build-exe.md)

### 文档

- 设计概览：[docs/overview.md](file:///c:/Users/zhouj/Desktop/kvm-wubi/docs/overview.md)
- 使用说明：[docs/usage.md](file:///c:/Users/zhouj/Desktop/kvm-wubi/docs/usage.md)
- 常见问题：[docs/troubleshooting.md](file:///c:/Users/zhouj/Desktop/kvm-wubi/docs/troubleshooting.md)
- 带注释源码：[docs/annotated/](file:///c:/Users/zhouj/Desktop/kvm-wubi/docs/annotated/)

