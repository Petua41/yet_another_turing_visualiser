'''Copyright 2022 Пётр Сениченков
лицензия GNU GPLv3'''

'''
     Этот файл — часть Yet another Turing visualiser.

    Yet another Turing visualiser — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

    Yet another Turing visualiser распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

    Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>. 
'''


import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from xml.etree import ElementTree as ET
from collections import deque
from webbrowser import open_new
from sys import platform

if platform.startswith('win'):
    from os import startfile
    
try:
    from ttkthemes import ThemedTk
except (ModuleNotFoundError, ImportError):
    messagebox.showerror(title='Ошибка', message='Для отображения справки и информации о программе НЕОБХОДИМ модуль ttkthemes')
    exit()

class About():
    def __init__(self, theme='breeze'):
        self.root = ThemedTk(theme=theme)
        self.root.focus_force()
        self.root.title('О программе')
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        self.root.resizable(False, False)

        if platform.startswith('win'):
            self.platform = 'win'
        elif platform.startswith('linux'):
            self.platform = 'linux'
        else:
            self.platform = 'other'

        self.program_name = ttk.Label(self.root, text='Yet another Turing visualiser')
        self.program_name.grid(row=0, column=0, pady=15, padx=10)
        
        self.author = ttk.Label(self.root, text='© Сениченков Пётр, 11 А')
        self.author.grid(row=1, column=0, pady=15, padx=10)

        self.year = ttk.Label(self.root, text='2022')
        self.year.grid(row=2, column=0, pady=15, padx=10)

        self.help_frm = ttk.Frame(self.root)
        self.help_frm.grid(row=3, column=0, columnspan=2, pady=15, padx=10)
    
        self.help_lbl = ttk.Label(self.help_frm, text='Автор:')
        self.help_lbl.grid(row=0, column=0)

        self.help_ref = ttk.Label(self.help_frm, text='https://t.me/petua41', foreground='#3daee9', cursor='hand2')
        self.help_ref.grid(row=0, column=1)
        self.help_ref.bind('<Button-1>', self.open_tg)

        self.license_frm = ttk.Frame(self.root)
        self.license_frm.grid(row=4, column=0, columnspan=2, pady=15)

        self.license_lbl = ttk.Label(self.license_frm, text='Лицензия:')
        self.license_lbl.grid(row=0, column=0)

        self.license_ref = ttk.Label(self.license_frm, text='GNU GPLv3', foreground='#3daee9', cursor='hand2')
        self.license_ref.grid(row=0, column=1)
        self.license_ref.bind('<Button-1>', self.open_license)
        
        self.exit_btn = ttk.Button(self.root, text='Закрыть', command=self.root.destroy)
        self.exit_btn.grid(row=5, column=0, pady=15)

    def open_img(self, filename):
        img = Image.open(filename)
        img = ImageTk.PhotoImage(img, master=self.root)
        return img

    def open_tg(self, *args):
        open_new('https://t.me/petua41')

    def open_license(self, *args):
        if self.platform == 'win':
            startfile(r'COPYING.htm')
        else:
            open_new('https://www.gnu.org/licenses/gpl-3.0.html')

