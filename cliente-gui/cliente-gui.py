# -*- coding: utf-8 -*-

import socket
import json
import re
import time

from Tkinter import *
import ttk

TAMANHO_VENTANA = [600,400]
	
class App():

	def __init__(self):
		self.root = Tk()
		self.cadro_texto = Text(self.root,relief="flat",state="disable")
		app_init(self)
		self.conectado = False
		self.server_i = server_info(self)
		self.cadros_texto = cadros_text(self)
		self.time_update()
		self.root.mainloop()
		
	def time_update(self):
	
		#BOTÓN CAMBIAR
		ip_server = self.server_i.entrada_ip.get()
		port_server = self.server_i.entrada_port.get()
		cadena_de_comprobacion_ip = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
		if (re.findall(cadena_de_comprobacion_ip,ip_server) and
				port_server and port_server.isdigit()):
			self.server_i.boton_activado = True
		else:
			self.server_i.boton_activado = False
			
		self.server_i.boton_conectar.configure(state="normal" 
					if self.server_i.boton_activado else "disable")
							
		#TICKS
		self.root.after(500, self.time_update)
	
def app_init(appli):

	#TITULO
	appli.root.title("Cliente de Chat")
	
	#CONFIGURACION DA VENTANA
	appli.root.resizable(width=False, height=False)
	appli.root.minsize(TAMANHO_VENTANA[0],TAMANHO_VENTANA[1])
	
class server_info():

	def __init__(self,appli):

		#CAMPOS PARA A IP E PORTO DO SERVIDOR
		
		self.entrada_ip = ttk.Entry(appli.root, width=15, state="normal")
		self.entrada_port = ttk.Entry(appli.root, width=15, state="normal")
		self.entrada_alias = ttk.Entry(appli.root, width=15, state="normal",
							foreground="blue")
		
		if self.entrada_ip.get():	
			self.boton_activado = True
		else:
			self.boton_activado = False
		
		self.boton_conectar = ttk.Button(appli.root, text="CONECTAR",
							command=lambda: self.conectar(appli),
							state="disable")
		
			#TEXTO
		
		text_ip = ttk.Label(appli.root, text="IP do Servidor:")
		text_port = ttk.Label(appli.root, text="Porto:")
		text_alias = ttk.Label(appli.root, text="Alias:")
		
			#COLOCAR NA VENTANA
			
		text_ip.grid(row=0, column=0, pady=10, padx=5, sticky="we")
		text_port.grid(row=0, column=2, pady=10, padx=5, sticky="we")
		text_alias.grid(row=0, column=4, pady=10, padx=5, sticky="we")
		
		self.entrada_ip.grid(row=0, column=1, pady=10, padx=5, sticky="we")
		self.entrada_port.grid(row=0, column=3, pady=10, padx=5, sticky="we")
		self.entrada_alias.grid(row=0, column=5, pady=10, padx=5, sticky="we")
		
		self.boton_conectar.grid(row=0, column=6, pady=10, padx=5, sticky="we")
		
	def conectar(self,appli):
	
		ip_server = self.entrada_ip.get()
		port_server = self.entrada_port.get()
		alias_conec = self.entrada_alias.get()
		cadena_de_comprobacion_ip = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
		
		if (re.findall(cadena_de_comprobacion_ip,ip_server) and
				self.entrada_port.get() and port_server.isdigit()):
			conexion_co_servidor(appli,ip_server,port_server,alias_conec)
	
class cadros_text():

	def __init__(self,appli):
	
		#CAMPOS DE TEXTO
	
		self.texto_recibos = Text(appli.root,relief="solid",state="disable",bg="#F7F6FA")
		self.texto_envios = Entry(appli.root,relief="solid",state="disable")
		
		self.boton_enviar = ttk.Button(appli.root, text="ENVIAR",
							command=self.enviar,
							state="disable")
		
			#COLOCAR NA VENTANA
			
		espacio_x = 10
		espacio_y = 50
		alto_cadro_escritura = 20
			
		self.texto_recibos.place(x=espacio_x,y=espacio_y,
					width=TAMANHO_VENTANA[0]-espacio_x*2,height=TAMANHO_VENTANA[1]/1.5)
		self.texto_envios.place(x=espacio_x,y=TAMANHO_VENTANA[1]/1.4+espacio_y,
					width=TAMANHO_VENTANA[0]-espacio_x*2,height=alto_cadro_escritura)
					
		self.boton_enviar.place(x=espacio_x,
							y=TAMANHO_VENTANA[1]/1.4+espacio_y+alto_cadro_escritura+5)
							
		appli.root.bind("<Return>",self.enviar)
					
	def enviar(self,Return=False):
		texto = self.texto_envios.get()
		texto = " ".join(texto.split())
		if texto:
			print ">>> "+texto
			self.texto_envios.delete(0,END)
			
def escribir_en(entrada,texto,cont=False):
	estado = entrada.cget("state")
	entrada.config(state="normal")
	#entrada.insert('1.0',texto+"\n")
	entrada.insert(END,texto+("\n" if not cont else ""))
	entrada.yview(END)
	entrada.config(state=estado)
			
###FUNCIÓNS SOCKETS

def conexion_co_servidor(appli,server,port,alias):
	#CONECTAMOS O SOCKET ACTIVO
	try:
		port = int(port)
		
		activo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		activo.connect((server, port))

		#ENVIMOS A ID 0 PARA QUE O SERVIDOR NOS ASIGNE UNHA ID
		#ID, ALIAS, KEY
		msx = [0,alias,0]
		activo.send(json.dumps(msx))
		
		escribir_en(appli.cadros_texto.texto_recibos,
					">>> Conectando...",True)

		#RECIVIMOS A CONTESTACIÓN DO SERVIDOR
		
		try:
			data = activo.recv(256)
			ID,ALIAS,KEY = json.loads(data)
			escribir_en(appli.cadros_texto.texto_recibos,
					"...",True)

			if ID == 0 or ALIAS == "Rechazado":
				activo.close()
				escribir_en(appli.cadros_texto.texto_recibos,
						" ERROR")
			else:
			#EXECUTAMOS O SCRIPT QUE MANEXA O SOCKET PASIVO
			#AQUÍ LANZAMOS PASIVO
				escribir_en(appli.cadros_texto.texto_recibos,
						" Sucess!")
		except:
			escribir_en(appli.cadros_texto.texto_recibos,
						" ERROR")
			
	except:
		escribir_en(appli.cadros_texto.texto_recibos,
					">>> Non se consigueu conectar co servidor")

			
if __name__ == "__main__":
	app = App()