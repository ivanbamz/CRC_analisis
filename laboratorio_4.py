from bitarray import bitarray
from numpy.random import Generator, MT19937
import sys


def cyclic_redundancy_check(filename: str, divisor: str, len_crc: int) -> int:
    """
    This function computes the CRC of a plain-text file 
    arguments:
    filename: the file containing the plain-text
    divisor: the generator polynomium
    len_crc: The number of redundant bits (r)
    """
    redundancy = len_crc * bitarray('0')
    bin_file = bitarray()
    p = bitarray(divisor)
    len_p = len(p)
    with open(filename, 'rb') as file:
        bin_file.fromfile(file)
    cw = bin_file + redundancy
    rem = cw[0 : len_p]
    end = len(cw)
    for i in range(len_p, end + 1):
        if rem[0]:
            rem ^= p
        if i < end:
            rem = rem << 1 
            rem[-1] = cw[i]
    #retorna el residuo
    return rem[len_p-len_crc : len_p] #CRC


def codificador(filename: str, divisor: str, len_crc: int):

    """Esta función permite codificar un arreglo de caracteres 
    añadiendo además de añadir el CRC al final del mismo
    filename: el archivo contenedor de texto
    codigo: CRC"""

    crc = cyclic_redundancy_check(filename, divisor, len_crc)

    bin_file = bitarray()
    
    with open(filename, 'rb') as file:
        bin_file.fromfile(file)

    cw = bin_file + crc
    
    return cw


def generador_de_errores(codigo : str, n : int, seed : int): 
    
    """Este módulo se encarga de generar una rafaga de tamaño n
    De los n bits que mide la rafaga, solo 'e' serán invertidos
    Retorna el código de entrada, pero corrompido"""

    aux = Generator(MT19937(seed + 71771)) #modificar la semilla para conseguir resultados diferentes

    e = int(aux.integers(0, n-1))# "e" es el número de errores que cambiaran
    
    codigo[seed] = not codigo[seed]   #Invetir el primer bit de la rafaga
    codigo[seed+n] = not codigo[seed+n]  #Invertir el ultimo bit de la rafaga
    pos_e = []

    """for que determina la posición de 
    cada uno de los 'e' bits que cambiarán"""
    for i in range(0, e):
        pos = int(aux.integers(1, n-1))
        if pos not in pos_e:
            pos_e.append(pos)
    
    """for que modifica los bits de las posiciones pos_e"""
    for i in pos_e:   
        codigo[i+seed] = not codigo [i+ seed]

    return codigo




def descodificador(bin_file : str , divisor: str, len_crc: int):

    """"Esta función permite decodificar un arreglo de caracteres 
    calculando por medio de una división agregando al dividendo el CRC al final
    filename: el archivo contenedor de texto
    divisor : divisor
    len_crc : tamaño del crc
    codigo: CRC
    """
    p = bitarray(divisor)
    len_p = len(p)
    cw = bin_file
    rem = cw[0 : len_p]
    end = len(cw)
    for i in range(len_p, end + 1):
        if rem[0]:
            rem ^= p
        if i < end:
            rem = rem << 1 
            rem[-1] = cw[i]
    #retorna el residuo
    return rem[len_p-len_crc : len_p] #CRC



def validador(filename: str, polinomio: str, len_crc: int, n : int, seed : int):

    """
    Modulo que se encarga de verificar si un código que previamente fue enviado
    de un punto a otro, llegó sin errores.
    Para analizar errores se basa en CRC
    
    filename: archivo a ser codificado/descodificado
    divisor: polinomnio divisor
    len_crc: tamaño deseado del CRC
    n: tamaño de la rafaga
    seed: semilla
    retorna true si el mensaje decodificado está libre de errores
    retorna false si el mensaje decodificado cuenta con errores
    """
    res = False

    codigo_codificado = codificador(filename, polinomio, len_crc)
    
    codigo_corrompido = generador_de_errores(codigo_codificado, n, seed)
    
    codigo_decodificado = descodificador(codigo_corrompido, polinomio, len_crc)

    comparacion = bitarray('0') * (len_crc) #"0000"

    if(codigo_decodificado == comparacion):
        #print("comparacion", comparacion)
        #print("codigo descodificado", codigo_decodificado)
        res = True

    return res



def main():
    contador = 0
    r = 4
    n = int(sys.argv[1])
    print("El valor de r (longitud del crc) es igual a: ", r)
    print("El valor de n (tamaño de la rafaga de error) es igual a: ", n)
    divisor = '11111'
    repeticiones = 1000

    for i in range (0, repeticiones):
        if (validador('HarryPotter.txt', divisor, r, n, i)  == False):
            contador += 1

    print ("\nErrores encontrados\n", contador)
    print("\nProbabilidad de encontrar un error:\n", contador/repeticiones)



if __name__ == '__main__':
    main()