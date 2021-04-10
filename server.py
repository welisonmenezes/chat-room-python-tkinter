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
            send_serialized(current_client, message)
    else:
        for client in clients:
            send_serialized(client, message)


# def broadcastFile(current_client, message):
#     if message.recipient != None and message.recipient != 'None':
#         index = logins.index(message.recipient)
#         recipient = clients[index]
#         if current_client != recipient:
#             recipient.send(message)
#             current_client.send(message)
#     else:
#         for client in clients:
#             #if current_client != client:
#             client.send(message)


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
    # recebo o nome do arquivo enviado

    the_recipient = None
    the_file_name = message
    the_file_path = f'{threadId}.jpg'

    #abro o arquio temporario
    arq = open(f'server_files{os.path.sep}{the_file_path}', 'wb')

    cont = 0
    while message:
        if cont > 0:
            # se receber a flag done, sai do loop
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

    # fecho o arquivo temporario
    arq.close()
    time.sleep(.5)

    message = Message()
    if the_recipient != None and the_recipient != 'None':
        message.recipient = the_recipient
    message.command = 'REQUEST_PATH'
    message.message = f'{the_file_name.decode()}'
    message.user = get_login_by_client(client)
    broadcast(client, message)
    message.command = None
    message.recipient = None
    message.message = None
    message.user = None

    the_file = [the_file_path, the_file_name]
    



def server_send_file_to_client(client):
    global the_file
    print(the_file)
    # envio o nome do arquivo enviado
    client.send(the_file[1])
    time.sleep(.1)

    # abro o arquivo temporário, leio seu conteúdo e envio ao cliente
    arq2 = open(f'server_files{os.path.sep}{the_file[0]}', 'rb')
    data = arq2.read()
    client.send(data)
    time.sleep(.1)

    # envio a flag de done para o cliente
    client.send(b'done')
    time.sleep(.1)

    # fecho o arquivo que foi lido
    arq2.close()
    print('Arquivo do servidor fechado.')




def handle(client, threadId):
    global the_file
    while True:
        #print(f'Id da trhead é: {threadId}')
        message = Message()
        try:
            b_data = client.recv(1024)
            if b_data:
                try:
                    data = get_serialized_message(client, b_data)

                    if data.command == 'LOGIN':
                        make_client_login(client, data, message)

                    elif data.command == 'LOGOUT':
                        message = Message()
                        message.command = 'LOGOUT_DONE'
                        send_serialized(client, message)
                        message.command = None
                        time.sleep(.1)
                        logout(client)
                        break

                    elif data.command == 'SEND_PATH':
                        server_send_file_to_client(client)

                    else:
                        broadcast(client, data)

                except:
                    try:
                        server_receive_save_file(client, b_data, threadId)
                    except:
                        pass
            else:
                print('erro 1')
                logout(client)
                break
        except Exception as e:
            print(e)
            print('erro 2')
            logout(client)
            break





# escutando para receber novas conexões
def receive():
    while True:
        message = Message()
        client, address = server.accept()
        print(f'Conectado com {str(address)}')

        data = get_serialized_message(client)

        make_client_login(client, data, message)
        
        threadId = str(uuid.uuid4())
        threading.Thread(target=handle, args=(client, threadId)).start()

print('Server is listening...')
receive()