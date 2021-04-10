import pickle, os, time
from tkinter import filedialog
from model import *


# serializa a mensagem e as envia atravez do dado cliente
def send_serialized(client, obj_to_send, the_type='text'):
    client.send(pickle.dumps(obj_to_send))


# retorna com o objeto desserializado 
def get_serialized_message(client, data=None):
    if data is None:
        obj = pickle.loads(client.recv(1024))
        return obj
    return pickle.loads(data)


# envia o arquivo do cliente remetente para o servidor
def send_file_to_server(client, obj_to_send):
    file_path = filedialog.askopenfilename(initialdir = "/",title = "Escolha um arquivo")
    file_info  = file_path.split('/')
    filename = file_info.pop()
    recipient = obj_to_send.recipient
    
    try:
        arq = open(file_path,'rb')

        obj_to_send.message = f'{file_path}'
        obj_to_send.command = 'MESSAGE'
        send_serialized(client, obj_to_send)
        obj_to_send.command = None
        time.sleep(.1)

        #client.send(obj_to_send.user.encode())
        #time.sleep(.1)
        
        # client.send('filename'.encode())
        # time.sleep(.1)

        data = arq.read()
        client.send(data)
        arq.close()
        #time.sleep(.1)

        # client.send('DONE'.encode())
        # print('arquivo fechado')
    except:
        print('Arquivo não selecionado.')
        # time.sleep(.1)
        # client.send('ERROR'.encode())
        # time.sleep(.1)
        # client.send('DONE'.encode())


    '''
    try:
        arq = open(file_path,'rb')
        obj_to_send.message = f'{obj_to_send.user} enviou o arquivo: {file_path}'
        send_serialized(client, obj_to_send)
        time.sleep(.01)

        client.send(filename.encode('utf-8'))
        time.sleep(.01)

        data = arq.read()
        client.send(data)
        time.sleep(.01)

        client.send('DONE'.encode('utf-8'))
        arq.close()
    except:
        print('Arquivo não selecionado.')
        time.sleep(.01)
        client.send('ERROR'.encode('utf-8'))
        time.sleep(.01)
        client.send('DONE'.encode('utf-8'))
    '''



# recebe e salva o arquivo encaminhado pelo sevidor
def client_receive_save_file(client, message):
    #print(message.decode())
    if (message == b'ERROR'):
        message = client.recv(1024)
    else:
        # if '@@@' in message.decode():
        #     data = message.decode().split('@@@')
        #     data = data[1]
        # else:
        #     data = message.decode()

        #data = message.decode()
        #print(data)

        # file_info = message.split('.')
        # filename = file_info[0]
        # extension = file_info[1]
        #print(message)
        save_as = f'_filename.jpg'
        arq = open(save_as,'wb')

        # cont = 10
        while message:
            # print(message)
            # print('--------')
            # cont = cont + 1
            # if cont > 0:
                # print('outras message')
                # if (message == b'DONE'):
                #     print(f'Arquivo salvo como: xxx')
                #     arq.close()
                #     break
                # else:
            arq.write(message)
            message = client.recv(1024)
            # else:
            #     print('primeira message')
            #     message = client.recv(1024)
        print('fechou<--------')
        arq.close()
