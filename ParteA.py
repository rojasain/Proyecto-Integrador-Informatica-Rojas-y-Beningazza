# ESTACIÓN DE MONITOREO DE TEMPERATURA
# Parte A - Trabajo Final
# Código Python para Arduino (via pyFirmata)

import pyfirmata               # Para comunicar Python con Arduino usando protocolo Firmata
import time                    # Para medir tiempos y pausas
from datetime import datetime  # Para registrar fecha y hora exacta de cada lectura
import os                      # Para verificar si existe o no el archivo de registro
import csv                     # Para escribir registros en formato CSV


# 1. CONFIGURACIÓN DE HARDWARE

PORT = 'COM4'  # Ajustar según la PC
board = pyfirmata.Arduino(PORT)

TEMP_PIN = 0        # Pin analógico A0 -> Sensor LM35
LED_ROJO = 2        # Pin digital 2 -> LED rojo (tendencia alta)
LED_AMARILLO = 3    # Pin digital 3 -> LED amarillo (tendencia estable)
LED_AZUL = 4        # Pin digital 4 -> LED azul (tendencia baja)
BUTTON_PIN = 5      # Pin digital 5 -> Pulsador (configurar ciclo / finalizar)


# 2. PARÁMETROS DEL SISTEMA

CICLO_DEFECTO = 3.5   # Ciclo de medición inicial en segundos
N = 5                 # Número de lecturas para calcular promedio
X_PORCENTAJE = 5      # % de variación para decidir tendencia


# 3. INICIAR FIRMATA

it = pyfirmata.util.Iterator(board)  #El iterador es un hilo de Python que se encarga de leer continuamente los valores del Arduino
it.start()
board.analog[TEMP_PIN].enable_reporting()        #Habilita la lectura de un pin analógico
board.digital[BUTTON_PIN].mode = pyfirmata.INPUT #Define el pin digital como entrada 
board.digital[BUTTON_PIN].enable_reporting()     #Habilita la lectura de un pin digital

# 4. DEFINIR LISTA DE LECTURAS VACÍA

lecturas = [] 

# FUNCIONES DEL SISTEMA

# Leer temperatura LM35
def leer_temperatura():
    lecturas_temp = []  # Lista temporal para almacenar varias lecturas
    intentos = 10       # Número de intentos por ciclo

    for i in range(intentos):
        valor = board.analog[TEMP_PIN].read()  # Lee valor analógico
        if valor is not None:                  # Solo considera valores válidos
            lecturas_temp.append(valor)
        time.sleep(0.01)                       # Pequeña espera de 10 ms entre lecturas

    if lecturas_temp:                          # Si hay al menos una lectura válida
        promedio = sum(lecturas_temp) / len(lecturas_temp)
        # LM35: 10 mV por °C, Arduino analogico 0-5V -> 0-1023, con pyFirmata 0-1
        temperatura = promedio * 5.0 * 100
        return temperatura
    else:
        # No se pudo obtener lectura válida, retornamos None
        return None

# Calcular promedio de las últimas N lecturas
def calcular_promedio(lista):
    if len(lista) < N:                    # Si hay menos de N lecturas
        return None                       # No hay suficientes datos, devuelve None
    else: promedio = sum(lista[len(lista)-N : len(lista)]) / N  # Toma solo las últimas N lecturas y calcula el promedio
    return promedio                       # Devuelve el promedio

# Analizar tendencia y decidir LEDs
def analizar_tendencia(lectura, promedio):
    if promedio is None:                                        # Si no hay suficientes datos
        return "sin datos" 
    variacion = promedio * X_PORCENTAJE / 100                   # Rango de variación permitido         
    if lectura > promedio + variacion:                          # Si la lectura es mayor que el promedio + variación
        return "alta"                                           # Tendencia alta 
    elif lectura < promedio - variacion:                        # Si la lectura es menor que el promedio - variación
        return "baja"                                           # Tendencia baja 
    else:                                                       # Si la lectura está dentro del rango de variación
        return "estable"                                        # Tendencia estable 

# Registrar evento en archivo
def registrar_evento(temperatura, tendencia):
    # 5. CREAR O ABRIR EL ARCHIVO CSV (y mantener registro.txt para compatibilidad)
    ahora = datetime.now()                                 # Obtiene fecha y hora actual
    fecha_str = ahora.strftime("%d/%m/%Y")   # Día/Mes/Año
    hora_str  = ahora.strftime("%H:%M:%S")   # Hora:Minuto:Segundo

    # Escribimos en el archivo CSV para la parte C
    with open("registro.csv", "a", newline='', encoding="utf-8") as archivo_csv:
     writer = csv.writer(archivo_csv)
     writer.writerow([fecha_str, hora_str, f"{temperatura:.2f}", tendencia])

    # Escribimos en el archivo TXT para lectura y parte B
    with open("registro.txt", "a") as archivo_txt:
        archivo_txt.write(f"Fecha: {fecha_str}; Hora: {hora_str}; Temperatura: {temperatura:.2f}; Tendencia: {tendencia}\n")

# Encender LEDs segun tendencia
def encender_leds(tendencia):
    if tendencia == "sin datos":               # Si no hay suficientes datos,Todos los LEDs encendidos
        board.digital[LED_ROJO].write(1)
        board.digital[LED_AMARILLO].write(1)
        board.digital[LED_AZUL].write(1)
    elif tendencia == "alta":                  # Tendencia alta, solo LED rojo encendido
        board.digital[LED_ROJO].write(1)
        board.digital[LED_AMARILLO].write(0)
        board.digital[LED_AZUL].write(0)
    elif tendencia == "estable":               # Tendencia estable, solo LED amarillo encendido
        board.digital[LED_ROJO].write(0)
        board.digital[LED_AMARILLO].write(1)
        board.digital[LED_AZUL].write(0)
    elif tendencia == "baja":                  # Tendencia baja, solo LED azul encendido
        board.digital[LED_ROJO].write(0)
        board.digital[LED_AMARILLO].write(0)
        board.digital[LED_AZUL].write(1)