class Help():
    def __init__(self, theme='breeze'):
        self.root = ThemedTk(theme=theme)
        self.root.focus_force()
        self.root.title('Справка')
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        #self.root.resizable(False, False)
        self.root.geometry('800x350')

        if platform.startswith('win'):
            self.platform = 'win'
        elif platform.startswith('linux'):
            self.platform = 'linux'
        else:
            self.platform = 'other'

        self.dict_ids_to_texts = {}

        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(expand=True, fill='both', side='left')

        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(expand=True, fill='both', side='right')

        self.topics = ttk.Treeview(self.left_frame, show='tree', selectmode='browse')
        self.topics.pack(expand=True, fill='both')
        self.topics.bind('<<TreeviewSelect>>', self.topics_selected)

        self.help_text = tk.Text(self.right_frame, state='disabled', wrap='word')
        self.help_text.pack(expand=True, fill='both')

        self.parse_tree(self.topics)
    
    def parse_tree(self, treeview: ttk.Treeview, filename='help.xml'):
        '''вызывается при открытии окна
парсит xml файлик и разделяет его на словари по категориям'''
        tree = ET.parse(filename)
        lst_tree = self.turn_tree_into_list(tree)
        self.dict_ids_to_texts = self.insert_list_into_treeview(lst_tree, treeview)
        self.img_dict = self.extract_images_from_tree(tree)
        self.hlinks_descs_dict = self.extract_hlinks_descs_from_tree(tree)
        self.links_dict = self.extract_links_from_tree(tree)


    def turn_tree_into_list(self, tree):
        lst = []
        for elem in tree.iter('topic'):
            dc = {'id': elem.attrib['id'], 'name': elem.attrib['name'], 'text': elem.text, 'parent': ''}
            if dc['id'].count('.') > 0:
                   dc['parent'] = dc['id'][:dc['id'].rfind('.'):]
            lst.append(dc)
        return sorted(lst, key=lambda x: len(x['id'].split('.')))

    def insert_list_into_treeview(self, lst: list, treeview: ttk.Treeview):
        texts_dict = {}
        for dc in lst:
            _id = treeview.insert(dc['parent'], 'end', iid=dc['id'], text=dc['name'])
            texts_dict.update({_id: dc['text']})
        return texts_dict

    def topics_selected(self, *args):
        '''вызывается при выборе заголовка справа
меняет текст слева и вставляет в него всё что нужно из словарей'''
        _id = self.topics.selection()[0]
        try:
            txt = self.dict_ids_to_texts[_id]
            self.help_text['state'] = 'normal'
            self.help_text.delete(0.0, 'end')
            self.help_text.insert(0.0, txt)
            self.help_text['state'] = 'disabled'
        except KeyError:
            messagebox.showerror(title='Ошибка', message='Не удалось найти текст для выбранной темы')

        self.insert_images(_id, self.img_dict)
        self.insert_hlinks_from_descs(_id, self.hlinks_descs_dict)
        self.insert_links(_id, self.links_dict)

    def insert_image_into_text(self, symbol, image):
        self.help_text['state'] = 'normal'
        self.help_text.image_create(symbol, image=image)
        self.help_text['state'] = 'disabled'

    def extract_images_from_tree(self, tree):
        img_dict = {}
        for elem in tree.iter('image'):
            img_path = elem.text
            if self.platform == 'linux':
                img_path = img_path.replace('\\', '/')
            img = Image.open(img_path)
            if 'sizex' in elem.attrib and 'sizey' in elem.attrib:
                img = img.resize((int(elem.attrib['sizex']), int(elem.attrib['sizey'])), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img, master=self.root)
            
            if elem.attrib['id'] in img_dict:
                img_dict[elem.attrib['id']].append((elem.attrib['symbol'], img))
            else:
                img_dict.update({elem.attrib['id']: [(elem.attrib['symbol'], img)]})
        return img_dict

    def insert_images(self, _id, img_dict):
        if _id in img_dict:
            for tp in img_dict[_id]:
                self.insert_image_into_text(tp[0], tp[1])

    def insert_hlink_from_desc(self, addr, text, fg, cursor, symbol):
        hlink = ttk.Label(self.help_text, text=text, foreground=fg, cursor=cursor)
        hlink.bind('<Button-1>', lambda e: self.open_hlink(e, addr))

        self.help_text['state'] = 'normal'
        self.help_text.window_create(symbol, window=hlink)
        self.help_text['state'] = 'disabled'

    def insert_hlinks_from_descs(self, _id, hlinks_descs_dict):
        if _id in hlinks_descs_dict:
            for dic in hlinks_descs_dict[_id]:
                self.insert_hlink_from_desc(**dic)

    def extract_hlinks_descs_from_tree(self, tree):
        hlinks_descs_dict = {}
        for elem in tree.iter('hlink'):
            _addr = elem.text
            if 'name' in elem.attrib:
                _text = elem.attrib['name']
            else:
                raise Exception('in help.xml there is hlink without text')
            _foreground=elem.attrib['foreground'] if 'foreground' in elem.attrib else '#3daee9'
            _cursor = elem.attrib['cursor'] if 'cursor' in elem.attrib else 'hand2'
            if 'id' in elem.attrib:
                _id = elem.attrib['id']
            else:
                raise Exception('in help.xml there is hlink without id')
            if 'symbol' in elem.attrib:
                _symbol = elem.attrib['symbol']
            else:
                raise Exception('in help.xml there is hlink without symbol')

            if _id in hlinks_descs_dict:
                hlinks_descs_dict[_id].append({'addr': _addr, 'text': _text, 'fg': _foreground, 'cursor': _cursor, 'symbol': _symbol})
            else:
                hlinks_descs_dict.update({_id: [{'addr': _addr, 'text': _text, 'fg': _foreground, 'cursor': _cursor, 'symbol': _symbol}]})

        return hlinks_descs_dict

    def open_hlink(self, event, addr='https://www.google.com/404'):
        open_new(addr)

    def open_link(self, event, new_id):
        '''now_selected = self.topics.curselection[0]
        self.topics.select_clear(now_selected)
        self.topics.select_set(_id)'''

        self.topics.selection_set(new_id)

    def insert_link(self, new_id, text, fg, cursor, symbol):
        link = ttk.Label(self.help_text, text=text, foreground=fg, cursor=cursor)
        link.bind('<Button-1>', lambda e: self.open_link(e, new_id))

        self.help_text['state'] = 'normal'
        self.help_text.window_create(symbol, window=link)
        self.help_text['state'] = 'disabled'

    def insert_links(self, _id, links_dict):
        if _id in links_dict:
            for dic in links_dict[_id]:
                self.insert_link(**dic)

    def extract_links_from_tree(self, tree):
        links_dict = {}
        for elem in tree.iter('link'):
            _new_id = elem.text
            if 'name' in elem.attrib:
                _text = elem.attrib['name']
            else:
                raise Exception('in help.xml there is link without text')
            _foreground=elem.attrib['foreground'] if 'foreground' in elem.attrib else '#3daee9'
            _cursor = elem.attrib['cursor'] if 'cursor' in elem.attrib else 'hand2'
            if 'id' in elem.attrib:
                _id = elem.attrib['id']
            else:
                raise Exception('in help.xml there is link without id')
            if 'symbol' in elem.attrib:
                _symbol = elem.attrib['symbol']
            else:
                raise Exception('in help.xml there is link without symbol')

            if _id in links_dict:
                links_dict[_id].append({'new_id': _new_id, 'text': _text, 'fg': _foreground, 'cursor': _cursor, 'symbol': _symbol})
            else:
                links_dict.update({_id: [{'new_id': _new_id, 'text': _text, 'fg': _foreground, 'cursor': _cursor, 'symbol': _symbol}]})

        return links_dict
        
if __name__ == '__main__':
    about = About()
    hlp = Help()
