# Yet another Turing Emulator

Yet another Turing visualiser -- это эмулятор машины Тьюринга, ориентированный на кастомизацию и кроссплатформенность.

В отличие от других учебных эмуляторов, вам не будет неприятно пользоваться программой с интерфейсом прямиком с Windows 95 -- вы сможете настроить внешний вид так, как вам нравится.

Также, вам не придётся искать компьютер с Windows 95 -- этот эмулятор работает на Python, так что вы сможете запустить его даже на электрическом чайнике, если на нём есть интерпретатор Python.

Эмулятор протестирован и отлично работает на Windows 10 и нескольких дистрибутивах GNU/Linux (в том числе Raspbian). Даже на Linux From Scratch! (Вам понадобится установить Tk, затем заново установить Python 3. Не так уж сложно, не правда ли?) 

Эмулятор полностью портативный и абсолютно не зависит от операционной системы.

## How to launch emulator?

#### Windows
  To launch emulator on Windows you should click on **Emulator_windows**
#### Linux
  To launch emulator on Linux you should click on **Emulator_linux** file or execute `./Emulator_linux`
  
Also, you can go into folder *turing* and run file **RUN.py** (execute `python RUN.py` on Windows or `python3 RUN.py` on Linux)

## Старые версии Python ($\leq$ 3.9)       (***FIXME: здесь пока нет тега old_python***) 
  Чтобы установить Yet another Turing Emulator на старой версии Python, вам нужно всего лишь переключиться на тег **old_python** (в верхнем левом углу этой страницы). 
  Не волнуйтесь, он практически не отличается от версии для нового Python. Просто все конструкции `match...case` заменены на `if...elif...else` и убрана проверка версии Python. 
