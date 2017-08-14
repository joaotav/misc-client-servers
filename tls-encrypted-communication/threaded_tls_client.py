#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Sistemas Distribuídos 2017/1 - Código modificado por João Otávio Chervinski
import socket
import traceback
import struct
import os, sys, getopt
from random import (
    choice, randint
)
from string import (
    ascii_uppercase, ascii_letters, digits
)
import threading
import logging
import ssl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

# Função que manipula as threads
def request_handler(IP, Port, Filename):
    # Cria um descritor de socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock, ca_certs="server.crt",
    cert_reqs=ssl.CERT_REQUIRED)

    try:
        ssl_sock.connect((IP, int(Port)))

        # Envia para o servidor o tamanho do nome do arquivo a ser esperado
        name_len = struct.pack('>L', len(Filename))
        ssl_sock.sendall(name_len)
        ssl_sock.sendall(bytes(Filename,'UTF-8'))
        f = open(Filename,'rb')
        l = f.read(1024)

        while (l):
            ssl_sock.sendall(l)
            l = f.read(1024)

        print ("[+]" + threading.current_thread().name + " -- Data has been sent")
        f.close()

    except:
        traceback.print_exc()
    ssl_sock.close()

# Exibe a ajuda do parser
def help():
    print(os.path.basename(sys.argv[0]), '-h -i <IP> -p <Port> -t <Threads> -f <Filename>')

def main(argv):
    IP = ''
    Port = 0
    Threads = 0
    Filename = ''
    try:
        opts, args = getopt.getopt(argv,"hi:p:t:f:",["IP=", "Port=", "Threads=", "Filename="])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    # Trata os argumentos da linha de comando
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-i", "--IP"):
            IP = arg
        elif opt in ("-p", "--Port"):
            Port = arg
        elif opt in ("-t", "--Threads"):
            Threads = arg
        elif opt in ("-f", "--Filename"):
            Filename = arg
    if ((IP == '') or (Port == 0) or (Threads == 0) or (Filename == '')):
        help()
        quit()

    ''' Cria uma lista 'threads'. Cada thread existente manipula uma instância da função
    request_handler e é adicionada na lista de threads'''
    threads = []
    for i in range(int(Threads)):
        thread = threading.Thread(target=request_handler, args = (IP, Port, Filename ))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main(sys.argv[1:])
