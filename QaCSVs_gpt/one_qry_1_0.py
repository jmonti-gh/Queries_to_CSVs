"""
reganalys_1_4.py

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
    $ python reganalys_1_4.py

Required libraries:
    - os; ...

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
    - "reganalys_qry.txt"
"""

## Libraries
import pyodbc
import sys
from datetime import datetime
import os
import re



### fixed variables - constants
err_sign = ' > ERROR!:'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')        # Timestamp for filenames
query_file = "reganalys_qry.txt"                            # Query file

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



### Read input data - arguments
if len(sys.argv) < 3:       # Show usage + structure of cursor.description + value and exit
    # Usage message display
    prg_name = os.path.basename(sys.argv[0])
    print(f"Uso: {prg_name} <nomnbre del .csv -SIN espacios -SIN extensión .csv> <número de registro>")

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
    title = " * Esctructura del campo + valor del dato del campo:"
    print(f"\n{title}\n")
    print(f"{mini_headers[0]:<8} {mini_headers[1]:<20} {mini_headers[2]}")
    print("--" * 56)
    for row in table_data:
        print(f"{str(row[0]):<8} {row[1]:<20} {row[2]}")

    # Save to .txt
    txt_desc = f"estructura_campo.txt"
    with open(txt_desc, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n")
        f.write(f"{mini_headers[0]:<8} {mini_headers[1]:<20} {mini_headers[2]}\n")
        f.write("--" * 56 + "\n")
        for row in table_data:
            f.write(f"{str(row[0]):<8} {row[1]:<20} {row[2]}\n")

    print(f"\n✔️  Structure saved to '{txt_desc}'")
    input('\n --> Press ENTER to close...')
    sys.exit(0)

else:                       # Read .csv filename + record_number + SQL Srv query
    try:
        csv_file = sys.argv[1]
        if not is_valid_win_filename(csv_file):
            raise ValueError
    except ValueError:
        print(f"{err_sign} '{csv_file}' no es un nombre de archivo válido en Windows")
        sys.exit(1)

    try:
        record_number = int(sys.argv[2])
        if record_number <= 0:
            raise ValueError
    except ValueError:
        print(f"{err_sign} ❌ The record number must be a positive integer.")
        sys.exit(1)

    if not os.path.exists(query_file):                          # Load query from file
        print(f"{err_sign} ❌ Query file '{query_file}' not found.")
        sys.exit(1)

    with open(query_file, 'r', encoding='utf-8') as f:
        sql_query = f.read().strip()
    
    if not sql_query:
        print(f"{err_sign} ❌ The query in '{query_file}' is empty.")
        sys.exit(1)


## Additional constants - Output filename(s)
txt_file = f"{csv_file}_{record_number}_{timestamp}.txt"
csv_fname = f"{csv_file}.csv"

## Main process
with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()          # Make DB connection
    cursor.execute(sql_query)       # Execute the query

    rows = cursor.fetchall()        # Read all registers of the query's output
    if not cursor.description:
        print("❌ Query returned no columns.")
        sys.exit(1)

    if len(rows) < record_number:
        print(f"❌ Only {len(rows)} records found. Record #{record_number} is out of range.")
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

    # Console output
    print(f"\n📄 Full information for record #{record_number}:\n")
    print(f"{headers[0]:<20} {headers[1]:<30} {headers[2]:<13} {headers[3]:<14} "
          f"{headers[4]:<10} {headers[5]:<7} {headers[6]:<8} {headers[7]}")
    print("-" * 130)
    for row in table_rows:
        print(f"{str(row[0]):<20} {str(row[1]):<30} {str(row[2]):<13} {str(row[3]):<14} "
              f"{str(row[4]):<10} {str(row[5]):<7} {str(row[6]):<8} {row[7]}")

    # Save to .txt
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"Full information for record #{record_number}:\n\n")
        f.write(f"{headers[0]:<20} {headers[1]:<30} {headers[2]:<13} {headers[3]:<14} "
                f"{headers[4]:<10} {headers[5]:<7} {headers[6]:<8} {headers[7]}\n")
        f.write("-" * 130 + "\n")
        for row in table_rows:
            f.write(f"{str(row[0]):<20} {str(row[1]):<30} {str(row[2]):<13} {str(row[3]):<14} "
                    f"{str(row[4]):<10} {str(row[5]):<7} {str(row[6]):<8} {row[7]}\n")

    print(f"\n✅ Output saved to:   - {txt_file}")
    input("\nPress 'Enter' to finish.")

