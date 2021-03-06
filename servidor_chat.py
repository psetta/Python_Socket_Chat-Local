# -*- coding: utf-8 -*-

#SERVIDOR DE CHAT LOCAL

import socket
import json
import sys
import random
from threading import *



#VARIABLES SERVIDOR
print(u"*** Servidor Chat - Local ***")

HOST = "0.0.0.0"
try:
	PORT = int(raw_input(u"Porto: "))
except:
	print(u"ERROR - Número incorrecto ou demasiado grande")
	sys.exit(0)

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))

print(HOST,PORT)

#PROCESAMENTO DOS DATOS RECIVIDOS UNHA VEZ QUE A CONEXIÓN XA ESTÁ ESTABLECIDA

class Procesando_Conexion(Thread):
	def __init__(self, id, socket, address):
		Thread.__init__(self)
		self.id = id
		self.sock = socket
		self.addr = address
	def run(self):
		while True:
			try:
				data = self.sock.recv(512)
			except:
				mensaxe_desc = u">>> Desconexión de "+str([self.id,clientes[self.id]["alias"]])+" "+str(self.addr)
				print(mensaxe_desc)
				try:
					del clientes[id]
				except:
					pass
				sys.exit(0)
			if data:
				try:
					#CADA MENSAXE DO CLIENTE TEN: ID, KEY e TEXTO
					id, key, text = json.loads(data)
					#COMPROBAMOS A KEY
					if id in clientes and clientes[id]["key"] == key:
						#ENVIANDO INFORMACIÓN DA MENSAXE A TODOS OS CLIENTES
						#ID, IP, E TEXTO
						alias = clientes[id]["alias"]
						msx = json.dumps([id,self.addr[0],alias,text])
						for client in clientes.values():
							client["pasivo"].sendall(msx)
				except:
					pass
			else:
				break
		mensaxe_con_cerrada = u"Conexión cerrada: "+str(self.id)+" "+str(self.addr)
		print(mensaxe_con_cerrada)
		del clientes[self.id]

def servidor_init():
	#NOVOS CLIENTES - CONEXIÓNS
	global clientes
	global conexions_procesandose
	clientes = {}
	conexions_procesandose = []
	id = 1
	#SERVIDOR ESCOITANDO
	print(u"Servidor escoitando por novos clientes...")
	serversocket.listen(1)
	while True:
		try:
			sock, addr = serversocket.accept()
		except:
			serversocket.close()
			
		print(u">>> Petición de: "+addr[0])
		
		try:
			data = sock.recv(1024)
			data = json.loads(data)
		except:
			data = [None,None,None]
		
		id_cliente, alias, key = data
		
		print u"\tRecibido\t-ID: "+str(id_cliente),"-Alias: "+str(alias),"-Key: "+str(key)
		
		#COMPROBAMOS O ID DO CLIENTE E SE XA HAI UN CLIENTE COA MESMA IP
		if ((id_cliente == 0) and (not addr[0] in [client["ip"] for client in clientes.values()])
			and (len(clientes) < 10)):
			#COMPROBAMOS SE O ALIAS XA EXISTE OU SE NON HAI
			lista_alias = [client["alias"] for client in clientes.values()]
			if not alias.replace(" ",""):
				alias = "Anonymous"
			if len(alias) > 20:
				alias = alias[0:15]
			if alias in lista_alias:
				#EN CASO DE ALIAS REPETIDO, MODIFICAMOLO
				alias_engadido = 2
				while alias+"_"+str(alias_engadido) in lista_alias:
					alias_engadido += 1
				alias = alias+"_"+str(alias_engadido)
			#GARDAMOS O SOCK ACTIVO DO CLIENTE
			key = random.randint(1,100000)
			clientes[id] = {"ip":addr[0],"activo":sock,"pasivo":None,"alias":alias,"key":key}
			#ENVIAMOS AO CLIENTE O SEU ID E ALIAS
			msx = json.dumps([id,alias,key])
			sock.send(msx)
			print u"\tDevolución\t-ID: "+str(id),"-Alias: "+str(alias), "-Key: "+str(key)
	
		elif ((id in clientes) and (alias == u"Pasivo") and (str(key) == str(clientes[id]["key"]))
				and not (clientes[id]["pasivo"])):
			#GARDAMOS O SOCK PASIVO DO CLIENTE
			clientes[id]["pasivo"] = sock
			#PROCESAMOS A CONEXIÓN DO CLIENTE
			conexions_procesandose.append(
						Procesando_Conexion(id,clientes[id]["activo"],addr)
						)
			print u"\tCorrecto\tCliente Engadido"
			for id in clientes:
				print("id: "+str(id),"ip: "+clientes[id]["ip"],"alias: "+clientes[id]["alias"])
			conexions_procesandose[-1].start()
			#AUMENTAMOS O ID
			id += 1
			
		else:
			msx = "Rechazado\n"
			try:
				sock.send(msx)
				clientes[id].activo = None
			except:
				pass
			print u"\tERROR --\t",addr
		
servidor_init()


