## 打包为 exe（Windows）

### 依赖

- Python（建议 3.10+）
- PyInstaller

安装：

```bash
pip install pyinstaller
```

### 打包命令

在项目根目录执行：

```bash
python -m PyInstaller --onefile --noconsole --add-data "wubi.json;." --name "WubiKVM_VoiceInput" main_gui.py
```

生成产物：

- dist/WubiKVM_VoiceInput.exe

### 外置 corrections.json

该项目约定 corrections.json 为外置文件，运行时从 exe 所在目录读取。发布时请把 corrections.json 和 exe 放在同一目录。

建议发布目录结构：

- WubiKVM_VoiceInput.exe
- corrections.json

### 常见打包问题

- WinError 5 / Permission denied
  - 说明：exe 可能正在运行或被杀软占用，导致覆盖失败
  - 处理：先关闭 exe，再重新打包；或删除 dist 下旧 exe 再打包

