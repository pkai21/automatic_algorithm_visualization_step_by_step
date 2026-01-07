# NFA Minimization - Visualize NFA
# Ngôn ngữ lập trình: Python (3.13.9)
# Người thực hiện: Phan Văn Khải

# Tool : dist\NFA Mimimization.exe
## Cài đặt
```bash
pip install -r requirements.txt
python -m PyInstaller --onefile --noconsole --add-data "gui;gui" --add-data "core;core" --hidden-import=customtkinter --hidden-import=PIL --hidden-import=PIL._tkinter_finder --hidden-import=gui.app_gui --name="NFA Mimimization" main.py
