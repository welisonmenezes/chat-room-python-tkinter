import threading, socket, pickle, base64, time, uuid, os, logging
from datetime import datetime
import tkinter as tk
from tkinter import *
from model import *
from utils import *


class ServerGUI:

    '''
        INICIALIZA A INTERFACE GRÁFICA DO SERVIDOR
    '''
    def __init__(self):
        # cria e configrua a janela
        self.window = Tk()
        self.window.title('Chatroom ABC Bolinhas - Servidor')
        self.window.geometry('870x700+0+0')
        self.window.configure(background='#2b2d42', pady=30)
        self.window.protocol('WM_DELETE_WINDOW', self._close)

        # inicializa alguns atributos
        self.clients = []
        self.logins = []
        self.the_file = []

        # chama metodo pra construir os elementos da tela
        self._build()


    '''
        CHAMA OS METODOS QUE CONSTRÓI OS ELEMENTOS DA TELA
    '''
    def _build(self):
        self._build_message_area()
        self._build_connecteds_area()


    '''
        CONSTRÓI A AREA DE LOG
    '''
    def _build_message_area(self):
        lb_messages = LabelFrame(self.window, text='Logs do servidor', height=30, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        self.f_messages = Text(lb_messages, height=28, width=59, background='#edf2f4', font=('Arial', 14))
        self.f_messages.configure(state='disabled')
        self.f_messages.pack()
        lb_messages.grid(row=0, column=0, sticky='we', padx=10)


    '''
        CONSTRÓI A AREA DOS USUÁRIOS CONECTADOS
    '''
    def _build_connecteds_area(self):
        lb_connecteds = LabelFrame(self.window, text='Conectados', height=30, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        self.f_connecteds = Listbox(lb_connecteds, height=27, width=15, background='#edf2f4', font=('Arial', 14))
        self.f_connecteds.pack()
        lb_connecteds.grid(row=0, column=1)


    '''
        HELPER QUE EXIBE OS LOGS NA TELA
    '''
    def _show_message_on_screen(self, message):
        self.f_messages.configure(state='normal')
        self.f_messages.insert(INSERT, f'{message} \n')
        self.f_messages.see(END)
        self.f_messages.configure(state='disabled')


    '''
        HELPER QUE ATUALIZA OS USUÁRIO CONECTADOS NA TELA 
    '''
    def _update_users_on_screen(self):
        self.f_connecteds.delete(0,END)
        i = 0
        for user in self.logins:
            self.f_connecteds.insert(i, user)
            i = i + 1


    '''
        NOTIFICA OS DESTINATÁRIOS COM NOVA MENSAGEM
    '''
    def broadcast(self, current_client, message):
        recipient = self.get_recipient(message)
        if recipient != None:
            # aqui existe destinatários selecionados
            if current_client != recipient:
                send_serialized(recipient, message)

                # o cliente que enviou a imagem não precisa recebê-la
                if message.command != 'REQUEST_PATH':
                    send_serialized(current_client, message)
        else:
            # aqui a mensagem é para todos os conectados
            for client in self.clients:

                # o cliente que enviou a imagem não precisa recebê-la
                if message.command == 'REQUEST_PATH':
                    if client != current_client:
                        send_serialized(client, message)
                else:
                    send_serialized(client, message)


    '''
        NOTIFICA OS CLIENTES COM LISTA DE CONECTADOS
    '''
    def broadcast_users_update(self, client):
        time.sleep(.1)
        message = Message()
        message.command = 'UPDATE_USERS'
        message.message = '@@@'.join(self.logins)
        self.broadcast(client, message)
        message.command = None


    '''
        PEGA O DESTINATÁRIO CASO EXISTA NO ATRIBUTO RECIEPIENT DO OBJETO DE MENSAGEM
    '''
    def get_recipient(self, message):
        if message.recipient != None and message.recipient != 'None':
            index = self.logins.index(message.recipient)
            recipient = self.clients[index]
            if recipient:
                return recipient
        return None


    '''
        REALIZA O LOGOUT DO CLIENTE
    '''
    def logout(self, client):
        try:
            index = self.clients.index(client)
            login = self.logins[index]

            # log o logout
            self.server_log(client, 'Logout')

            # remove do lista de conectados
            self.clients.remove(client)
            self.logins.remove(login)

            # notifica os clientes com a nova lista de conectados
            self.broadcast_users_update(client)
            self._update_users_on_screen()
        finally:
            client.close()


    '''
        FAZ O LOGIN DO CLIENTE
    '''
    def make_client_login(self, client, data, message):
        if data.user in self.logins:
            # se login já existe, notifica cliente para que este use outro
            self.feedback_login_status(client, 'LOGIN_INVALID')
        else:
            # login válido
            self.logins.append(data.user)
            self.clients.append(client)
            self.feedback_login_status(client, 'LOGIN_VALID')
            self.broadcast_users_update(client)
            self._update_users_on_screen()

            # log o login
            self.server_log(client, 'Login')


    '''
        HELPER PARA MONTAR A MENSAGEM DE FEEDBACK DO LOGIN
    '''
    def feedback_login_status(self, client, command):
        message = Message()
        message.command = command
        send_serialized(client, message)
        message.command = None


    '''
        PEGA O LOGIN PELO DADO CLIENTE
    '''
    def get_login_by_client(self, client):
        index = self.clients.index(client)
        return self.logins[index]


    '''
        RECEBE O ARQUIVO DO CLIENTE E SALVA NO SERVIDOR
    '''
    def server_receive_save_file(self, client, message, threadId):

        the_recipient = None
        received_file_name = message # recebe o nome do arquivo enviado
        saved_file_name = f'{threadId}.jpg' # gera nome único para salvar o arquivo recebido

        # abre um arquio para salvar no servidor
        arq = open(f'server_files{os.path.sep}{saved_file_name}', 'wb')

        # inicia a escrita do novo arquivo
        cont = 0
        while message:
            if cont > 0:
                # na primeria iteração pula, pois é onde recebeu o nome do arquivo
                # ao receber a flag b'done' finaliza a escrita
                if cont == 1:
                    the_recipient = message.decode()
                elif message == b'done':
                    break
                else:
                    arq.write(message)
                message = client.recv(1024)
            else:
                # pulo a primeira msg (no do arquivo)
                message = client.recv(1024) 
            cont = cont + 1

        # fecha o arquivo 
        arq.close()
        time.sleep(.5)

        # após salvar o arquivo no servidor, notifica os destinatários
        # para que os mesmos setem onde querem salvar lá no ambiente deles
        # o cliente notificará após isso, para que o servidor possa prosseguir
        message = Message()
        if the_recipient != None and the_recipient != 'None':
            message.recipient = the_recipient
        message.command = 'REQUEST_PATH'
        message.message = f'{received_file_name.decode()}'
        message.user = self.get_login_by_client(client)
        self.broadcast(client, message)

        # salva globalmente o nome do arquivo enviado e o nome do arquivo salvo no servidor
        # essa informação será usada no próximo passo (ao enviar para os destinatários)
        self.the_file = [saved_file_name, received_file_name]

        # log envio de arquivo
        self.server_log(client, f'Arquivo: {received_file_name.decode()}', self.get_recipient(message))

        message.command = None
        message.recipient = None
        message.message = None
        message.user = None
        

    '''
        ENVIA O ARQUIVO RECÉM SALVO NO SERVIDOR PARA OS DESTINATÁRIOS
    '''
    def server_send_file_to_client(self, client):

        # envia o nome do arquivo enviado (pois o cliente salvará com o mesmo nome)
        client.send(self.the_file[1])
        time.sleep(.1)

        # abre o arquivo salvo no servidor, lê seu conteúdo e envio ao cliente
        arq2 = open(f'server_files{os.path.sep}{self.the_file[0]}', 'rb')
        data = arq2.read()
        client.send(data)
        time.sleep(.1)

        # envia a flag de done para o cliente, para que ele possa fechar o arquivo do seu lado
        client.send(b'done')
        time.sleep(.1)

        # fecha o arquivo que foi lido
        arq2.close()


    '''
        FAZ O LOG (EM ARQUIVO, TELA E TERMINAL)
    '''
    def server_log(self, client, complement, recipient=None):
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        client_ip = client.getsockname()[0]
        client_login = self.get_login_by_client(client)

        if (recipient == None):
            text_to_log = f'{now}; {client_ip}; {client_login}; {complement}'
        else:
            recipient_ip = recipient.getsockname()[0]
            recipient_login = self.get_login_by_client(recipient)
            text_to_log = f'{now}; {client_ip}; {client_login}; {recipient_ip}; {recipient_login}; {complement}'

        logging.basicConfig(filename='file.log', filemode='w', format='%(message)s')
        logging.warning(text_to_log)
        self._show_message_on_screen(text_to_log)
        print(text_to_log)


    '''
        ESCUTA AS MENSAGENS/NOTIFICAÇÕES ENVIADOS PELOS CLIENTES
        (RODA DENTRO DE UMA THREAD)
    '''
    def handle(self, client, threadId):
        while True:
            message = Message()
            try:
                b_data = client.recv(1024)
                if b_data:
                    try:
                        data = get_serialized_message(client, b_data)

                        # o cliente requisitou para fazer o login
                        if data.command == 'LOGIN':
                            self.make_client_login(client, data, message)

                        # o cliente requisitou para fazer o logout
                        elif data.command == 'LOGOUT':
                            message = Message()
                            message.command = 'LOGOUT_DONE'
                            send_serialized(client, message)
                            message.command = None
                            time.sleep(.1)
                            self.logout(client)
                            break
                        
                        # o cliente escolheu onde quer salver e notifiou o servidor 
                        # (o mesmo enviará o arquivo agora)
                        elif data.command == 'SEND_PATH':
                            self.server_send_file_to_client(client)

                        # broatcast das mensagens em geral
                        else:
                            # log envio de mensagem
                            self.server_log(client, f'Mensagem: {data.message}', self.get_recipient(data))
                            self.broadcast(client, data)

                    except:
                        # broadcast dos arquivos binários (arquivos incluso)
                        try:
                            self.server_receive_save_file(client, b_data, threadId)
                        except Exception as e:
                            pass
                else:
                    self.logout(client)
                    break
            except Exception as e:
                self.logout(client)
                break


    '''
        RECEBE NOVAS CONEXÕES DOS CLIENTES
    '''
    def receive(self):
        while True:
            message = Message()
            client, address = self.server.accept()

            # recebe primeiro contato do cliente (solicitação de login)
            data = get_serialized_message(client)
            self.make_client_login(client, data, message)
            
            threadId = str(uuid.uuid4())
            threading.Thread(target=self.handle, args=(client, threadId)).start()


    '''
        CALLBACK QUE ESCUTA QUANDO A JANELA É FECHADA
    '''
    def _close(self):
        os._exit(0)
        self.window.destroy()


    '''
        MÉTODO QUE INICIALIZA O SERVIÇO
    '''
    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 10000))
        self.server.listen()
        print('Servidor online...')
        threading.Thread(target=self.receive).start()


instance = ServerGUI()
instance.run()
instance.window.mainloop()