# Destellar todos los LEDs durante 50 ms
def destellar_leds():
    board.digital[LED_ROJO].write(1)
    board.digital[LED_AMARILLO].write(1)
    board.digital[LED_AZUL].write(1)
    time.sleep(0.05)
    board.digital[LED_ROJO].write(0)
    board.digital[LED_AMARILLO].write(0)
    board.digital[LED_AZUL].write(0)

# Apagar todos los LEDs
def apagar_leds():
    board.digital[LED_ROJO].write(0)
    board.digital[LED_AMARILLO].write(0)
    board.digital[LED_AZUL].write(0)

# Mostrar por consola
def mostrar_por_consola(temp, promedio, tendencia):
    if promedio is None: promedio_texto = "N/A"
    else: promedio_texto = f"{promedio:.2f}"
    print(f"Temp: {temp:.2f}°C | Promedio: {promedio_texto}°C | Tendencia: {tendencia}")

# Ajustar ciclo y monitoreo segun duración del pulsador
def medir_duracion_pulsacion():

    # Inicializamos variables
    t_inicio = time.time()
    t_destello = t_inicio

    # Mientras el botón esté presionado, destellamos cada 1 segundo
    while board.digital[BUTTON_PIN].read() == 1:
        ahora = time.time()
        if ahora - t_destello >= 1:
            destellar_leds()
            t_destello = ahora
        time.sleep(0.01)

    # Al soltarse el botón, calculamos la duración
    t_final = time.time()
    duracion = t_final - t_inicio

    if duracion < 1:          # Si la duración es menor a 1 finalizar monitoreo
        print("Finalizando monitoreo...")
        return None
    elif duracion < 2.5:      # Si la duración es menor a 2.5s, ciclo mínimo 2.5s
        nuevo_ciclo = 2.5
    elif duracion < 10:       # Si la duración es menor a 10s, ciclo = duración
        nuevo_ciclo = duracion
    else:                     # Si la duración es mayor a 10s, ciclo máximo 10s
        nuevo_ciclo = 10

    print(f"Ciclo ajustado a {nuevo_ciclo:.2f} segundos")
    return nuevo_ciclo


# Esperar ciclo
# verifica periódicamente si el botón fue presionado
def esperar_ciclo(ciclo):
    intervalo=0.05        # Intervalo de verificación en segundos
    t_start = time.time() # Tiempo de inicio
    while (time.time() - t_start) < ciclo: # Mientras no se cumpla el ciclo
        estado = board.digital[BUTTON_PIN].read() # Lee el estado del botón
        if estado == 1:                           # Si el botón está presionado
            nuevo_ciclo = medir_duracion_pulsacion()
            if nuevo_ciclo is None:               # Si se indicó finalizar monitoreo
                return False, ciclo
            return True, nuevo_ciclo              # Si se indicó un nuevo ciclo
        time.sleep(intervalo)                     # Espera el intervalo
    return True, ciclo                 # Retorna que el monitoreo sigue activo y el ciclo actual

# BUCLE PRINCIPAL

ciclo = CICLO_DEFECTO
print("Estación de monitoreo iniciada. Presiona el botón para configurar ciclo o finalizar.")
monitoreo_activo = True

while True:
   # 7. Leer el estado del pulsador
   pulsador = board.digital[BUTTON_PIN].read()  
   
   if monitoreo_activo==True:     # monitoreo activo:
    
    # 8. Si el pulsador está presionado:
    if pulsador == 1:
        nuevo_ciclo = medir_duracion_pulsacion() # Medir duración de pulsación
        if nuevo_ciclo is None:           # Si se indicó finalizar monitoreo
            monitoreo_activo = False
            continue
        else:                             # Si se indicó un nuevo ciclo
            ciclo = nuevo_ciclo

    # 9. Leer temperatura
    temperatura = leer_temperatura()
    if temperatura is None:
        print("Esperando señal del sensor...")
        time.sleep(0.5)
        continue

    # 10. Actualizar lista de lecturas
    lecturas.append(temperatura)

    # 11. Calcular promedio si hay suficientes lecturas
    promedio = calcular_promedio(lecturas)

    # 12 Analizar tendencia 
    tendencia = analizar_tendencia(temperatura, promedio)
    encender_leds(tendencia)

    # 13. Mostrar por consola
    mostrar_por_consola(temperatura, promedio, tendencia)

    # 14. Registrar evento en archivo
    registrar_evento(temperatura, tendencia)

    # 15. Destellar LEDs fin de ciclo
    destellar_leds()

    # 16. Encender LEDs según tendencia
    encender_leds(tendencia)

    # 17. Esperar hasta siguiente ciclo 
    monitoreo_activo, ciclo = esperar_ciclo(ciclo)


   if monitoreo_activo == False:                          # monitoreo detenido
        apagar_leds()
        if pulsador == 1:                                 # Si el pulsador está presionado
            while board.digital[BUTTON_PIN].read() == 1:  # Esperar a que el botón se suelte
                time.sleep(0.01)
            monitoreo_activo = True                       # Reactiva el monitoreo
            lecturas = []                                 # reinicia lecturas
            print("Reiniciando monitoreo desde 0...")
        time.sleep(0.01)
        continue
   

