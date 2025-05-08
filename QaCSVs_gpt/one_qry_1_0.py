"""
one_qry_1_0.py

Ejecuta el query y lo guarda en un .csv; y + todo lo de reganalys.py:
    Depuración o análisis detallado de un solo registro de una consulta (query) SQL Server.
    Detalla las características (metadata) de todos los campos de un registro.
    Muestra en pantalla el resultado y escribe un .txt con la misma info

Author:
    Jorge Monti

Date:
    2025-05-07

Version:
    1.4

Use:
    $ python one_qry_1_0.py

Required libraries:
    - pyodbc, sys, ...

Arguments:
    - 
    
Query file:
    - 
Query file:
    - sys.argv[0]: program name
    - sys.argv[1]: csv filename
    - sys.argv[2]: register number

Script do:
    - The **record number** is taken from the **first command-line argument**.
    - El **query SQL** se lee desde un archivo llamado `reganalys.qry` (en el mismo directorio)
    - ❌ Si no hay argumentos: muestra la tabla descriptiva de `cursor.description` y la guarda como `.txt`
    - It will print the selected record's metadata and values in a formatted table.
    - It will export the output to a `.txt` file

Query file:
    - "oneq_qry.txt"
"""

## Libraries
import pyodbc
import sys
from datetime import datetime
import os
import re
import csv



### fixed variables - constants
err_sign = ' > ERROR!:'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')        # Timestamp for filenames
query_file = "oneq_qry.txt"                                 # Query file

server = '172.31.119.50'                                    # Connection parameters
database = 'Bantotal'
username = 'usr_motor'
password = 'MTM.m0t0R2024'
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

# Headers of the output table info and for the metadata description
headers = [
        "Field_name", "type_code", "display_size", "internal_size",
        "precision", "scale", "null_ok", "Value"
    ]



### Functions

def usage_msg(prg):
    prg_name = os.path.basename(prg)
    result = f"\nUso: {prg_name} <nomnbre del archivo CSV> <número de registro>"
    result += f"\n   - <nombre del archivo CSV>: SIN espacios y SIN extensión .csv"
    result += f"\n   - <número del registro>: resgistro que se va a anilizar en detalle (entero > 1)"
    return result


def is_valid_win_filename(nombre):
    # Lista de nombres reservados en Windows (sin extensión)
    nombres_reservados = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10))
    }

    # Validar caracteres inválidos
    if re.search(r'[<>:"/\\|?*\s]$', nombre):  # termina en espacio o tiene caracteres no válidos
        return False
    if any(c in r'<>:"/\|?*' for c in nombre):
        return False
    if nombre.upper() in nombres_reservados:
        return False
    if nombre.endswith('.') or nombre.endswith(' '):
        return False
    return True


def close_prg():
    input("\n* Presione 'Enter' para cerrar.")
    sys.exit(0)



### Read input data - arguments
if len(sys.argv) < 3:       # Show usage + structure of cursor.description + value and exit
    # Usage message display
    print(usage_msg(sys.argv[0]))

    ## Field Structure (+ Value) display and save
    mini_headers = ["Index", "Element", "Meaning"]
    table_data = [
        [0, headers[0], "Nombre de la columna (string)"],
        [1, headers[1], "Tipo de dato (depende del driver, ej. int, str, etc.)"],
        [2, headers[2], "Tamaño máximo que puede ocupar al mostrar (normalmente `None` en pyodbc)"],
        [3, headers[3], "Tamaño interno en bytes (por ejemplo, 4 para un `INT`, 8 para un `FLOAT`)"],
        [4, headers[4], "Precisión para números decimales (número total de dígitos)"],
        [5, headers[5], "Escala decimal (número de dígitos a la derecha del punto decimal)"],
        [6, headers[6], "Booleano que indica si la columna acepta `NULL`"],
        [7, headers[7], "Valor (data) del campo para el registro  seleccionado"],
    ]

    # Console Ouput
    struct_title = " * Esctructura del campo + valor del dato del campo:"
    print(f"\n{struct_title}\n")
    print(f"{mini_headers[0]:<8} {mini_headers[1]:<20} {mini_headers[2]}")
    print("--" * 56)
    for row in table_data:
        print(f"{str(row[0]):<8} {row[1]:<20} {row[2]}")

    # Save to .txt
    txt_desc = f"estructura_campo.txt"
    with open(txt_desc, 'w', encoding='utf-8') as f:
        f.write(f"{struct_title}\n\n")
        f.write(f"{mini_headers[0]:<8} {mini_headers[1]:<20} {mini_headers[2]}\n")
        f.write("--" * 56 + "\n")
        for row in table_data:
            f.write(f"{str(row[0]):<8} {row[1]:<20} {row[2]}\n")

    print(f"\n✔️  Estructura guardada en: '{txt_desc}'")
    close_prg()

