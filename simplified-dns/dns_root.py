import socket
import sys
import threading

bind_ip = "127.0.0.1"
bind_port = int(sys.argv[2])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)

domain = open(sys.argv[1], 'r')

domain_data = domain.readlines()

def get_service(domain_data, service_name):
    for line in domain_data:
        data = line.split(' ')
        if service_name in data:
            return data[2]

def handle_client(client_socket, domain_data):
    operation = client_socket.recv(1024)
    client_socket.send("[*] Servidor: Operacao recebida.")
    info = client_socket.recv(1024)
    client_socket.send("[*] Servidor: Informacao recebida.")

    if operation.lower() == 'ip':
        for line in domain_data:
            data = line.rstrip('\n').split(' ')
            if 'IP' in data and data[0] == info:
                client_socket.send(data[2])
                client_socket.close()
                quit()

    elif operation.lower() == 'hn':
        for line in domain_data:
            data = line.rstrip('\n').split(' ')
            if 'HN' in data and data[0] == info:
                client_socket.send(data[2])
                client_socket.close()
                quit()

    elif operation.lower() == 'ns':
        for line in domain_data:
           data = line.rstrip('\n').split(' ')
           if info in data:
                client_socket.send(get_service(domain_data, 'NS'))
                client_socket.close()
                quit()

    elif operation.lower() == 'mx':
        for line in domain_data:
           data = line.rstrip('\n').split(' ')
           if info in data:
                client_socket.send(get_service(domain_data, 'MX'))
                client_socket.close()
                quit()

    elif operation.lower() == 'tc':
        for line in domain_data:
            data = line.rstrip('\n').split(' ')
            if info in data:
                client_socket.send(get_service(domain_data, 'TC'))
                client_socket.close()
                quit()

    client_socket.send("Os dados requisitados nao foram encontrados.")

while True:
    client,addr = server.accept()
    print "[*] Foi aceita conexao com: %s:%d" % (addr[0],addr[1])
    client_handler = threading.Thread(target=handle_client,args=(client, domain_data))
    client_handler.start()

def get_service(domain_data, service_name):
    for line in domain_data:
        data = line.split(' ')
        if service_name in data:
            return data[2]

def request_info(operation, info, server_port):
    target_host = '127.0.0.1'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_host, server_port))
    client.send(operation)
    client.send(info)
    answer = client.recv(1024)
    client.close()
    return(answer)
