import threading, socket, pickle, base64, time, uuid, os
from model import *
from utils import *

clients = []
logins = []
the_file = []


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 10000))
server.listen()


def broadcast(current_client, message):
    if message.recipient != None and message.recipient != 'None':
        index = logins.index(message.recipient)
        recipient = clients[index]
        if current_client != recipient:
            send_serialized(recipient, message)
            if message.command != 'REQUEST_PATH':
                send_serialized(current_client, message)
    else:
        for client in clients:
            if message.command == 'REQUEST_PATH':
                if client != current_client:
                    send_serialized(client, message)
            else:
                send_serialized(client, message)


def broadcast_users_update(client):
    time.sleep(.1)
    message = Message()
    message.command = 'UPDATE_USERS'
    message.message = '@@@'.join(logins)
    broadcast(client, message)
    message.command = None


def logout(client):
    try:
        index = clients.index(client)
        login = logins[index]
        clients.remove(client)
        logins.remove(login)
        broadcast_users_update(client)
    finally:
        client.close()


def make_client_login(client, data, message):
    if data.user in logins:
        feedback_login_status(client, 'LOGIN_INVALID')
    else:
        logins.append(data.user)
        clients.append(client)
        feedback_login_status(client, 'LOGIN_VALID')
        broadcast_users_update(client)


def feedback_login_status(client, command):
    message = Message()
    message.command = command
    send_serialized(client, message)
    message.command = None


def get_login_by_client(client):
    index = clients.index(client)
    return logins[index]


def server_receive_save_file(client, message, threadId):
    global the_file
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
    message.user = get_login_by_client(client)
    broadcast(client, message)
    message.command = None
    message.recipient = None
    message.message = None
    message.user = None

    # salva globalmente o nome do arquivo enviado e o nome do arquivo salvo no servidor
    # essa informação será usada no próximo passo (ao enviar para os destinatários)
    the_file = [saved_file_name, received_file_name]
    

def server_send_file_to_client(client):
    global the_file

    # envia o nome do arquivo enviado (pois o cliente salvará com o mesmo nome)
    client.send(the_file[1])
    time.sleep(.1)

    # abre o arquivo salvo no servidor, lê seu conteúdo e envio ao cliente
    arq2 = open(f'server_files{os.path.sep}{the_file[0]}', 'rb')
    data = arq2.read()
    client.send(data)
    time.sleep(.1)

    # envia a flag de done para o cliente, para que ele possa fechar o arquivo do seu lado
    client.send(b'done')
    time.sleep(.1)

    # fecha o arquivo que foi lido
    arq2.close()


def handle(client, threadId):
    global the_file

    while True:
        message = Message()
        try:
            b_data = client.recv(1024)
            if b_data:
                try:
                    data = get_serialized_message(client, b_data)

                    # o cliente requisitou para fazer o login
                    if data.command == 'LOGIN':
                        make_client_login(client, data, message)

                    # o cliente requisitou para fazer o logout
                    elif data.command == 'LOGOUT':
                        message = Message()
                        message.command = 'LOGOUT_DONE'
                        send_serialized(client, message)
                        message.command = None
                        time.sleep(.1)
                        logout(client)
                        break
                    
                    # o cliente escolheu onde quer salver e notifiou o servidor 
                    # (o mesmo enviará o arquivo agora)
                    elif data.command == 'SEND_PATH':
                        server_send_file_to_client(client)

                    # broatcast das mensagens em geral
                    else:
                        broadcast(client, data)

                except:
                    # broadcast dos arquivos binários (arquivos incluso)
                    try:
                        server_receive_save_file(client, b_data, threadId)
                    except Exception as e:
                        pass
            else:
                logout(client)
                break
        except Exception as e:
            logout(client)
            break


# escuta para receber novas conexões
def receive():
    while True:
        message = Message()
        client, address = server.accept()
        print(f'Conectado com {str(address)}')

        # recebe primeiro contato do cliente (solicitação de login)
        data = get_serialized_message(client)
        make_client_login(client, data, message)
        
        threadId = str(uuid.uuid4())
        threading.Thread(target=handle, args=(client, threadId)).start()

print('Servidor online...')
receive()