import socket
import sys

domain = open(sys.argv[3], "r")
operation = sys.argv[1]

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
    print client.recv(1024)
    client.send(info)
    print client.recv(1024)
    answer = client.recv(1024)
    client.close()
    return(answer)


if len(sys.argv) != 5:
    print "[*] Por favor digite 4 argumentos.\n"
    print "[*] Formato: python dns_server.py <operacao> <dominio/ip> <arquivo> <porta_servidor_raiz> "
    print "[*] Operacoes suportadas: IP, HN, NS, MX, TC.\n"
    print "[*] Exemplos:\n"
    print " IP www.dominio.com.br 8080\n TC dominio.com.br 7643\n HN 172.124.23.231 12675"
    quit()

server_port = int(sys.argv[4])
if server_port not in range(1025, 65536):
    print "[*] Numero de porta invalido. Por favor escolha uma porta valida(1025 - 65535)."
    quit()

if operation in 'IP HN NS MX TC ip hn ns mx tc':
    domain_data = domain.readlines()
    if operation.lower() == 'ip':
        for line in domain_data:
            data = line.rstrip('\n').split(' ')
            if 'IP' in data and data[0] == sys.argv[2]:
                print "[*] Resposta: %s" % data[2]
                quit()
        print "[*] Informacao indisponivel no servidor local."
        print "[*] Requisitando informacao ao servidor raiz..."
        print "[*] Resposta: %s" % request_info(operation, sys.argv[2], server_port)

    elif operation.lower() == 'hn':
        for line in domain_data:
            data = line.rstrip('\n').split(' ')
            if 'HN' in data and data[0] == sys.argv[2]:
                print "[*] Resposta: %s" % data[2]
                quit()
        print "[*] Informacao indisponivel no servidor local."
        print "[*] Requisitando informacao ao servidor raiz..."
        print "[*] Resposta: %s" % request_info(operation, sys.argv[2], server_port)

    elif operation.lower() == 'ns':
        for line in domain_data:
           data = line.rstrip('\n').split(' ')
           if sys.argv[2] in data:
                print "[*] Resposta: %s" % get_service(domain_data, 'NS')
                quit()
        print "[*] Informacao indisponivel no servidor local."
        print "[*] Requisitando informacao ao servidor raiz..."
        print "[*] Resposta: %s" % request_info(operation, sys.argv[2], server_port)

    elif operation.lower() == 'mx':
        for line in domain_data:
           data = line.rstrip('\n').split(' ')
           if sys.argv[2] in data:
                print "[*] Resposta: %s" % get_service(domain_data, 'MX')
                quit()
        print "[*] Informacao indisponivel no servidor local."
        print "[*] Requisitando informacao ao servidor raiz..."
        print "[*] Resposta: %s" % request_info(operation, sys.argv[2], server_port)


    elif operation.lower() == 'tc':
        for line in domain_data:
            data = line.rstrip('\n').split(' ')
            if sys.argv[2] in data:
                print "[*] Resposta: %s" % get_service(domain_data, 'TC')
                quit()
        print "[*] Informacao indisponivel no servidor local."
        print "[*] Requisitando informacao ao servidor raiz..."
        print "[*] Resposta: %s" % request_info(operation, sys.argv[2], server_port)

else:
    print "[*] Operacao invalida: %s." % sys.argv[1]
