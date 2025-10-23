"""
Cliente simple: se conecta a un servidor TCP que envía líneas CSV
con el formato fecha;hora;temp;tendencia (o con comas) y grafica
en tiempo real las últimas N temperaturas.
"""

import socket
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# --- Configuración del servidor ---
SERVER_IP = '172.20.10.4'  # Cambiar por la IP de la PC servidor
PORT = 5000
MAX_PUNTOS = 20          # Muestras a mostrar en el gráfico


# --- Utilidad de parseo ---
def parsear_linea(linea: str):
    s = linea.strip()           #Quita espacios en blanco iniciales y finales de la cadena
    if not s:                   #Si la linea está vacia retorna none
        return None
    # Detectar separador principal (priorizar ';')
    sep = ';' if ';' in s else ','                  #Si la linea contiene ";" lo usa como separador, sino utiliza coma ","
    partes = [p.strip() for p in s.split(sep)]      #separa la linea por el separador elegido
    if len(partes) < 3:                             #verifica si hay almenos 3 partes 
        return None
    hora = partes[1]                                #Toma el segundo campo (indice 1) y lo asigna como hora
    # Aceptar decimal con coma o punto
    try:
        temp = float(partes[2].replace(',', '.'))   #Convierte el tercer campo (índice 2) a número
    except ValueError:                              #Si la conversión a float falla entra en la excepcion y retorna none
        return None
    return hora, temp                               #si todo sale bien retorna (hora, temperatura)


# --- Conexión TCP (no bloqueante) ---
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #crea unn socket para comunicación por red
sock.connect((SERVER_IP, PORT))                             #Le indica al socket a qué IP y puerto debe conectarse
#Pone el socket en modo no bloqueante para que espere hasta que haya datos y no se pare el programa
sock.setblocking(False)           

buffer_rx = ""                       #Variable tipo string que actúa como buffer acumulador de bytes/strings recibidos
temps = deque(maxlen=MAX_PUNTOS)     #deque es una cola que permite añadir y sacar elementos por ambos extremos
horas = deque(maxlen=MAX_PUNTOS)     #maxlen=MAX_PUNTOS hace que la deque tenga longitud máxima


# --- Gráfico ---
plt.style.use('seaborn-v0_8-darkgrid')                  #Aplica un estilo visual predeterminado al gráfico
fig, ax = plt.subplots()                      #Crea la figura principal (fig) y un eje (ax) donde se dibujará la gráfica
ax.set_title('Temperatura en tiempo real')              #Define el título del gráfico que aparecerá en la parte superior
ax.set_xlabel('Hora')                                   #Asigna el nombre del eje X como "Hora"
ax.set_ylabel('Temperatura (°C)')                       #Asigna el nombre del eje Y como "Temperatura"
linea, = ax.plot([], [], 'r-', label='Temperatura')     #crea una linea vacia que resevirá los datos de hora y Temp.
ax.legend()                                             #muestra una leyenda en el gráfico


def actualizar(_frame):
    global buffer_rx            #declara que el buffer es global y se definió fuera de la funcion
    # 1) Recibir datos y acumular en buffer (sin bloquear)
    try:
        data = sock.recv(4096).decode('utf-8') #intenta recibir 4096 bytes y .decode los convierte en texto
        if data:
            buffer_rx += data       #acumula los fragmentos recibidos
    except BlockingIOError:
        pass                        #si no hay datos nuevo no se frena, pasa

    # 2) Procesar líneas completas
    while '\n' in buffer_rx:                                #Revisa si la linea está completa si hay \n
        linea_csv, buffer_rx = buffer_rx.split('\n', 1)     #separa la linea completa del comienzo de otra
        parsed = parsear_linea(linea_csv)
        if parsed is None:                              #si el parsed retorna none salta al siguiente ciclo del while
            continue
        hora, temp = parsed
        horas.append(hora)
        temps.append(temp)

    # 3) Refrescar gráfico
    n = len(temps)                                         #calcula la cantidad de mediciones de Temperatura almacenadas
    # set_data(x, y) reemplaza los valores antiguos por los nuevos:
    linea.set_data(range(n), list(temps))           #range genera los valores del eje X y list los del eje Y
    ax.set_xlim(0, max(1, n - 1))                   #define el rango visible del eje horizontal
    if n:
        y_min, y_max = min(temps), max(temps)                       #calcula max y min de Temperatura
        margen = (y_max - y_min) * 0.1 if y_max != y_min else 1.0   #agrega 10% de margen extra arriba y abajo
        ax.set_ylim(y_min - margen, y_max + margen)                 #Ej: rango 20 a 30 grados. Eje Y irá de 19 a 31
    ax.set_xticks(range(len(horas)))                                #coloca una marca en el eje X por cada hora registrada.
    ax.set_xticklabels(list(horas), rotation=45, ha='right')
    return linea,


# --- Animación ---
try:
    #Llama a cada segundo la funcion actualizar para refrescar el gráfico
    ani = FuncAnimation(fig, actualizar, interval=1000, cache_frame_data=False) 
    plt.tight_layout()  #ajusta márgenes y espacios del gráfico
    plt.show()  #Muestra la ventana del gráfico
finally:
    sock.close()    #cierra el socket TCP
