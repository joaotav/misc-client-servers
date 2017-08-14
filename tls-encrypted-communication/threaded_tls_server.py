#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Sistemas Distribuídos 2017/1 - Código modificado por João Otávio Chervinski
import os
import sys
import getopt
import socket
import threading
import struct
import ssl

class threaded_server(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))

	def listen(self):
		self.sock.listen(5)
		while True:
			try:
				print ("Waiting for incoming connections...")
				client, address = self.sock.accept()
				client.settimeout(60)
				ssl_sock = ssl.wrap_socket(client,
				server_side=True, certfile="server.crt", keyfile="server.key")
				# Envia os descritores de conexão para as threads com a função ping_pong
				threading.Thread(target = self.ping_pong, args = (ssl_sock,address,)).start()
			except (KeyboardInterrupt, SystemExit):
				print ("[+] Shutdown requested...exiting")
				sys.exit(0)


	def ping_pong(self, ssl_sock, address):
		print ('[+] Got secure connection from', address)
		len_name = ssl_sock.recv(4)
		name_len = struct.unpack('>L', len_name)[0]
		fname = ssl_sock.recv(name_len)
		print('[+] File name = ', repr(fname.decode('UTF-8')))
		# Cada thread abre um arquivo cujo nome contém seu descritor (ex: *Thread-1.srv, *Thread-2.srv)
		with open(fname.decode('UTF-8') + '_' + threading.current_thread().name + '.srv', 'wb') as f:
			print ('[+] File opened')
			#while True:
			print('[+] Receiving data...')
			data = ssl_sock.recv(1024)
			print('[+] Data = %s \n' % (data))
			if not data:
				ssl_sock.shutdown(socket.SHUT_RDWR)
				ssl_sock.close()
				return
			f.write(data)
			ssl_sock.shutdown(socket.SHUT_RDWR)
			ssl_sock.close()

def help():
    print(os.path.basename(sys.argv[0]), '-h -p <Port>')

def main(argv):
    port = 0
    try:
        opts, args = getopt.getopt(argv,"hp:",["Port="])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-p", "--Port"):
            port = arg

    if (port == 0):
        help()
        quit()

    threaded_server('', int(port)).listen()

if __name__ == "__main__":
    main(sys.argv[1:])
