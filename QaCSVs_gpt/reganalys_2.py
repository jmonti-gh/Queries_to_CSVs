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
from datetime import datetime
import os


## fixed variables - constants
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')        # Timestamp for filenames
query_file = "reganalys.qry"                                # Query file

server = '172.31.119.50'                                    # Conn parameters
database = 'Bantotal'
username = 'usr_motor'
password = 'MTM.m0t0R2024'
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
)


## Read input data - arguments
if len(sys.argv) < 2:       # Show structure of cursor.description amd exit
    headers = ["Index", "Element", "Meaning"]
    table_data = [
        [0, "`name`", "Column name (string)"],
        [1, "`type_code`", "Data type code (int, str, etc.) depending on driver"],
        [2, "`display_size`", "Max display width (usually None in pyodbc)"],
        [3, "`internal_size`", "Internal size in bytes (e.g., 4 for INT)"],
        [4, "`precision`", "Total digits for numeric fields"],
        [5, "`scale`", "Digits to the right of decimal point"],
        [6, "`null_ok`", "True if the column accepts NULLs"]
    ]

    print("\n📘 Structure of cursor.description:\n")
    print(f"{headers[0]:<8} {headers[1]:<20} {headers[2]}")
    print("-" * 70)
    for row in table_data:
        print(f"{str(row[0]):<8} {row[1]:<20} {row[2]}")

    csv_desc = f"cursor_description_{timestamp}.csv"
    with open(csv_desc, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(table_data)

    print(f"\n✔️ Structure saved to '{csv_desc}'")
    input('\n --> Press ENTER to close...')
    sys.exit(0)

else:                       # Read record_number and SQL Srv query
    try:
        record_number = int(sys.argv[1])
        if record_number <= 0:
            raise ValueError
    except ValueError:
        print("❌ The record number must be a positive integer.")
        sys.exit(1)

    if not os.path.exists(query_file):                          # Load query from file
        print(f"❌ Query file '{query_file}' not found.")
    sys.exit(1)

    with open(query_file, 'r', encoding='utf-8') as f:
        sql_query = f.read().strip()

    if not sql_query:
        print("❌ The query in 'reganalys.qry' is empty.")
        sys.exit(1)


## Additional constants - Output filenames
base_filename = f"record_{record_number}_{timestamp}"
txt_file = f"{base_filename}.txt"
csv_file = f"{base_filename}.csv"
html_file = f"{base_filename}.html"
md_file = f"{base_filename}.md"


## Main process
with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    cursor.execute(sql_query)

    rows = cursor.fetchall()
    if not cursor.description:
        print("❌ Query returned no columns.")
        sys.exit(1)

    if len(rows) < record_number:
        print(f"❌ Only {len(rows)} records found. Record #{record_number} is out of range.")
        sys.exit(1)

    selected_row = rows[record_number - 1]
    column_info = cursor.description

    headers = [
        "Field_name", "type_code", "display_size", "internal_size",
        "precision", "scale", "null_ok", "Value"
    ]

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

    # Save to .csv
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(table_rows)

    # Save to .html
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(f"<h2>Full metadata and values for record #{record_number}</h2>\n")
        f.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
        f.write("<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>\n")
        for row in table_rows:
            f.write("<tr>" + "".join(f"<td>{str(cell)}</td>" for cell in row) + "</tr>\n")
        f.write("</table>\n")

    # Save to .md
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Full metadata and values for record #{record_number}\n\n")
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["-" * len(h) for h in headers]) + "|\n")
        for row in table_rows:
            f.write("| " + " | ".join(str(cell) for cell in row) + " |\n")

    print(f"\n✅ Output saved to:")
    print(f"  - {txt_file}\n  - {csv_file}\n  - {html_file}\n  - {md_file}")
    input("\nPress 'Enter' to finish.")

