import tkinter as tk
from tkinter import *
from tkinter import filedialog

class GUIHelper():

    def __init__(self):
        pass

    
    '''
        CONTROI E RETORNA A JANELA PRINCIAPL
    '''
    def window_build(self, close_callback):
        window = Tk()
        window.title('Chatroom ABC Bolinhas')
        window.geometry('870x700+0+0')
        window.configure(background='#2b2d42', pady=30)
        window.protocol('WM_DELETE_WINDOW', close_callback)
        return window


    '''
        CONSTROI A AREA DE MENSAGENS E RETORNA O ELEMENTO DE MENSGENS
    '''
    def message_area_build(self, window, title, height=22):
        lb_messages = LabelFrame(window, text=title, height=30, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        text_area = Text(lb_messages, height=height, width=59, background='#edf2f4', font=('Arial', 14))
        text_area.configure(state='disabled')
        text_area.pack()
        lb_messages.grid(row=0, column=0, sticky='we', padx=10)
        return text_area


    '''
        CONSTROI A AREA DE CONECTADOS E RETORNA O ELEMENTO DE CONECTADOS
    '''
    def connecteds_area_build(self, window, title, height=21):
        lb_connecteds = LabelFrame(window, text=title, height=30, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        f_connecteds = Listbox(lb_connecteds, height=height, width=15, background='#edf2f4', font=('Arial', 14))
        f_connecteds.pack()
        lb_connecteds.grid(row=0, column=1)
        return f_connecteds


    '''
        CONSTROI A AREA DE DIGITAR MENSAGEM E RETORNA O ELEMENTO DE TEXTO
    '''
    def entry_area_build(self, window, title):
        lb_text = LabelFrame(window, text=title, height=5, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        f_text = Entry(lb_text, width=60, background='#edf2f4', font=('Arial', 14))
        f_text.pack(side=LEFT)
        lb_text.grid(row=1, column=0, sticky='we', padx=10, ipady=6, pady=10)
        return f_text


    '''
        CONSTROI A AREA DO LOGADO E RETORNA A LABEL ONDE SE EXIBE O SEU LOGIN
    '''
    def connected_area_build(self, window, title):
        lb_you = LabelFrame(window, text=title, height=5, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        f_you_label = Label(lb_you, text='', fg='white', background='#8d99ae', font=('Arial', 13, 'bold'), padx=10)
        f_you_label.pack(side=LEFT)
        lb_you.grid(row=1, column=1, sticky='we', padx=10, ipady=6, pady=10)
        return f_you_label


    '''
        CONSTROI A AREA DE ACTIONS E RETORNA OS BOTÕES
    '''
    def actions_area_build(self, window, send_action, file_action, logout_action, login_action):
        lb_actions = LabelFrame(window, text='', height=10, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')

        f_send = Button(lb_actions, text='Enviar', width=10, command=send_action, background='#8d99ae', font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_send.pack(side=LEFT)

        f_file = Button(lb_actions, text='Arquivo', width=10, command=file_action, background='#8d99ae', font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_file.pack(side=LEFT)

        f_logout = Button(lb_actions, text='Sair', width=10, background='#8d99ae', command=logout_action, font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_logout.pack(side=RIGHT)

        f_connect = Button(lb_actions, text='Conectar', width=10, command=login_action, background='#64a6bd', font=('Arial', 12), fg='white', cursor='hand2')
        f_connect.pack(side=RIGHT)

        lb_actions.grid(row=2, column=0, columnspan=2, sticky='we', ipady=5, padx=10, ipadx=10)

        return [f_send, f_file, f_logout, f_connect]


    '''
        CONSTROI A JANELA DO POPUP E RETORNA A MESMA
    '''
    def login_popup_build(self, window, title, open_callback, close_callback):
        # cria e configura a janela de popup
        popup = Tk()
        popup.configure(background='#2b2d42', pady=30)
        popup.title(title) 
        popup.protocol('WM_DELETE_WINDOW', close_callback)

        # chama método que constrói os elementos do popup
        open_callback(popup)

        return popup


    '''
        CONSTROI OS ELEMENTOS DA TELA DE POPUP E RETORNA OS CAMPOS
        (CHAMADO NO OPEN CALLBACK DO POPUP)
    '''
    def login_popup_elements_build(self, popup, title, do_login_action):
        f_label_login = Label(popup, text=title, fg='white', background='#2b2d42', font=('Arial', 12))
        f_label_login.grid(row=0, column=0)
        f_login = Entry(popup, width=30, background='#edf2f4', font=('Arial', 14))
        f_login.grid(row=1, column=0, sticky='we', padx=10, ipady=6, pady=10)
        f_do_login = Button(popup, text='Entrar', width=10, command=do_login_action, background='#64a6bd', font=('Arial', 12), fg='white', cursor='hand2')
        f_do_login.grid(row=1, column=1, sticky='we', padx=10, ipady=6, pady=10)
        f_label_fail = Label(popup, text='', fg='#ef233c', background='#2b2d42', font=('Arial', 12))

        return [f_login, f_do_login, f_label_fail]


    '''
        HELPER QUE HABILITA OS ACTIONS
    '''
    def enable_actions(self, context):
        context.f_send['state'] = NORMAL
        context.f_send['background'] = '#5BBA6F'
        context.f_file['state'] = NORMAL
        context.f_file['background'] = '#395697'
        context.f_connect['state'] = DISABLED
        context.f_connect['background'] = '#8d99ae'
        context.f_logout['state'] = NORMAL
        context.f_logout['background'] = '#ef233c'


    '''
        HELPER QUE DESABILITA OS ACTIONS
    '''
    def disabled_actions(self, context):
        context.f_send['state'] = DISABLED
        context.f_send['background'] = '#8d99ae'
        context.f_file['state'] = DISABLED
        context.f_file['background'] = '#8d99ae'
        context.f_connect['state'] = NORMAL
        context.f_connect['background'] = '#64a6bd'
        context.f_logout['state'] = DISABLED
        context.f_logout['background'] = '#8d99ae'


    '''
        HELPER QUE ATUALIZA A AREA DE MENSAGENS
    '''
    def update_message_area(self, message_area, message):
        message_area.configure(state='normal')
        message_area.insert(INSERT, f'{message} \n')
        message_area.see(END)
        message_area.configure(state='disabled')