import socket
import argparse
from operator import xor

parser = argparse.ArgumentParser(description='Communicate with the server.')
parser.add_argument('-S', dest='secret')
parser.add_argument('-s', dest='server_ip')
parser.add_argument('-f', dest='filename')
parser.add_argument('-o', dest='operation')
parser.add_argument('-p', type=int, dest='port_number')
args = parser.parse_args()

target_host = args.server_ip
target_port = args.port_number

def encrypt():
    ciphertext = ''
    with open(args.filename, 'r') as arq:
        content = arq.readlines()
        for index in range(len(content)):
            content[index] = content[index].rstrip('\n')
    try:
        for line in content:
            for index in range(len(line)):
                bin_text = format(int(line[index]), '#06b')
                bin_secret = format(int(args.secret[index]), '#06b')
                for item in range(len(bin_text)):
                    if item < 2:
                        ciphertext += bin_text[item]
                    else:
                        ciphertext += str(xor(int(bin_text[item]), int(bin_secret[item])))
    except IndexError:
        print '[*] WARNING: The key and the text must be of the same size.'
        quit()
    return ciphertext

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))

if args.operation.lower() == 'put':
    client.send('put')
    print client.recv(1024)
    client.send(encrypt())
    response = client.recv(1024)

elif args.operation.lower() == 'get':
    plaintext = ''
    client.send('get')
    print client.recv(1024)
    client.send('[*] Client Awaiting response...')
    response = client.recv(1024)
    client.send('[*] Client received message')
    print "[*] Decrypting message..."
    plaintext_bin = ''
    plaintext = ''
    #Divide a mensagem nas representacoes de cada numero em binario
    bin_list = list(map(''.join, zip(*[iter(response)]*6)))
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

else:
    print "[*] Invalid operation: %s. Please choose PUT or GET." % args.operation
    quit()
