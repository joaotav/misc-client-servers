import socket
import threading
import argparse
from random import randint
from operator import xor

parser = argparse.ArgumentParser(description='Run the server.')
parser.add_argument('-S', dest='secret')
parser.add_argument('-p', type=int, dest='server_port')
args = parser.parse_args()

bind_ip = "127.0.0.1"
bind_port = args.server_port

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)

print "[*] Listening on %s:%d" % (bind_ip,bind_port)

def handle_client(client_socket):
    operation = client_socket.recv(1024)
    client_socket.send('[*] Server: Request received.')
    gen_message = ''
    if operation == "put":
        message = client_socket.recv(1024)
        print "[*] Received: %s" % message
        client_socket.send("Message received, disconnecting.")
        client_socket.close()
        print "[*] Decrypting message..."
        plaintext_bin = ''
        plaintext = ''
        #Divide a mensagem nas representacoes de cada numero em binario
        bin_list = list(map(''.join, zip(*[iter(message)]*6)))
        for index in range(len(bin_list)):
            bin_secret = format(int(args.secret[index]), '#06b')
            for item in range(len(bin_list[index])):
                if item < 2:
                    plaintext_bin += bin_list[index][item]
                else:
                    plaintext_bin += str(xor(int(bin_list[index][item]), int(bin_secret[item])))
        plain_bin_list = list(map(''.join, zip(*[iter(plaintext_bin)]*6)))
        for item in range(len(plain_bin_list)):
            plaintext += str(int(plain_bin_list[item], 2))
        print "[*] Message: %s" % plaintext
        print "[*] Done"

    if operation == "get":
        print client_socket.recv(1024)
        ciphertext = ''
        for _ in range(len(args.secret)):
            num = randint(0,9)
            gen_message += str(num)
        for index in range(len(gen_message)):
            bin_text = format(int(gen_message[index]), '#06b')
            bin_secret = format(int(args.secret[index]), '#06b')
            for item in range(len(bin_text)):
                if item < 2:
                    ciphertext += bin_text[item]
                else:
                    ciphertext += str(xor(int(bin_text[item]), int(bin_secret[item])))
        client_socket.send(ciphertext)
        print client_socket.recv(1024)

while True:
    client,addr = server.accept()
    print "[*] Accepted connection from: %s:%d" % (addr[0],addr[1])
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()
