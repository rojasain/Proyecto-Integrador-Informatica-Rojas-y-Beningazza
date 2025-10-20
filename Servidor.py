# ================================================
# PARTE C - SERVIDOR (PC con Arduino)
# Envía datos del archivo registro.csv a otra PC
# ================================================

import socket
import time
import os

# --- CONFIGURACIÓN DEL SERVIDOR ---
HOST = '0.0.0.0'   # Escucha en todas las interfaces. Se puede conectar por localhost o la IP local
PORT = 5000        # Puerto TCP (usar el mismo en el cliente)
ARCHIVO = "registro.csv"

# --- CREAR SOCKET TCP ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #crea el socket, es como el “enchufe” virtual por donde viajarán los datos. 
server_socket.bind((HOST, PORT))    #asocia el socket creado a la IP y el puerto
server_socket.listen(1)             #acepta hasta un cliente pendiente
print(f"Servidor iniciado en {HOST}:{PORT}")
print("Esperando conexión del cliente...")

# --- ESPERAR CONEXIÓN ---
conn, addr = server_socket.accept()     #Acepta la conexión del cliente y devuelve un nuevo socket (conn) para comunicarse con él.
print(f"Cliente conectado desde: {addr}")

# --- CONTROL DEL ARCHIVO ---
ultimo_tamano = 0   #guarda el número de líneas que tenía el archivo la última vez que fue leído.

try:
    while True:
        if os.path.exists(ARCHIVO):                          #Revisa si el archivo especificado por la variable ARCHIVO existe en el sistema.
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                lineas = f.readlines()                       #Abre el archivo en modo lectura y guarda todas las líneas en una lista llamada lineas

            # Si hay nuevas líneas, las enviamos al cliente
            if len(lineas) > ultimo_tamano:
                nuevas = lineas[ultimo_tamano:]
                for linea in nuevas:
                    conn.sendall(linea.encode('utf-8'))
                ultimo_tamano = len(lineas)                   #Se actualiza el número de líneas para no reenviar las mismas en la siguiente iteración

        time.sleep(1)

except KeyboardInterrupt:                        #con Ctrl+C se para el programa y la conexion 
    print("\nServidor detenido manualmente.")
finally:                                         #Cierre de conexiones
    conn.close()
    server_socket.close()
    print("Conexión cerrada.")
