# NFA Minimization - Visualize NFA
# Programming Language: Python (3.13.9)
# Author: Phan Van Khai

# Tool: dist\NFA Mimimization.exe
## Workflow
![alt text](workflow.png)
## Installation
```bash
pip install -r requirements.txt
python -m PyInstaller --onefile --noconsole --add-data "gui;gui" --add-data "core;core" --hidden-import=customtkinter --hidden-import=PIL --hidden-import=PIL._tkinter_finder --hidden-import=gui.app_gui --name="NFA Mimimization" main.py