else:                               # Read .csv filename + record_number + SQL Srv query
    try:
        csv_file = sys.argv[1]                      # read csv filenme wo/extension
        if not is_valid_win_filename(csv_file):
            raise ValueError
    except ValueError:
        print(f"{err_sign} '{csv_file}' no es un nombre de archivo válido en Windows")
        sys.exit(1)

    try:
        record_number = int(sys.argv[2])            # read register number
        if record_number <= 0:
            raise ValueError
    except ValueError:
        print(f"{err_sign} ❌ The record number must be a positive integer.")
        sys.exit(1)

    if not os.path.exists(query_file):              # Load query from query_file
        print(f"{err_sign} ❌ Query file '{query_file}' not found.")
        sys.exit(1)

    with open(query_file, 'r', encoding='utf-8') as f:
        sql_query = f.read().strip()
    
    if not sql_query:
        print(f"{err_sign} ❌ The query in '{query_file}' is empty.")
        sys.exit(1)


### Additional constants - Output filename(s)
txt_file = f"{csv_file}_{record_number}_{timestamp}.txt"
csv_filename = f"{csv_file}.csv"



### main. Two process: register_analysis and query_to_csv

## DB inspection (conn + qry), needed for both processes
with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()          # Make DB connection
    cursor.execute(sql_query)       # Execute the query

## Register analysis
    rows = cursor.fetchall()        # Read all registers of the query's output
    if not cursor.description:
        print(f"{err_sign} ❌ Query returned no columns.")
        sys.exit(1)

    if len(rows) < record_number:
        print(f"{err_sign} ❌ Only {len(rows)} records found. Record #{record_number} is out of range.")
        sys.exit(1)

    selected_row = rows[record_number - 1]      # 0 register indexing
    column_info = cursor.description            # Fields metadata

    table_rows = []
    for i, col in enumerate(column_info):
        row_data = [
            col[0],             # Field_name
            str(col[1]),
            col[2],
            col[3],
            col[4],
            col[5],             # Scale
            col[6],
            selected_row[i]     # Value [dato del campo (col) del registro (fila) seleccionada]
        ]
        table_rows.append(row_data)     # Append new line of output info

    title = f"* Información detallada del registro #{record_number}:"
    # Console output
    print(f"\n{title}\n")
    print(f"{headers[0]:<20} {headers[1]:<30} {headers[2]:<13} {headers[3]:<14} "
          f"{headers[4]:<10} {headers[5]:<7} {headers[6]:<8} {headers[7]}")
    print("-" * 130)
    for row in table_rows:
        print(f"{str(row[0]):<20} {str(row[1]):<30} {str(row[2]):<13} {str(row[3]):<14} "
              f"{str(row[4]):<10} {str(row[5]):<7} {str(row[6]):<8} {row[7]}")

    # Save to .txt
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n")
        f.write(f"{headers[0]:<20} {headers[1]:<30} {headers[2]:<13} {headers[3]:<14} "
                f"{headers[4]:<10} {headers[5]:<7} {headers[6]:<8} {headers[7]}\n")
        f.write("-" * 130 + "\n")
        for row in table_rows:
            f.write(f"{str(row[0]):<20} {str(row[1]):<30} {str(row[2]):<13} {str(row[3]):<14} "
                    f"{str(row[4]):<10} {str(row[5]):<7} {str(row[6]):<8} {row[7]}\n")
            
    ## Query to .csv
    # Get columns names
    columns = [column[0] for column in column_info]

    # Write .csv with ';' separator and utg-9 w/BOM codification
    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(columns)                # Write result columns headers
        for row in rows:
            writer.writerow(row)



    ### Output info and End.
    print(f"\n* Archivos de salida:")
    print(f"  - {txt_file:<56} <- Análisis de un registro\n  - {csv_filename:<56} <- Query como .csv\n")

    close_prg()


