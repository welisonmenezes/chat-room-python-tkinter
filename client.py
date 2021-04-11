import socket, threading, time, os
from gui_helper import *
from model import *
from utils import *

class Client:

    '''
        INICIALIZA A INTERFACE GRÁFICA DA APLICAÇÃO
    '''
    def __init__(self):
        # cria e configura a janela
        self.gui_helper = GUIHelper()
        self.window = self.gui_helper.window_build(self._close_callback)

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
        self.f_messages = self.gui_helper.message_area_build(self.window, 'Mensagens recebidas:')


    '''
        CONSTRÓI A AREA DOS USUÁRIOS CONECTADOS
    '''
    def _build_connecteds_area(self):
        self.f_connecteds = self.gui_helper.connecteds_area_build(self.window, 'Enviar para:')


    '''
        CONSTRÓI A AREA ENVIO DE MENSAGEM
    '''
    def _build_entry_area(self):
        self.f_text = self.gui_helper.entry_area_build(self.window, 'Digite uma mensagem:')

    
    '''
        CONSTRÓI A AREA ONDE APARECE O NOME DO USUÁRIO CORRENTE
    '''
    def _build_you_area(self):
        self.f_you_label = self.gui_helper.connected_area_build(self.window, 'Conectado como:')


    '''
        CONSTRÓI A AREA DE AÇÕES (BOTÕES)
    '''
    def _build_actions_area(self):
        actions = self.gui_helper.actions_area_build(self.window, self._send_message, self._send_file, self._desconnect, self._popup)
        self.f_send, self.f_file, self.f_logout, self.f_connect = actions


    '''
        METODO QUE CONSTROI O POPUP (PARA FAZER O LOGIN)
    '''
    def _popup(self):
        self.popup = self.gui_helper.login_popup_build(self.window, 'Login', self._open_popup_callback, self._close_popup_callback)
        self.popup.mainloop()


    '''
        METODO QUE CONSTROI OS ELEMENTOS DE TELA DO POPUP
    '''
    def _open_popup_callback(self, popup):
        self.f_login, self.f_do_login, self.f_label_fail = self.gui_helper.login_popup_elements_build(popup, 'Informe seu login', self._do_login)
        self.f_connect['state'] = DISABLED
        self.f_connect['background'] = '#8d99ae'

    
    '''
        HABILITA OS BOTÕES PARA QUANDO O USUÁRI ESTÁ CONECTADO
    '''
    def _enable_actions(self):
        self.gui_helper.enable_actions(self)

    
    '''
        DESABILITA OS BOTÕES PARA QUANDO O USUÁRI ESTÁ DESCONECTADO
    '''
    def _disable_actions(self):
        self.gui_helper.disabled_actions(self)


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
        self.gui_helper.update_message_area(self.f_messages, message)


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
    def _close_callback(self):
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
    def _close_popup_callback(self):
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
    

Client().run()