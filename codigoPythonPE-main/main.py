
import sys
import os
import recepcion
import cargarDatos


# pantalla principal que inicializa todo
def main():
    numero_intentos = 1
    while(numero_intentos != 0):
        recepcion.recibir_peticion_frontend()
        numero_intentos = numero_intentos - 1

main()