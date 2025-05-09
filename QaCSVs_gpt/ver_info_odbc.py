# 9/5/25 - 17hs
# SEGUIR CON ESTO EN CASA
# Acá en office voy a seguir con el qacsv (los ditisntos queries)  probando con el one_qry..
# por otro lado AHORA .. hacer la copia de todo lo que hay en om93

'''
ver_info_odbc.py

Presenta (en tabla1):
    1.- Datos del equipo (nombre_pc, so -x_bits, user, fecha hora)
    2.- Presenta datos detallados odbc driver s(version, company, fecha, x_bits)
Presenta (en tabla2):
    3.- Dataos detallados otros drivers odbc-type

Escribe todo esto a un archivo + la data de script powershell

'''

### Libraries
import os
from datetime import datetime
import platform

import pyodbc


### Constants




### Functions

def get_env_data():
    '''
    Obtiene datos del entorno
    '''
    now = datetime.now()

    env_data = {
        'date_time': now.strftime("%Y-%m-%d %H:%M:%S"),
        'timestamp': now.strftime("%Y%m%d%H%M%S"),
        'pc_name': platform.node(),
        'user': os.environ['USERNAME'],
        'OS': platform.system(),
        'OS_RELEASE': platform.release(),
        'OS_VERSION': platform.version(),
        'ARCHITECTURE': platform.architecture()[0],
        'SYSTEM_ALIAS': platform.system_alias(platform.system(), platform.release(), platform.version()),
        'UNAME': platform.uname(),
        'NODE': platform.node(),
        'PLATFORM': platform.platform(),
        'PROCESSOR': platform.processor(),
        'MACHINE': platform.machine(),
        'WIN32_VER': platform.win32_ver()
    }
    return env_data 


### main
os.system('cls' if os.name == 'nt' else 'clear')

print()

print(f"Nombre del equipo: {os.environ['COMPUTERNAME']}")
print(f"Nombre del usuario: {os.environ['USERNAME']}")
print(f"SO: {platform.system()} - {platform.release()} - {platform.version()}")
print(f"{platform.architecture()[0] = } bits")
print(f"{platform.system_alias(platform.system(), platform.release(), platform.version()) = }")
print(f"{platform.uname() = }")
print(f"{platform.node() = }")
print(f"{platform.platform() = }") 
print(f"{platform.processor() = }")
print(f"{platform.machine() = }")   
print(f"{platform.platform() = }")
print(f"{platform.win32_ver() = }")

print(f"{platform.win32_ver()[0] = }")
print(f"{platform.win32_ver()[1] = }")
print(f"{platform.win32_ver()[2] = }")
print(f"{platform.win32_ver()[3] = }")

print()

