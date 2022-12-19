'''Copyright 2022 Пётр Сениченков
лицензия GNU GPLv3'''

'''
     Этот файл — часть Yet another Turing visualiser.

    Yet another Turing visualiser — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

    Yet another Turing visualiser распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

    Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>. 
'''


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from threading import Thread, Condition
from os import system
from time import sleep

try:
    from custom_help import About, Help
except (ModuleNotFoundError, ImportError):
    self.finish_func(err_code=6, missing_module='custom_help')

try:
    from custom_text import CustomText
except (ModuleNotFoundError, ImportError):
    self.finish_func(err_code=6, missing_module='custom_text')

try:
    import yet_another_turing as tur
except (ModuleNotFoundError, ImportError):
    self.finish_func(err_code=6, missing_module='yet_another_turing')

ttkthemes_imported = True

try:
    from ttkthemes import ThemedTk, THEMES
except (ModuleNotFoundError, ImportError):
    ttkthemes_imported = False
    

#               TODO
# всё обернуть в коды ошибок (особенно в yet_another_turing), заодно подумать о защите от дурака и от багов вообще везде
# ещё поиграть в тетрис и побаловаться с цветами
# ~ постараться сделать всё более менее в одном стиле (закруглённые углы)
# ~~ добавить парочку тем
# ~ ещё цвета (фон такой, фон сякой, кнопки, ещё что-нибудь)
# spell checking
# ~~~ в комментариях выделять символы из таблицы
# ~ кнопки типа kill (это труднее чем кажется, так что ~)
# = меню (по-максимуму туда напихать, почему-то всегда так деалют)
# желательно ВСЁ задокументировать


