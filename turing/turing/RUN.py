'''Copyright 2022 Пётр Сениченков
лицензия GNU GPLv3'''

'''
     Этот файл — часть Yet another Turing visualiser.

    Yet another Turing visualiser — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

    Yet another Turing visualiser распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

    Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>. 
'''

'''Это основной файл для запуска эмулятора.
Он проверяет, что все необходимые модули установлены, что используется Python версии 3.10 или выше и что все файлы эмулятора на месте'''


try:
    from sys import version, platform
    system = platform
    ver = (version.split('.')[0], version.split('.')[1])
except (ImportError, ModuleNotFoundError):
    print('''WARNING
Module sys not found.
Without it I can`t detect your operating system and Python version, so Emulator may not work.
You`d better install it with
    pip install sys

And if your Python version lower than 3.10, you MUST update Python to use Emulator.''')

if ver[0] != '3' or int(ver[1]) < 10:
    print('''ERROR
Python 3.10 or higher required.
Please, update Python.''')
    input()
    exit()

try:
    from tkinter import ttk
except (ImportError, ModuleNotFoundError):
    print('''ERROR
Tkinter не найден.
Скорее всего, у вас Linux.
Если это так, установите его с помощью
    sudo <your-package-manager> install python3xx-tk
или
	sudo <your-package-manager> install python3-tk,
в зависимости от вашего дистрибутива и используемых репозиториев.
	Например, sudo apt install python310-tk
	
Сейчас будет показано сообщение об ошибке. Там может быть больше информации о том, что вам нужно сделать\n\n\n''')
    from tkinter import ttk
    input()
    exit()

try:
    import os
except (ImportError, ModuleNotFoundError):
    print('''ERROR
Can`t find module os.
Install it with pip:
    pip install os''')
    input()
    exit()

def missing_module(name: str):
    print(f'''ERROR
Can`t find module {name}
Try to install it? (y/n)''')
    answer = input().lower()
    if answer == 'y':
        print(f'Trying to install {name}...')
        if system.startswith('win'):
            err_code = os.system(f'python pip install {name}')
            if err_code:
                print(f'''ERROR
Installation failed.
Maybe you don`t have python in PATH''')
                return False
            else:
                print(f'{name} installed successfully')
                return True
        elif system.startswith('linux'):
            err_code = os.system(f'pip install {name}')
            if err_code:
                print(f'''ERROR
Installation failed.
Maybe you don`t have pip installed.
Try to install it with
	sudo <your-package-manager> install python3xx-pip
or
	sudo <your-package-manager> install python3-pip,
depending on your distro and repositories.
	For example, sudo apt install python310-pip

Now you`ll see error message. There may be more information about what you should do\n\n\n''')
            else:
                print(f'{name} installed successfully')
                return True
        else:
            print(f'''I can`t detect your operating system, so I can`t install {name} for you.
Please do it yourself.''')
            return False
    elif answer == 'n':
        print(f'''You`ve decided me not to help you to install {name}.
You can do it manually later''')
        input()
        exit()
    else:
        print('Unexpected answer')
        input()
        exit()

try:
    import threading
except (ImportError, ModuleNotFoundError):
    missing_module('threading')

try:
    import time
except (ImportError, ModuleNotFoundError):
    missing_module('time')
    
try:
	import PIL
except (ImportError, ModuleNotFoundError):
	missing_module('Pillow')

try:
    from PIL import Image, ImageTk
except (ImportError, ModuleNotFoundError):
    print(f'''ERROR
Newer version of Pillow required.
Try to upgrade it? (y/n)''')
    answer = input().lower()
    if answer == 'y':
        print(f'Trying to upgrade Pillow...')
        if system.startswith('win'):
            err_code = os.system(f'python pip install --upgrade Pillow')
            if err_code:
                print(f'''ERROR
Installation failed.
Maybe you don`t have python in PATH''')
            else:
                print(f'Pillow upgraded successfully')
        elif system.startswith('linux'):
            err_code = os.system(f'pip install --upgrade Pillow')
            if err_code:
                print(f'''ERROR
Installation failed.
Maybe you don`t have pip installed.
Try to install it with
	sudo <your-package-manager> install python3xx-pip
or
	sudo <your-package-manager> install python3-pip,
depending on your distro and repositories.
	For example, sudo apt install python310-pip
	
Now you`ll see error message. There may be more information about what you should do\n\n\n''')
            else:
                print(f'Pillow upgraded successfully')
        else:
            print(f'''I can`t detect your operating system, so I can`t install {name} for you.
Please do it yourself.''')
    elif answer == 'n':
        print(f'''You`ve decided me not to help you to install {name}.
You can do it manually later''')
        input()
        exit()
    else:
        print('Unexpected answer')
        input()
        exit()

try:
    from xml.etree import ElementTree
except (ImportError, ModuleNotFoundError):
    missing_module('xml.etree')

try:
    import collections
except (ImportError, ModuleNotFoundError):
    missing_module('collections')

try:
    import webbrowser
except (ImportError, ModuleNotFoundError):
    if not missing_module('webbrowser'):
        print(''''\nYou can also install ttkthemes from sources.
You can find them in folder Dependencies''')

try:
    import ttkthemes
except (ImportError, ModuleNotFoundError):
    missing_module('ttkthemes')

try:
    from yet_another_turing_visualiser import main as vis_main
except (ImportError, ModuleNotFoundError):
    print('''ERROR
One of essential files (yet_another_turing_visualiser.py) not found.
Try reinstalling Emulator.''')
    input()
    exit()

try:
    from yet_another_turing import end as tur_end
except (ImportError, ModuleNotFoundError):
    print('''ERROR
One of essential files (yet_another_turing.py) not found.
Try reinstalling Emulator.''')
    input()
    exit()

try:
    from custom_help import About
except (ImportError, ModuleNotFoundError):
    print('''ERROR
One of essential files (custom_help.py) not found.
Try reinstalling Emulator.''')
    input()
    exit()

try:
    from custom_text import CustomText
except (ImportError, ModuleNotFoundError):
    print('''ERROR
One of essential files (custom_text.py) not found.
Try reinstalling Emulator.''')
    input()
    exit()


vis_main()
