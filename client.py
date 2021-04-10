import socket, threading, time, os
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from model import *
from utils import *

class ClientGUI:

    '''
        INICIALIZA A INTERFACE GRÁFICA DA APLICAÇÃO
    '''
    def __init__(self):
        # cria e configura a janela
        self.window = Tk()
        self.window.title('Chatroom ABC Bolinhas')
        self.window.geometry('870x700+0+0')
        self.window.configure(background='#2b2d42', pady=30)
        self.window.protocol('WM_DELETE_WINDOW', self._close)

        # chama metodo pra construir os elementos da tela
        self._build()

        # inicializa alguns atributos
        self.message = Message()
        self.file_path = ''
        

    '''
        CHAMA OS METODOS QUE CONSTRÓI OS ELEMENTOS DA TELA
    '''
    def _build(self):
        self._build_message_area()
        self._build_connecteds_area()
        self._build_entry_area()
        self._build_you_area()
        self._build_actions_area()
        

    '''
        CONSTRÓI A AREA DE MENSAGEM
    '''
    def _build_message_area(self):
        lb_messages = LabelFrame(self.window, text='Mensagens recebidas', height=30, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        self.f_messages = Text(lb_messages, height=22, width=59, background='#edf2f4', font=('Arial', 14))
        self.f_messages.configure(state='disabled')
        self.f_messages.pack()
        lb_messages.grid(row=0, column=0, sticky='we', padx=10)


    '''
        CONSTRÓI A AREA DOS USUÁRIOS CONECTADOS
    '''
    def _build_connecteds_area(self):
        lb_connecteds = LabelFrame(self.window, text='Enviar para:', height=30, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        self.f_connecteds = Listbox(lb_connecteds, height=21, width=15, background='#edf2f4', font=('Arial', 14))
        self.f_connecteds.pack()
        lb_connecteds.grid(row=0, column=1)


    '''
        CONSTRÓI A AREA ENVIO DE MENSAGEM
    '''
    def _build_entry_area(self):
        lb_text = LabelFrame(self.window, text='Digite uma mensagem:', height=5, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        self.f_text = Entry(lb_text, width=60, background='#edf2f4', font=('Arial', 14))
        self.f_text.pack(side=LEFT)
        lb_text.grid(row=1, column=0, sticky='we', padx=10, ipady=6, pady=10)

    
    '''
        CONSTRÓI A AREA ONDE APARECE O NOME DO USUÁRIO CORRENTE
    '''
    def _build_you_area(self):
        lb_you = LabelFrame(self.window, text='Conectado como:', height=5, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        self.f_you_label = Label(lb_you, text='', fg='white', background='#8d99ae', font=('Arial', 13, 'bold'), padx=10)
        self.f_you_label.pack(side=LEFT)
        lb_you.grid(row=1, column=1, sticky='we', padx=10, ipady=6, pady=10)


    '''
        CONSTRÓI A AREA DE AÇÕES (BOTÕES)
    '''
    def _build_actions_area(self):
        lb_actions = LabelFrame(self.window, text='', height=10, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')

        self.f_send = Button(lb_actions, text='Enviar', width=10, command=self._send_message, background='#8d99ae', font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        self.f_send.pack(side=LEFT)

        self.f_file = Button(lb_actions, text='Arquivo', width=10, command=self._send_file, background='#8d99ae', font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        self.f_file.pack(side=LEFT)

        self.f_logout = Button(lb_actions, text='Sair', width=10, background='#8d99ae', command=self._desconnect, font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        self.f_logout.pack(side=RIGHT)

        self.f_connect = Button(lb_actions, text='Conectar', width=10, command=self._popup, background='#64a6bd', font=('Arial', 12), fg='white', cursor='hand2')
        self.f_connect.pack(side=RIGHT)

        lb_actions.grid(row=2, column=0, columnspan=2, sticky='we', ipady=5, padx=10, ipadx=10)


    '''
        METODO QUE CONSTROI O POPUP (PARA FAZER O LOGIN)
    '''
    def _popup(self):
        # cria e configura a janela de popup
        self.popup = Tk()
        self.popup.configure(background='#2b2d42', pady=30)
        self.popup.title('Login') 
        self.popup.protocol('WM_DELETE_WINDOW', self._close_popup)

        # desabilita o botao de conectar
        self.f_connect['state'] = DISABLED
        self.f_connect['background'] = '#8d99ae'

        # chama método que constrói os elementos do popup
        self._build_popup_elements()
        
        # starta o popup
        self.popup.mainloop()


    '''
        METODO QUE CONSTROI OS ELEMENTOS DE TELA DO POPUP
    '''
    def _build_popup_elements(self):
        f_label_login = Label(self.popup, text='Informe seu login', fg='white', background='#2b2d42', font=('Arial', 12))
        f_label_login.grid(row=0, column=0)
        self.f_login = Entry(self.popup, width=30, background='#edf2f4', font=('Arial', 14))
        self.f_login.grid(row=1, column=0, sticky='we', padx=10, ipady=6, pady=10)
        self.f_do_login = Button(self.popup, text='Entrar', width=10, command=self._do_login, background='#64a6bd', font=('Arial', 12), fg='white', cursor='hand2')
        self.f_do_login.grid(row=1, column=1, sticky='we', padx=10, ipady=6, pady=10)
        self.f_label_fail = Label(self.popup, text='', fg='#ef233c', background='#2b2d42', font=('Arial', 12))

    
    '''
        HABILITA OS BOTÕES PARA QUANDO O USUÁRI ESTÁ CONECTADO
    '''
    def _enable_actions(self):
        self.f_send['state'] = NORMAL
        self.f_send['background'] = '#5BBA6F'
        self.f_file['state'] = NORMAL
        self.f_file['background'] = '#395697'
        self.f_connect['state'] = DISABLED
        self.f_connect['background'] = '#8d99ae'
        self.f_logout['state'] = NORMAL
        self.f_logout['background'] = '#ef233c'

    
    '''
        DESABILITA OS BOTÕES PARA QUANDO O USUÁRI ESTÁ DESCONECTADO
    '''
    def _disable_actions(self):
        self.f_send['state'] = DISABLED
        self.f_send['background'] = '#8d99ae'
        self.f_file['state'] = DISABLED
        self.f_file['background'] = '#8d99ae'
        self.f_connect['state'] = NORMAL
        self.f_connect['background'] = '#64a6bd'
        self.f_logout['state'] = DISABLED
        self.f_logout['background'] = '#8d99ae'


    '''
        MÉTODO QUE VALIDA O FORM DE LOGIN E FAZ O LOGIN
    '''
    def _do_login(self):
        if (not self.f_login.get()):
            self._show_validation_error('Campo obrigatório.')
        else:
            self.message.user = self.f_login.get()
            self.message.command = 'LOGIN'

            # chama metodo para conectar o cliente
            if not self._connect_client():
                self._show_validation_error('Servidor indisponível.')
            else:
                self.f_you_label['text'] = self.message.user


    '''
        MÉTODO QUE CONECTA O CLIENTE AO SERVIDOR (CHAMADO PELO LOGIN)
    '''
    def _connect_client(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.client.connect_ex(('127.0.0.1', 10000)) == 0:
                send_serialized(self.client, self.message)
                threading.Thread(target=self._receive).start()
            else:
                send_serialized(self.client, self.message)
            return True
        except Exception as e:
            return False


    '''
        HELPER QUE MOSTRA MENSAGEM DE ERRO NA TELA DE LOGIN
    '''
    def _show_validation_error(self, message):
        self.f_label_fail['text'] = message
        self.f_label_fail.grid(row=2, column=0)


    '''
        HELPER QUE EXIBE AS MENSAGENS RECEBIDAS NA TELA
    '''
    def _show_message_on_screen(self, message):
        self.f_messages.configure(state='normal')
        self.f_messages.insert(INSERT, f'{message} \n')
        self.f_messages.see(END)
        self.f_messages.configure(state='disabled')


    '''
        HELPER QUE ATUALIZA OS USUÁRIO CONECTADOS NA TELA 
    '''
    def _update_users_on_screen(self, message):
        users = message.split('@@@')
        self.users = []
        self.f_connecteds.delete(0,END)
        self.f_connecteds.insert(0, 'Todos')
        i = 1
        for user in users:
            if user != self.message.user:
                self.f_connecteds.insert(i, user)
                self.users.append(user)
                i = i + 1
        self.f_connecteds.select_set(0)


    '''
        MÉTODO SETA O DESTINATÁRIO DA MENSAGEM NO OBJETO DE MENSAGEM (O QUAL SERÁ ENVIADO COM AS MENSAGENS)
    '''
    def _set_the_recipient(self):
        selected = self.f_connecteds.curselection()
        if selected and selected[0] != 0:
            self.message.recipient = self.users[selected[0] - 1]
        else:
            self.message.recipient = None


    '''
        MÉTODO QUE ENVIA A MENSAGE DO CLIENTE PARA O SERVIDOR
    '''
    def _send_message(self):
        text = self.f_text.get()
        if text:
            self._set_the_recipient()
            self.message.message = text
            self.message.command = 'MESSAGE'
            send_serialized(self.client, self.message)
            self.message.command = None
            self.f_text.delete(0, END)
            self.f_text.insert(0, '')


    '''
        MÉTODO QUE ENVIA O ARQUIVO SELECIONADO PELO CLIENTE PARA O SERVIDOR
    '''
    def _send_file(self):
        self._set_the_recipient()

        # solicita o arquivo
        file_path = filedialog.askopenfilename(initialdir = os.path.sep, title = 'Escolha um arquivo')

        if (file_path and file_path != None and file_path != ''):
            file_info  = file_path.split('/')
            file_name = file_info.pop()
            recipient = 'None'
            
            # recupera o destinatário (se houver)
            if self.message.recipient != None:
                recipient = self.message.recipient

            # envia o nome do arquivo selecionado
            self.client.send(file_name.encode())
            time.sleep(.1)

            # envia o nome do destinatário (se houver)
            self.client.send(recipient.encode())
            time.sleep(.1)

            # envia o arquivo selecionado
            selected_file = open(file_path,'rb')
            data = selected_file.read()
            self.client.send(data)
            time.sleep(.1)

            # envia flag sinalizando que arquivo foi todo enviado
            self.client.send('done'.encode())
            time.sleep(.1)

            # fecha o arquivo
            selected_file.close()
            print('Arquivo de envio fechado.')


    '''
        MÉTODO QUE ATUALIZA O DIRETÓRIO ONDE O USUÁRIO SALVARÁ O ARQUIVO RECEBIDO
        CHAMADO SEMPRE QUE ALGUÉM LHE ENVIAR UM ARQUIVO
    '''
    def _send_file_path(self):
        # seleciona o diretório
        self.file_path = None
        self.file_path = filedialog.askdirectory()
        if (self.file_path and self.file_path != None and self.file_path != ''):

            # notifica ao servidor que o diretório onde salvar foi atualizado
            time.sleep(.1)
            self.message.command = 'SEND_PATH'
            send_serialized(self.client, self.message)
            self.message.command = None


    '''
        MÉTODO QUE RECEBE O ARQUIVO ENVIADO PELO SERVIDOR AOS DESTINATÁRIOS
        (APÓS O SERVIDOR SALVAR UM ARQUIVO ENVIADO ESTE O ENVIA AOS DESTINATÁRIOS)
    '''
    def client_receive_save_file(self, data):

        # recupera o nome do arquivo enviado (o qual o servidor repassou)
        send_filename = data

        # cria um arquivo com diretório escolhido e mesmo nome do arquivo enviado
        save_as = f'{self.file_path}{os.path.sep}{send_filename.decode()}'
        arq = open(save_as, 'wb')

        cont = 0
        while data:

            if cont > 0:
                # se sinalizado como done e sai do loop
                if data == b'done':
                    arq.close()
                    break
                
                # escreve o conteudo recebido no arquivo q está sendo salvo
                arq.write(data)
                data = self.client.recv(1024)
            else:
                # pula a primeira mensagem (onde foi recuperado nome do arquivo)
                data = self.client.recv(1024)
                cont = cont + 1

        # fecha o arquivo salvo
        arq.close()


    '''
        MÉTODO QUE ESCUTA AS MENSAGENS ENVIADAS PELO SERVIDOR
        (ESTÁ NUMA THREAD)
    '''
    def _receive(self):
        while True:
            try:
                b_data = self.client.recv(1024)
                if b_data:

                    try:
                        # mensagens em geral
                        data = get_serialized_message(self.client, b_data)

                        # falha no login (servidor notificou que já existe o login informado conectado)
                        if data.command == 'LOGIN_INVALID':
                            self._disable_actions()
                            self._show_validation_error('Por favor, escolha outro login.')
                        
                        # login bem sucedido (servidor notificou que login foi realizado com sucesso)
                        elif data.command == 'LOGIN_VALID':
                            self.message.command = None
                            self._enable_actions()
                            self.popup.destroy()

                        # atualizar lista de conectados (servidor notificou que lista de usuários foi alterada)
                        elif data.command == 'UPDATE_USERS':
                            self.message.command = None
                            self._update_users_on_screen(data.message)

                        # receber mensagem (servidor notificou nova mensagem)
                        elif data.command == 'MESSAGE':
                            self._show_message_on_screen(f'{data.user}: {data.message}')

                        # selecionar onde salvar o arquivo (servidor notificou novo arquivo a ser enviado)
                        elif data.command == 'REQUEST_PATH':
                            self._show_message_on_screen(f'{data.user}: {data.message}')
                            self._send_file_path()

                        # desconectar no cliente (servidor notificou que o mesmo já foi desconectado no servidor)
                        elif data.command == 'LOGOUT_DONE':
                            self._reset_gui()
                            self.client.close()
                            break

                    except:
                        # mensagens binárias (inclui arquivos)
                        self.client_receive_save_file(b_data)
                        
                else:
                    self.client.close()
                    break
            except Exception as e:
                self.client.close()
                break

    
    '''
        CALLBACK QUE ESCUTA QUANDO A JANELA É FECHADA
    '''
    def _close(self):
        self.window.destroy()
        self.client.close()
        try:
            self.popup.destroy()
        except Exception as e:
            pass


    '''
        MÉTODO QUE SOLICITA QUE O SERVIDOR DESCONECTA O CLIENTE
        (SERVIDOR NOTIFICARÁ EM SEGUIDA)
    '''
    def _desconnect(self):
        self.message.command = 'LOGOUT'
        send_serialized(self.client, self.message)
        self.message.command = None

    
    '''
        CALLBACK QUE ESCUTA QUANDO O POPUP É FECHADO
    '''
    def _close_popup(self):
        self.popup.destroy()

        # habilita botão de conectar
        self.f_connect['state'] = NORMAL
        self.f_connect['background'] = '#64a6bd'


    '''
        MÉTODO QUE RESETA A TELA (CHAMDO APÓS O LOGOUT DO USUÁRIO)
    '''
    def _reset_gui(self):
        self._disable_actions()
        self.f_you_label['text'] = ''
        self.f_connecteds.delete(0, END)
        self.f_messages.configure(state='normal')
        self.f_messages.delete('1.0', END)
        self.f_messages.configure(state='disabled')

    
    '''
        MÉTODO QUE INICIALIZA A INTERFACE
    '''
    def run(self):
        self.window.mainloop()
    

ClientGUI().run()