class Debugger():
    def __init__(self):
        '''На самом деле не Debugger, а Yet another Turing visualiser'''
        self.running = False
        self.wait_time = 0.3
        self.thread = None
        self.step_btn_clicked = False
        self.auto = True
        self.init_str = '111+11'
        self.start_i_for_start_string = 100
        self.add_alph = ''
        self.start_i = 110
        self.start_state = 'q0'
        self.ttktheme = 'ubuntu'
        self.colors = {'light_blue': '#3daee9',
                       'very_light_blue': '#93cee9',
                       'blue': '#3333CC',
                       'red': '#CC5511',
                       'yellow': '#FFFF00'}
        self.elem_colors = {'states_in_comments': 'light_blue',
                            'highlight_command': 'blue',
                            'headers_in_table': 'very_light_blue',
                            'start_state': 'light_blue',
                            'edited_cell': 'red',
                            'active_cell_on_tape': 'yellow'
            }
        self.comments = '''Вычисляет сумму двух чисел в унарной записи
Головка изначально находится правее обоих чисел
q0: двигает головку вправо, пока не встретит пустую ячейку
q1: сдвигает головку влево и переходит к q2
q2: записывает единицу слева от обоих чисел'''
        self.filename = ''
        self.file_saved = True

        if ttkthemes_imported:
            self.root = ThemedTk(theme=self.ttktheme)
        else:
            self.root = tk.Tk()
            self.finish_func(err_code=5)
        self.root.focus_force()
        self.root.title('Turing emulator')
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        
        self.tape_frame = ttk.Frame(self.root)
        self.tape_frame.grid(padx=5, pady=5, row=0, column=0)

        self.tape = [ttk.Label(self.tape_frame, text = '~', borderwidth=1, relief='sunken', width=2) for i in range(20)]
        for i in range(20):
            self.tape[i].grid(padx=5, pady=5, row=0, column=i)


        self.table_frame = ttk.Frame(self.root)
        self.table_frame.grid(padx=5, pady=5, row=1, column=0)

        self.d = {
            'q0': {' ': ' <q1', '1': '1>q0', '+': '+>q0'},
            'q1': {' ': ' <q0', '1': ' <q2', '+': ' !'},
            'q2': {' ': '1>q0', '1': '1<q2', '+': '+<q2'}
            }
        self.states = []
        self.symbols = []
        self.red = []

        
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.grid(padx=5, pady=5, row=2, column=0)
        self.buttons = []
        self.invert_state_buttons = []
        self.auto_buttons = []
        self.not_auto_buttons = []

        self.start_btn = ttk.Button(self.btn_frame, text='Старт', command=self.start)
        self.start_btn.grid(padx=5, pady=5, row=0, column=0)
        self.buttons.append(self.start_btn)

        self.add_state_btn = ttk.Button(self.btn_frame, text='Добавить состояние головки', command=self.add_state)
        self.add_state_btn.grid(padx=5, pady=5, row=0, column=1)
        self.buttons.append(self.add_state_btn)

        self.remove_state_btn = ttk.Button(self.btn_frame, text='Удалить состояние головки', command=self.del_state)
        self.remove_state_btn.grid(padx=5, pady=5, row=0, column=2)
        self.buttons.append(self.remove_state_btn)


        self.settings_frame = ttk.Frame(self.root)
        self.settings_frame.grid(padx=5, pady=5, row=3, column=0)

        self.wait_time_scale = ttk.Scale(self.settings_frame, orient='horizontal', from_=0.05, to=1.5, value=self.wait_time, command=self.change_wait_time,
                                         length=150)
        self.wait_time_scale.grid(padx=5, pady=5, row=1, column=2)
        self.buttons.append(self.wait_time_scale)
        self.auto_buttons.append(self.wait_time_scale)

        self.wait_time_label = ttk.Label(self.settings_frame, text=str.format('Пауза: {0}', self.wait_time), width=10)
        self.wait_time_label.grid(padx=5, pady=5, row=0, column=2)
        self.auto_buttons.append(self.wait_time_label)

        self.step_btn = ttk.Button(self.settings_frame, text='Шаг', command=self.step_btn_click, state='disabled')
        self.step_btn.grid(padx=5, pady=5, row=1, column=3)
        self.invert_state_buttons.append(self.step_btn)

        self.auto_intvar = tk.IntVar(value=1 if self.auto else 0)
        self.auto_checkbox = ttk.Checkbutton(self.settings_frame, command=self.auto_change, state='active' if self.auto else 'disabled', text='auto',
                                             variable=self.auto_intvar)
        self.auto_checkbox.grid(padx=5, pady=5, row=0, column=0)
        self.buttons.append(self.auto_checkbox)

        self.start_state_stringvar = tk.StringVar(self.root, value=self.start_state)
        self.start_state_stringvar.trace_add('write', self.edit_start_state)
        
        self.start_state_spinbox = ttk.Spinbox(self.settings_frame, wrap=True, values=self.states, textvariable=self.start_state_stringvar)
        self.start_state_spinbox.grid(padx=5, pady=5, row=2, column=2)
        self.buttons.append(self.start_state_spinbox)

        self.start_state_lbl = ttk.Label(self.settings_frame, text='Начальное состояние головки: ')
        self.start_state_lbl.grid(padx=5, pady=5, row=2, column=1)
        self.buttons.append(self.start_state_lbl)


        self.alph_frame = ttk.Frame(self.root)
        self.alph_frame.grid(padx=5, pady=5, row=4, column=0)

        self.init_str_stringvar = tk.StringVar(self.root, value=self.init_str)
        self.init_str_stringvar.trace_add('write', self.edit_init_str)

        self.init_str_entry = ttk.Entry(self.alph_frame, textvariable=self.init_str_stringvar)
        self.init_str_entry.grid(padx=5, pady=5, row=0, column=1)
        self.buttons.append(self.init_str_entry)

        self.init_str_lbl = ttk.Label(self.alph_frame, text='Начальная строка: ')
        self.init_str_lbl.grid(padx=5, pady=5, row=0, column=0)
        self.buttons.append(self.init_str_lbl)

        self.add_alph_stringvar = tk.StringVar(self.root, value=self.add_alph)
        self.add_alph_stringvar.trace_add('write', self.edit_add_alph)

        self.add_alph_entry = ttk.Entry(self.alph_frame, textvariable=self.add_alph_stringvar)
        self.add_alph_entry.grid(padx=5, pady=5, row=0, column=4)
        self.buttons.append(self.add_alph_entry)

        self.add_alph_lbl = ttk.Label(self.alph_frame, text='Дополнительный алфавит: ')
        self.add_alph_lbl.grid(padx=5, pady=5, row=0, column=3)
        self.buttons.append(self.add_alph_lbl)

        self.comments_frame = ttk.Frame(self.root)
        self.comments_frame.grid(padx=5, pady=5, row=0, column=1, rowspan=4)

        self.comments_text = CustomText(self.comments_frame, width=40, height=15, wrap='word')
        self.comments_text.grid(padx=5, pady=5, row=1, column=0)
        self.comments_text.bind('<KeyRelease>', self.edit_comments)
        self.comments_text.insert(0.0, self.comments)
        self.buttons.append(self.comments_text)

        self.comments_lbl = ttk.Label(self.comments_frame, text='Комментарии')
        self.comments_lbl.grid(padx=5, pady=5, row=0, column=0)


        # menus
        self.root.option_add("*tearOff", 'FALSE')      # отключает возможность отцепить меню в отдельное окно (для всех сразу и навсегда)
        
        self.file_menu = tk.Menu()
        self.file_menu.add_command(label='Сохранить', command=self.save_btn_clicked, state='normal' if self.filename else 'disabled')
        self.file_menu.add_command(label='Сохранить как...', command=self.save_as)
        self.file_menu.add_command(label='Загрузить', command=self.load_btn_clicked)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Выход', command=self.root.destroy)

        self.options_menu = tk.Menu()
        self.options_menu.add_command(label='Настройки цветов', command=self.color_settings)

        self.info_menu = tk.Menu()
        self.info_menu.add_command(label='Справка', command=self.help)
        self.info_menu.add_command(label='О программе', command=self.info)

        self.menu = tk.Menu()
        self.menu.add_cascade(label='Файл', menu=self.file_menu)
        self.menu.add_cascade(label='Параметры', menu=self.options_menu)
        self.menu.add_cascade(label='Справка', menu=self.info_menu)
        self.root['menu'] = self.menu


        self.actions_frame = ttk.Frame(self.root)
        self.actions_frame.grid(padx=5, pady=5, row=5, column=0)

        self.save_btn = ttk.Button(self.actions_frame, text='Сохранить', command=self.save_btn_clicked)
        self.save_btn.grid(padx=5, pady=5, row=0, column=0)
        self.buttons.append(self.save_btn)

        self.load_btn = ttk.Button(self.actions_frame, text='Загрузить', command=self.load_btn_clicked)
        self.load_btn.grid(padx=5, pady=5, row=0, column=3)
        self.buttons.append(self.load_btn)

        self.load_colors_from_file(silent=True)
        self.root['theme'] = self.ttktheme

        self.init_tape(self.init_str, self.start_i_for_start_string, self.start_i)
        self.vis_table(True)
        
        self.root.mainloop()

    def start(self):
        '''вызывается нажатием кнопки СТАРТ
запускает интерпретатор в отдельном потоке, отключает все entry в таблице, меняет загловок окна, отключает всё что в self.buttons'''
        if self.running:
            self.finish_func(err_code=7)
        for symbol in range(len(self.symbols)):
            for state in range(len(self.states)):
                self.table[symbol][state]['foreground'] = ''
                self.table[symbol][state]['state'] = 'disabled'
        self.root.title('[running] Turing visualiser')

        for btn in self.buttons:
            btn['state'] = 'disabled'
        for btn in self.invert_state_buttons:
            btn['state'] = 'normal'
        if self.auto:
            self.step_btn['state'] = 'disabled'

        self.thread = Thread(target=tur.run_vis, kwargs={'vis_func': self.vis_all,
                                                         'wait_func': self.wait_func if self.auto else self.wait_func_step_by_step,
                                                         'program': self.d, 'start_i_for_start_string': self.start_i_for_start_string,
                                                         'start_string': self.init_str, 'start_i': self.start_i, 'finish_func': self.finish_func,
                                                         'start_state': self.start_state})
        self.running = True
        self.thread.start()

    def reset(self):
        '''вызывается finish_func, когда нет ошибок
включает всё что в self.buttons, заново отображает ленту и таблицу с начальными значениями'''
        for btn in self.buttons:
            btn['state'] = 'normal'
        for btn in self.invert_state_buttons:
            btn['state'] = 'disabled'
            
        self.running = False
        self.init_tape(self.init_str, self.start_i_for_start_string, self.start_i)
        self.vis_table()

    def color_settings(self):
        '''вызывается нажатием НАСТРОЙКИ ЦВЕТОВ в меню
открывает окно с настройками цветов'''
        
        def colors_combobox_chosen(*args):
            '''вызывается при выборе значения на colors_combobox
просто меняет цвет образца'''
            sample['background']=self.colors[self.elem_colors[inverted_colors_dict[colors_stringvar.get()]]]

        def choose_color(*args):
            '''вызывается при нажатии кнопки ВЫБРАТЬ ЦВЕТ
создаёт диалог выбора цвета, вызывает colors_combobox_chosen чтобы поменять цвет образца'''
            chosen_color = colorchooser.askcolor(color=self.colors[self.elem_colors[inverted_colors_dict[colors_stringvar.get()]]], parent=new_root)
            if chosen_color == (None, None):
                return
            else:
                chosen_color = chosen_color[1]
            if chosen_color in self.colors.values():
                for key in self.colors:
                    if self.colors[key] == chosen_color:
                        color_name = key
                        break
            else:
                color_name = chosen_color
                self.colors.update({color_name: chosen_color})
            self.elem_colors[inverted_colors_dict[colors_stringvar.get()]] = color_name
            colors_combobox_chosen()

        def close(*args):
            '''вызывается при нажатии кнопки закрыть и TODO: крестика
закрывает меню, сохраняет цвета, перерисовывает таблицу (self.reset)'''
            new_root.destroy()
            self.write_colors_to_file()
            self.reset()
            
        def choose_file(*args):
            '''вызывается при нажатии кнопки ВЫБРАТЬ ФАЙЛ
открывает диалог выбора файла, загружает цвета'''
            filename = filedialog.askopenfile(parent=new_root, defaultextension='.yats', filetypes=[('Файл настроек', '.yats'), ('Все файлы', '.*')])
            if filename == None:
                return
            open_theme_btn['text'] = filename.name.split('/')[-1] if '/' in filename.name else filename.name
            self.load_colors_from_file(filename=filename.name, parent=new_root)
            colors_combobox_chosen()

        def ttktheme_combobox_chosen(*args):
            '''вызывается при выборе значения на ttktheme_combobox
TODO: меняет self.root['theme'], на всякий проверяет корректность темы'''
            self.ttktheme = ttktheme_stringvar.get()
            try:
                self.root['theme'] = self.ttktheme
                new_root['theme'] = self.ttktheme
            except:
                self.finish_func(err_code=13, parent=new_root, unavailible_theme=self.ttktheme)
        
        
        if ttkthemes_imported:
            new_root = ThemedTk(theme=self.ttktheme)
        else:
            new_root = tk.Tk()
            self.finish_func(err_code=5, parent=new_root)
        new_root.focus_force()
        new_root.attributes('-topmost', True)
        new_root.attributes('-alpha', 0.95)
        new_root.title('Настройки цветов')
        new_root.resizable(False, False)
        new_root.protocol("WM_DELETE_WINDOW", close)

        colors_dict = {'states_in_comments': 'Подсветка состояний в комментариях',
        'highlight_command': 'Подсветка текущей команды в таблице',
        'headers_in_table': 'Заголовки в таблице',
        'start_state': 'Начальное состояние',
        'edited_cell': 'Отредактированная ячейка таблицы',
        'active_cell_on_tape': 'Активная ячейка на ленте'
            }

        inverted_colors_dict = {'Подсветка состояний в комментариях': 'states_in_comments',
                                'Подсветка текущей команды в таблице': 'highlight_command',
                                'Заголовки в таблице': 'headers_in_table',
                                'Начальное состояние': 'start_state',
                                'Отредактированная ячейка таблицы': 'edited_cell',
                                'Активная ячейка на ленте': 'active_cell_on_tape'}

        colors_stringvar = tk.StringVar(new_root, value=colors_dict['states_in_comments'])
        colors_stringvar.trace_add('write', colors_combobox_chosen)
        
        colors_combobox = ttk.Combobox(new_root, textvariable=colors_stringvar, values=list(inverted_colors_dict),
                                       width=60, state='readonly')
        colors_combobox.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

        sample = ttk.Label(new_root, text='Образец цвета', background=self.colors[self.elem_colors[inverted_colors_dict[colors_stringvar.get()]]])
        sample.grid(row=1, column=0, padx=10, pady=10, columnspan=3)

        if ttkthemes_imported:
            ttktheme_stringvar = tk.StringVar(new_root, value=self.ttktheme)
            ttktheme_stringvar.trace_add('write', ttktheme_combobox_chosen)

            ttktheme_lbl = ttk.Label(new_root, text='Внешний вид элементов:')
            ttktheme_lbl.grid(row=2, column=0, padx=5, pady=10, columnspan=2)

            ttktheme_combobox = ttk.Combobox(new_root, textvariable=ttktheme_stringvar, values=list(THEMES), width=30, state='readonly')
            ttktheme_combobox.grid(row=2, column=2, padx=5, pady=10, columnspan=2)

        choose_color_btn = ttk.Button(new_root, text='Выбрать цвет', command=choose_color)
        choose_color_btn.grid(row=3, column=0, padx=5, pady=10)

        close_btn = ttk.Button(new_root, text='Закрыть', command=close)
        close_btn.grid(row=3, column=2, padx=5, pady=10)

        open_theme_btn = ttk.Button(new_root, text='Выбрать файл с темой', command=choose_file)
        open_theme_btn.grid(row=3, column=1, padx=5, pady=10)

    def highlight_states_in_comments(self):
        self.comments_text.tag_delete('syntax', 0.0, 'end')
        self.comments_text.tag_configure('syntax', foreground=self.colors[self.elem_colors['states_in_comments']])
        for word in self.states:
            self.comments_text.highlight_pattern(word, 'syntax')

    def auto_change(self):
        '''вызывается при нажатии на флажок AUTO
изменяет self.auto, отключает или включает всё что надо'''
        self.auto = self.auto_intvar.get() > 0
        if self.auto:
            for btn in self.auto_buttons:
                btn['state'] = 'normal'
            for btn in self.not_auto_buttons:
                btn['state'] = 'disabled'
        else:
            for btn in self.auto_buttons:
                btn['state'] = 'disabled'
            for btn in self.not_auto_buttons:
                btn['state'] = 'normal'

    def step_btn_click(self):
        '''вызывается нажатием кнопки ШАГ
ставит self.step_btn_clicked истинным'''
        self.step_btn_clicked = True

    def step_btn_check(self):
        '''вызывается self.wait_func
если self.step_btn_clicked, ставит его ложным и возвращает True'''
        if self.step_btn_clicked:
            self.step_btn_clicked = False
            return True
        return False

    def save_btn_clicked(self):
        '''вызывается нажатием SAVE (кнопки или через меню)
если до этого не вызывалось, открывает диалог для SAVE AS
вызывает write_to_file)'''
        if not self.filename:
            self.filename = filedialog.asksaveasfilename(defaultextension='.yat', filetypes=[('Файл yet another turing', '.yat'), ('Текстовый файл', '.txt')])
            if self.filename == None or self.filename == '':
                return
        self.write_to_file(self.filename)
        self.file_menu.entryconfigure(self.file_menu.index('Сохранить'), state=['normal'])
        self.file_saved_change()
        self.red.clear()

    def info(self):
        '''вызывается нажатием О ПРОГРАММЕ в меню
вызывает About.__init__ из custom_help.py'''
        ab = About(theme=self.ttktheme)

    def help(self):
        hlp = Help(theme=self.ttktheme)

    def file_saved_change(self, file_saved=True):
        if self.running:
            self.finish_func(err_code=7)
        self.file_saved = file_saved
        self.root.title('Turing visualiser' if self.file_saved else '*Turing visualiser*')

    def save_as(self):
        '''то же, что и save_btn_clicked, но без если'''
        self.filename = filedialog.asksaveasfilename(defaultextension='.yat', filetypes=[('Файл yet another turing', '.yat'), ('Текстовый файл', '.txt')])
        self.save_btn_clicked()

    def load_btn_clicked(self):
        '''вызывается нажатием ЗАГРУЗИТЬ (кнопки или через меню)
открывает диалог выбора файла и вызывает load_from_file'''
        if self.running:
            self.finish_func(err_code=7)
        self.filename = filedialog.askopenfilename(defaultextension='.yat',
                                                   filetypes=[('Файл yet another turing', '.yat'), ('Текстовый файл', '.txt.'), ('Все файлы', '.*')],
                                                   initialdir=r'..\Examples')
        if self.filename == None or self.filename == '':
            return
        self.load_from_file(self.filename)
        self.file_saved_change()
        
    def change_wait_time(self, new_val: str):
        '''вызывается при изменении занчения self.wait_time_scale
изменяет self.wait_time (округление до 2 знаков после запятой), обновляет self.wait_time_label'''
        self.wait_time = round(float(new_val), 2)
        self.wait_time_label['text'] = str.format('Пауза: {0}', self.wait_time)

    def edit_cell(self, new_text, *args):
        '''вызывается при редактировании команды в ячейке таблицы
обновляет self.d, подсвечивает изменённую ячейку (до вызова self.start), добавляет ячеку в self.red'''
        for symbol in range(len(self.symbols)):
            for state in range(len(self.states)):
                if self.table_stringvars[symbol][state].get() == self.d[self.states[state]][self.symbols[symbol]]:
                    continue
                self.table[symbol][state]['foreground'] = self.colors[self.elem_colors['edited_cell']]
                self.red.append((symbol, state))
                self.d[self.states[state]][self.symbols[symbol]] = self.table_stringvars[symbol][state].get()
        self.file_saved_change(False)

    def edit_comments(self, event):
        '''вызывается, когда пользователь отпускает кнопку с фокусом на поле комментариев
обновляет self.comments, не даёт написать в комментариях запрещённые символы'''
        if self.comments_text['state'] == 'disabled':
            return
        self.comments = self.comments_text.get('0.0', 'end')
        if '/*' in self.comments or '*/' in self.comments:
            self.finish_func(err_code=3)
        self.highlight_states_in_comments()
        self.file_saved_change(False)

    def change_comments(self, s: str):
        '''вызывается load_from_file
обновляет self.comments и зону для комментариев, не даёт написать в комментариях запрещённые символы'''
        self.comments = s
        if '/*' in self.comments or '*/' in self.comments:
            self.finish_func(err_code=3)
        self.comments_text.delete(0.0, 'end')
        self.comments_text.insert(0.0, s)

    def vis_tape(self, **kwargs):
        '''вызывается self.vis_all
отображает 20 ячеек вокруг текущей, подсвечивает текущую жёлтым'''
        i = kwargs['i']
        mem = kwargs['mem']
        if i < 20:
            start = 0
            end = 20
            i_highlight = i
        else:
            start = i - 20 // 2
            end = i + 20 // 2
            i_highlight = i - start
        
        for j in range(start, end):
            self.tape[j - start]['text'] = mem[j]
            if j == i:
                self.tape[j - start]['background'] = self.colors[self.elem_colors['active_cell_on_tape']]
            else:
                self.tape[j - start]['background'] = ''

    def vis_all(self, **kwargs):
        '''вызывается дочерним потоком после init и после каждого шага
вызывает self.vis_tape и self.vis_curr_command'''
        self.vis_tape(i=kwargs['i'], mem=kwargs['mem'])
        self.vis_curr_command(symbol=kwargs['symbol'], state=kwargs['state'])

    def add_state(self):
        '''добавляет новое сотояние головки в таблицу и вызывает self.vis_table'''
        name = 'q' + str(len(self.states))
        if self.running:
            self.finish_func(err_code=7)
        self.d.update({name: dict.fromkeys(self.symbols, ' ')})
        self.vis_table()
        self.file_saved_change(False)

    def add_symbol(self, ch: str):
        '''добавляет новый символ в таблицу и вызывает self.vis_table'''
        if len(ch) > 1:
            self.finish_func(err_code=1, several_symbols=ch)
        if ch == 'ÿ':
            self.finish_func(err_code=418)
        if self.running:
            self.finish_func(err_code=7)
        for state in self.d:
            self.d[state].update({ch: ' '})
        self.vis_table()
        self.file_saved_change(False)

    def del_symbol(self, ch: str):
        '''удаляет символ из таблицы и вызывает self.vis_table'''
        if len(ch) > 1:
            self.finish_func(err_code=1, several_symbols=ch)
        if self.running:
            self.finish_func(err_code=7)
        for state in self.d:
            self.d[state].pop(ch)
        self.vis_table()
        self.file_saved_change(False)

    def del_state(self):
        '''удаляет крайнее правое сотояние головки из таблицы и вызывает self.vis_table'''
        name = 'q' + str(len(self.states) - 1)
        if self.running:
            self.finish_func(err_code=7)
        self.d.pop(name)
        self.vis_table()
        self.file_saved_change(False)

    def vis_table(self, first=False):
        '''Обновляет все пременные, связанные с таблицей и отображает таблицу, использует self.red чтобы не обесцвечивать все ячейки
В self.table и self.table_stringvars:
    внешний -- symbol,     внутренний -- state
В self.d -- наоборот (этот метод не изменяет self.d)'''
        if not first:
            for state_lbl in self.table_states:
                state_lbl.destroy()
            for symbol_lbl in self.table_symbols:
                symbol_lbl.destroy()
            for symbol in range(len(self.symbols)):
                for state in range(len(self.states)):
                    self.table[symbol][state].destroy()
        
        self.states = tuple(self.d.keys())
        self.symbols = tuple(self.d[self.states[0]].keys())
        self.table = [[None for state in self.states] for symbol in self.symbols]   # внешний SYMBOL    внутренний STATE
        
        self.table_stringvars = [[tk.StringVar(value=self.d[state][symbol]) for state in self.states] for symbol in
                                 self.symbols]   # внешний SYMBOL    внутренний STATE
        for state in range(len(self.states)):
            for symbol in range(len(self.symbols)):
                self.table_stringvars[symbol][state].trace_add('write', self.edit_cell)

        self.table_states = [ttk.Label(self.table_frame, text=self.states[state], padding=5, borderwidth=1, relief='sunken', width=10,
                                       background=self.colors[self.elem_colors['headers_in_table']]) for state in range(len(self.states))]
        for state in range(len(self.states)):
            self.table_states[state].grid(padx=5, pady=5, row=0, column=state + 1)

        self.table_states[self.states.index(self.start_state)]['background'] = self.colors[self.elem_colors['start_state']]
        
        self.buttons.pop(self.buttons.index(self.add_state_btn))
        self.add_state_btn.destroy()
        self.add_state_btn = ttk.Button(self.table_frame, text='+', command=self.add_state, width=1)  # TODO: сделать красиво
        self.add_state_btn.grid(padx=5, pady=5, row=0, column=len(self.states) + 1)
        self.buttons.append(self.add_state_btn)

        self.remove_state_btn.destroy()
        if len(self.table_states) > 1:
            self.buttons.pop(self.buttons.index(self.remove_state_btn))
            self.remove_state_btn = ttk.Button(self.table_frame, width=1, text='x', padding=-5, command=self.del_state)
            self.remove_state_btn.grid(padx=5, pady=5, row=0, column=len(self.states) + 2, sticky='n')
            self.buttons.append(self.remove_state_btn)
        
        self.table_symbols = [ttk.Label(self.table_frame, text=self.symbols[symbol], padding=5, borderwidth=1, relief='sunken', width=10,
                                        background=self.colors[self.elem_colors['headers_in_table']]) for symbol in range(len(self.symbols))]
        for symbol in range(len(self.symbols)):
            self.table_symbols[symbol].grid(padx=5, pady=5, row=symbol + 1, column=0)

        for symbol in range(len(self.symbols)):
            for state in range(len(self.states)):
                entry = ttk.Entry(self.table_frame, textvariable=self.table_stringvars[symbol][state], width=10)
                if (symbol, state) in self.red:
                    entry['foreground'] = self.colors[self.elem_colors['edited_cell']]
                entry.grid(padx=5, pady=5, row=symbol + 1, column=state + 1)
                self.table[symbol][state] = entry
                
        self.start_state_spinbox.destroy()
        self.buttons.pop(self.buttons.index(self.start_state_spinbox))
        self.start_state_spinbox = ttk.Spinbox(self.settings_frame, wrap=True, values=self.states, textvariable=self.start_state_stringvar)
        self.start_state_spinbox.grid(padx=5, pady=5, row=2, column=2)
        self.buttons.append(self.start_state_spinbox)
        
        self.highlight_states_in_comments()

    def vis_curr_command(self, **kwargs):
        '''подсвечивает выполняемую команду в таблице'''
        for symbol in range(len(self.symbols)):
            for state in range(len(self.states)):
                self.table[symbol][state]['foreground'] = (self.colors[self.elem_colors['highlight_command']]
                                                           if (self.symbols[symbol] == kwargs['symbol'] and self.states[state] == kwargs['state']) else '')

    def wait_func(self):
        '''вызываетя дочерним потоком после каждого шага (если self.auto)
ждёт self.wait_time (в секундах)'''
        sleep(self.wait_time)

    def wait_func_step_by_step(self):
        '''вызываетя дочерним потоком после каждого шага (если не self.auto)
ждёт нажатия на кнопку ШАГ'''
        while not self.step_btn_check():
            sleep(0.05)

    def init_tape(self, s: str, start_idx=100, i=110):
        '''вызывается __init__ и reset
отображает строку на ленту'''
        self.init_str = s
        self.start_i_for_start_string = start_idx
        self.start_i = i
        temp_mem = []
        for i in range(start_idx):
            temp_mem.append(' ')
        for ch in s:
            temp_mem.append(ch)
        for i in range(50):
            temp_mem.append(' ')
        self.vis_tape(i=self.start_i, mem=temp_mem)

    def edit_init_str(self, *args):
        '''вызывается при редактировании self.init_str_stringvar (которая привязана к полю для начальной строки)
записывает что надо куда надо, вызывает update_symbols'''
        self.init_str = self.init_str_stringvar.get()
        self.update_symbols()
        self.init_tape(s=self.init_str_stringvar.get())

    def update_symbols(self):
        '''вызывается edit_init_str и edit_add_alph
обновляет символы в таблице, отлавливает запрещённые символы'''
        symbols = set(self.add_alph) | set(self.init_str) | set(' ')
        if '\a' in symbols:
            self.finish_func(err_code=2)
        if symbols - set(self.symbols):
            for ch in symbols - set(self.symbols):
                self.add_symbol(ch)
        if set(self.symbols) - symbols:
            for ch in set(self.symbols) - symbols:
                self.del_symbol(ch)
                
    def edit_add_alph(self, *args):
        '''вызывается при редактировании self.add_alph_stringvar (которая привязана к полю для дополнительного алфавита)
записывает что надо куда надо, вызывает update_symbols'''
        self.add_alph = self.add_alph_stringvar.get()
        self.update_symbols()

    def edit_start_state(self, *args):
        '''вызывается при изменении начального состояния
записывает что надо куда надо, вызывает vis_table'''
        self.start_state = self.start_state_stringvar.get()
        self.vis_table()
        self.file_saved_change(False)

    def finish_func(self, parent=None, **kwargs):
        '''вызывается yet_another_turing в конце работы + везде, где нужно сообщить пользователю об ошибке
обрабатывает ошибки
если их нет, вызывает reset'''
        parent = parent if parent else self.root
        err_code = kwargs['err_code'] if 'err_code' in kwargs else -1
        match err_code:
            # общие ошибки
            case 0:     # success
                messagebox.showinfo(title='Программа завершилась', message='Программа завершилась без ошибок', parent=parent)
                self.reset()
            case -1:    # default
                messagebox.showwarning(title='Программа завершилась', message='Программа завершилась, но не сообщила код ошибки (обратитесь в поддержку)',
                                       parent=parent)
            case 418:   # i`m teapot
                messagebox.showerror(title='Ошибка', message='Я не могу сварить кофе, потому что я чайник', parent=parent)

            # ошибки визуализатора
            case 1:     # два символа вместо одного
                if 'several_symbols' not in kwargs:
                    messagebox.showerror(title='Ошибка визуализатора', message='Нельзя внести в таблицу несколько символов вместо одного', parent=parent)
                messagebox.showerror(title='Ошибка визуализатора', message=str.format('Нельзя внести в таблицу несколько символов ({0}) вместо одного',
                                                                                      kwargs['several_symbols']), parent=parent)
            case 2:     # \a в таблице
                messagebox.showwarning(title='Предупреждение', message=r''''Пожалуйста, не используйте символ "beep" (\a).
Во-первых, в Python он не обрабатывается как "beep".
Во-вторых, он зарезервирован''', parent=parent)
            case 3:     # /* или */ в комментариях
                messagebox.showwarning(title='Предупреждение', message=r'''Пожалуйста, не используйте комбинации символов /* и */ в комментариях.
Они зарезервированы''', parent=parent)
            case 4:     # это не файл yet_another_turing
                messagebox.showerror(title='Невозможно открыть файл',
                                     message='''Файл, который вы пытаетесь открыть, не был сохранён в этой программе или повреждён.
К сожалению, вам придётся переписать его в таблицу вручную''', parent=parent)
            case 5:     # не установлен ttkthemes
                answer = messagebox.askokcancel(title='Не найден модуль', message='''Не установлен модуль ttkthemes.
Нажмите OK, чтобы установить.
Нажмите CANCEL, чтобы продолжить без него (работоспособность не гарантируется)''', parent=parent)
                if answer:
                    err_code_temp = system('pip install ttkthemes')
                    if err_code_temp:
                        messagebox.showerror(title='Ошибка', message='Не удалось установить модуль ttkthemes. Ничем не могу помочь', parent=parent)
                    else:
                        messagebox.showinfo(title='Модуль установлен',
                                            message='Модуль ttkthemes установлен. Перезапустите программу, чтобы применить изменения', parent=parent)
            case 6:     # нет файла yet_another_turing, custom_help или custom_text
                if 'missing_module' not in kwargs:
                    messagebox.showerror(title='Фатальная ошибка',
                                         message='''Не хватает какого-то файла, но мы не знаем какого. Обратитесь в поддержку.
Это фатальная ошибка, продолжать работу невозможно''', parent=parent)
                    exit()
                messagebox.showerror(title='Фатальная ошибка визуализатора',
                                     message='Не хватает файла ' + kwargs['missing_module'] + '''.py. Обратитесь в поддержку.
Это фатальная ошибка, продолжать работу невозможно''', parent=parent)
                exit()
            case 7:     # нажата кнопка из self.buttons, но self.running
                messagebox.showerror(title='Ошибка визуализатора', message='Молодец, смог нажать на неактивную кнопку. А о последствиях ты подумал?',
                                     parent=parent)
            case 8:     # нет файла color_settings.yats
                messagebox.showwarning(title='Предупреждение', message='''Не найден корректный файл с настройками цветов. Используются настройки по умолчанию.
Нажмите Параметры -> Настройки цветов -> Закрыть. Если ошибка не исчезнет, обратитесь в поддержку''', parent=parent)
            case 9:     # нажат крестик, но self.ruuning
                return messagebox.askyesno(title='Предупреждение', message='Программа всё ещё работает. Вы действительно хотите выйти?', parent=parent)
            case 10:    # yesno вернул не True False
                messagebox.showerror(title='Ошибка визуализатора', message='Тебя спросили да или нет, а ты нажал крестик...', parent=parent)
            case 11:    # нажат крестик, но файл не сохранён
                return messagebox.askyesnocancel(title='Сохранить?', message='Файл не сохранён. Сохранить?', parent=parent)
            case 12:    # файл настроек цветов успешно загружен
                messagebox.showinfo(title='Настройки загружены', message='Файл настроек цветов успешно загружен', parent=parent)
            case 13:    # выбранная тема не поддерживается
                if 'unavailible_theme' not in kwargs:
                    messagebox.showerror(title='Ошибка визуализатора', message='''Выбранная тема недоступна, а нам ещё и не сообщили какая именно.
У вас уже две причины обратиться в поддержку. Я буду очень благодарен, если вы это сделаете''')
                else:
                    messagebox.showerror(title='Ошибка визуализатора', message=str.format('''Тема {0} недоступна.
Пожалуйста, сообщите об этом в поддержку''', kwargs['unavailible_theme']))
                
            # ошибки тьюринга
            case 99:    # lorem ipsum
                messagebox.showerror(title='Ошибка интерпретатора', message='Это ошибка-заполнитель (типа lorem ipsum). Как ты вообще смог её получить?',
                                     parent=parent)
            case 100:   # переход к несуществующему состоянию
                if 'missing_state' not in kwargs:
                    messagebox.showerror(title='Ошибка интерпретатора', message='Переход к состоянию головки, которого нет в таблице', parent=parent)
                else:
                    messagebox.showerror(title='Ошибка интерпретатора', message=str.format('Переход к состоянию головки {0}, которого нет в таблице',
                                                                                           kwargs['missing_state']), parent=parent)
            case 101:   # край ленты
                if 'end' not in kwargs:
                    messagebox.showerror(title='Ошибка интерпретатора', message='Достигнут край ленты. Да, лента не бесконечная', parent=parent)
                else:
                    messagebox.showerror(title='Ошибка интерпретатора', message=str.format('Достигнут {0} край ленты. Да, лента не бесконечная',
                                                                                           kwargs['end']), parent=parent)
            case 102:   # неизвестный управляющий символ
                if 'unknown_symbol' not in kwargs:
                    messagebox.showerror(title='Ошибка интерпретатора', message='Неизвестный символ на второй позиции', parent=parent)
                else:
                    messagebox.showerror(title='Ошибка интерпретатора',
                                         message=str.format('На второй позиции должен стоять один из символов: < > !\nА не {0}', kwargs['unknown_symbol']),
                                         parent=parent)
            case 103:   # начальная строка не помещается на ленту
                messagebox.showerror(title='Ошибка интерпретатора',
                                     message='Начальная строка не помещается на ленту. Зачем тебе строка больше 1000 символов?', parent=parent)
                
            case _:     # other
                messagebox.showerror(title='Программа завершилась',
                                     message=str.format('Прогамма завершилась с кодом ошибки {0}. Мы не знаем, что это значит. Обратитесь в поддержку',
                                                        err_code), parent=parent)

    def write_to_file(self, filename: str):
        '''вызывается всеми, кто что-то сохраняет
записывает всё что надо в файл filename'''
        if filename.endswith('.yat'):
            file = open(filename, 'w')
        else:
            file = open(filename + '.yat', 'w')

        save_str = '\a\a'
        save_str += '\a'.join(self.symbols)
        save_str += '\a\a\n'
        for state in self.d:
            new_d = self.d[state]
            save_str += '\a'.join([new_d[symbol] for symbol in self.symbols])
            save_str += '\n'

        save_str += '/*'
        save_str += self.comments
        save_str += '*/' + '\n'

        save_str += 'start_str=' + str(self.init_str) + '\n'
        save_str += 'start_i_for_start_string=' + str(self.start_i_for_start_string) + '\n'
        save_str += 'start_i=' + str(self.start_i) + '\n'
        save_str += 'start_state=' + str(self.start_state) + '\n'
        save_str += 'add_alph=' + str(self.add_alph) + '\n'

        file.write(save_str)

        file.close()

    def load_from_file(self, filename: str):
        '''вызывается всеми, кто что-то загружает
загружает всё что надо из файла filename
выполняет базовые проверки, если что вызывает finish_func'''

        try:
            with open(filename, 'r') as file:
                try:
                    file_content = file.read()
                except (UnicodeDecodeError):
                    self.finish_func(err_code=4)
                    return
        except FileNotFoundError:
            self.finish_func()
            return

        if (not file_content.startswith('\a\a')) or (file_content.find('\a\a', 4) < 0) or (file_content.find('/*') < 0) or (file_content.find('*/') < 0):
            self.finish_func(err_code=4)
            return

            
        symbols = file_content[2:file_content.find('\a\a', 2):].split('\a')
        table_lines = file_content[file_content.find('\a\a', 4) + 3:file_content.find('/*'):].split('\n')
        for i in range(len(table_lines)):
            if not table_lines[i]:
                table_lines.pop(i)
        table = [line.split('\a') for line in table_lines]
        comments = file_content[file_content.find('/*') + 2:file_content.find('*/'):]
        states_count = len(table_lines)
        zone_after_comments = file_content[file_content.find('*/') + 3::].split('\n')
        zone_after_comments = list(filter(lambda x: len(x) > 0, zone_after_comments))

        d = {}
        for state_num in range(states_count):
            state_name = 'q' + str(state_num)
            d0 = {}
            for symbol_num in range(len(symbols)):
                symbol = symbols[symbol_num]
                try:
                    d0.update({symbol: table[state_num][symbol_num]})
                except (IndexError):
                    self.finish_func(err_code=4)
            d.update({state_name: d0})

        try:
            for elem in zone_after_comments:
                if elem.startswith('start_str='):
                    start_str = elem[10::]
                elif elem.startswith('start_i_for_start_string='):
                    start_i_for_start_string = int(elem[25::])
                elif elem.startswith('start_i='):
                    start_i = int(elem[8::])
                elif elem.startswith('start_state='):
                    start_state = elem[12::]
                elif elem.startswith('add_alph='):
                    add_alph = elem[9::] if len(elem) > 9 else ''
            #print(str.format('start_str: {0}\nstart_i_for_start_string: {1}\nstart_i: {2}\nstart_state: {3}\nadd_alph: {4}', start_str,
                             #start_i_for_start_string, start_i, start_state, add_alph))
        except:
            self.finish_func(err_code=4)
            return

        self.d = d

        self.init_str = start_str
        self.start_i_for_start_string = start_i_for_start_string
        self.start_i = start_i
        self.start_state = start_state
        self.add_alph = add_alph

        self.vis_table()
        self.change_comments(comments)

    def write_colors_to_file(self):
        file = open('color_settings.yats', 'w')

        file.write('\nCOLORS\n')

        write_str = '\n'.join(map(lambda x: str.format('{0}:{1}', x, self.colors[x]), self.colors.keys()))
        file.write(write_str)

        file.write('\nENDCOLORS\n')

        file.write('\nELEMS\n')

        write_str = '\n'.join(map(lambda x: str.format('{0}:{1}', x, self.elem_colors[x]), self.elem_colors.keys()))
        file.write(write_str)

        file.write('\nENDELEMS\n')

        file.write('\nTTKTHEME=' + self.ttktheme + '\n')

        file.close()

    def load_colors_from_file(self, filename='color_settings.yats', silent=False, parent=None):
        try:
            file = open(filename, 'r')
        except FileNotFoundError:
            self.finish_func(err_code=8, parent=parent)
            return

        file_content = file.readlines()
        file.close()

        reading = ''
        colors = {}
        elem_colors = {}
        ttktheme = ''
        for string in file_content:
            string = string.strip()
            if not len(string):
                continue
            if string == 'COLORS' and not reading:
                reading = 'COLORS'
                continue
            if string == 'ENDCOLORS' and reading == 'COLORS':
                reading = ''
                continue
            if string == 'ELEMS' and not reading:
                reading = 'ELEMS'
                continue
            if not reading and string.startswith('TTKTHEME='):
                ttktheme = string[9::].strip()
                break
            if string == 'ENDELEMS' and reading == 'ELEMS':
                reading = ''
                continue
            if reading == 'COLORS' and len(string):
                colors.update({string.split(':')[0]: string.split(':')[1]})
                continue
            if reading == 'ELEMS' and len(string):
                elem_colors.update({string.split(':')[0]: string.split(':')[1]})
                continue
            if not reading:
                continue
            self.finish_func(err_code=8, parent=parent)
            return

        if not colors or not elem_colors or not ttktheme:
            self.finish_func(err_code=8, parent=parent)
            return

        self.colors = colors
        self.elem_colors = elem_colors
        self.ttktheme = ttktheme
        if not silent:
            self.finish_func(err_code=12, parent=parent)

    def close(self):
        '''вызывается при закрытии основного окна (нажатием на крестик; alt + f4 сюда не отностится)
спрашивает если self.ruuning или не self.file_saved'''
        if self.running:
            answer = self.finish_func(err_code=9)
            match answer:
                case False:
                    return
                case True:
                    pass
                case _:
                    self.finish_func(err_code=10)
        if not self.file_saved:
            answer = self.finish_func(err_code=11)
            match answer:
                case False:
                    pass
                case True:
                    self.save_btn_clicked()
                case None:
                    return
                case _:
                    self.finish_func(err_code=10)

        self.root.destroy()
        
def main():
    dbgr = Debugger()

if __name__ == '__main__':
    main()


