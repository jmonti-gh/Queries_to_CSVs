''' 
## reganalys.py

Depuración o análisis detallado de un solo registro
de una consulta (query) SQL Server

Detalla todos los campos de un registro
Muestra en pantalla el resultado y escribe .txt. y .csv
'''

## Libraries
import pyodbc
import csv
import sys


## Read input data - arguments
if len(sys.argv) < 2:       # Ensure the user provided a record number argument
    print("Usage: python script.py <record_number>")
    sys.exit(1)

try:                        # Check for valid argument
    record_number = int(sys.argv[1])
    if record_number <= 0:
        raise ValueError
except ValueError:
    print("The record number must be a positive integer.")
    sys.exit(1)


## fixed variables - constants
txt_file = f"record_{record_number}.txt"    # Output filenames
csv_file = f"record_{record_number}.csv"

server = '172.31.119.50'                    # Conn parameters
database = 'Bantotal'
username = 'usr_motor'
password = 'MTM.m0t0R2024'

conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

sql_query = "SELECT TOP 9 * FROM fsd010"


## main

with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    cursor.execute(sql_query)

    rows = cursor.fetchall()
    if len(rows) < record_number:
        print(f"There are only {len(rows)} records available.")
        sys.exit(1)

    selected_row = rows[record_number - 1]
    column_info = cursor.description

    # Table headers
    headers = [
        "Field_name", "type_code", "display_size", "internal_size",
        "precision", "scale", "null_ok", "Value"
    ]

    # Prepare data for output
    table_rows = []
    for i, col in enumerate(column_info):
        row_data = [
            col[0],
            str(col[1]),
            col[2],
            col[3],
            col[4],
            col[5],
            col[6],
            selected_row[i]
        ]
        table_rows.append(row_data)

    # Print to console
    print(f"\nFull information for record #{record_number}:\n")
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

    # Save to .csv
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(table_rows)

    print(f"\n✔️ Output exported to '{txt_file}' and '{csv_file}' successfully.")
    input("Press 'Enter' to finish'")
