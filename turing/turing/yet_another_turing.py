'''Copyright 2022 Пётр Сениченков
лицензия GNU GPLv3'''

'''
     Этот файл — часть Yet another Turing visualiser.

    Yet another Turing visualiser — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

    Yet another Turing visualiser распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

    Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>. 
'''


from collections import deque



def end():
    global running
    
    running = False

def finish_func(err_code=-1, parent=None, **kwargs):
    print(str.format('ERROR {0}: {1}', err_code, kwargs))

def run():
    while running:
        step()

def stage1(s: str):
    global mem
    
    mem[i] = s

def stage2(s: str, finish_func):
    global i
    global curr_symbol
    
    match s:
        case '>':
            if i < 1000:
                i += 1
            else:
                finish_func(err_code=101, end='правый')
                raise Exception()
        case '<':
            if i > 0:
                i -= 1
            else:
                finish_func(err_code=101, end='левый')
                raise Exception()
        case '!':
            end()
        case _:
            finish_func(err_code=102, unknown_symbol=s)
            raise Exception()
    curr_symbol = mem[i]

def stage3(s: str):
    global curr_state
    
    curr_state = s

def init_mem(s: str, mem_start: int, finish_func):
    global mem
    
    for j in range(len(s)):
        if mem_start + j <= 1000:
            mem[mem_start + j] = s[j]
        else:
            finish_func(err_code=103)
            raise Exception()

def step(vis_func, wait_func, finish_func):
    command = program[curr_state][curr_symbol]
    if command == ' ':
        raise Exception(str.format('Переход к пустой команде в столбце {0} и строке {1}', curr_state, curr_symbol))    
    stage1(command[0])
    
    stage2(command[1], finish_func)
    if command[1] == '!':
        vis_func(mem=mem, i=i, state=curr_state, symbol=curr_symbol, command=command)
        return
    
    if command[2::] in program:
        stage3(command[2::])
    else:
        finish_func(err_code=100)
        raise Exception()
    
    vis_func(mem=mem, i=i, state=curr_state, symbol=curr_symbol, command=command)
    wait_func()

def print_mem(mem_len=20, **kwargs):
    if i < mem_len:
        start = 0
        end = mem_len
        i_highlight = i
    else:
        start = i - mem_len // 2
        end = i + mem_len // 2
        i_highlight = i - start
    print('\n' * 5)
    print('Состояние головки:', curr_state, '\tТекущий символ:', curr_symbol)
    print('Команда:', kwargs['command'])
    for j in range(start, end + 1):
        print(' ' + mem[j] + ' ', end='')
    print('')
    print(' ' * ((i - start) * 3 + 1) + '^')








def main(vis_func=print_mem, wait_func=None, finish_func=None):

    if wait_func == None:
        def wait_func():
            pass
    if finish_func == None:
        def finish_func(err_code, **kwargs):
            print('ERROR', err_code)
    
    command = program[curr_state][curr_symbol]

    
    while running:
        step(vis_func, wait_func, finish_func)
    finish_func(err_code=0)
        

mem = [' ' for i in range(1000)]
init_mem('111+11', 100, finish_func)
i = 110
program = {
        'q0': {' ': ' <q1', '1': '1>q0', '+': '+>q0'},
        'q1': {' ': ' <q0', '1': ' <q2', '+': ' !'},
        'q2': {' ': '1>q0', '1': '1<q2', '+': '+<q2'}
        }
curr_state = 'q0'
vis = False
curr_symbol = mem[i]
running = False

if __name__ == '__main__':
    if not vis:
        print_mem(mem=mem, i=i, state=curr_state, symbol=curr_symbol, command='None')
    running = True
    main()

def run_vis(vis_func=None, wait_func=None, finish_func=None, **kwargs):
    global mem
    global i
    global program
    global curr_state
    global vis
    global curr_symbol
    global running

    
    mem = [' ' for i in range(1000)] if 'mem' not in kwargs else kwargs['mem']
    start_string = '111+11' if 'start_string' not in kwargs else kwargs['start_string']
    start_i_for_start_string =  100 if 'start_i_for_start_string' not in kwargs else kwargs['start_i_for_start_string']

    if finish_func == None:
        def finish_func(err_code, **kwargs):
            print('ERROR', err_code)

    init_mem(start_string, start_i_for_start_string, finish_func)
    i = 110 if 'start_i' not in kwargs else kwargs['start_i']
    program = {
            'q0': {' ': ' <q1', '1': '1>q0', '+': '+>q0'},
            'q1': {' ': ' <q0', '1': ' <q2', '+': ' !'},
            'q2': {' ': '1>q0', '1': '1<q2', '+': '+<q2'}
            } if 'program' not in kwargs else kwargs['program']
    curr_state = 'q0' if 'start_state' not in kwargs else kwargs['start_state']
    vis = vis_func != None
    curr_symbol = mem[i]
    running = True
    if wait_func == None:
        def wait_func():
            pass
    
    if vis_func:
        main(vis_func, wait_func, finish_func)



        
