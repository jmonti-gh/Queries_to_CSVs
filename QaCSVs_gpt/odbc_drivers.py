'''
odbc_driver.py
===================
'''


### Libraries
import pyodbc
import os
import platform
from datetime import datetime



### fixed variables - constants
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')        # Timestamp for filenames
pc_name = platform.node()                                   # Win computer where it is running
date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    # Actual Date-time
user = os.getlogin()                                        # Win user that is running the program


### Functions

def get_odbc_sqlserver_drv():
    try:
        drivers = pyodbc.drivers()      # List of installed ODBC drivers
        # sqlserver_drv = [driver for driver in drivers if 'SQL Server' in driver]
        # if sqlserver_drv:
        #     return sqlserver_drv[0]  # Return the first SQL Server driver found
        # else:
        #     raise Exception("No SQL Server ODBC driver found.")
    except Exception as e:
        raise Exception(f"Error retrieving ODBC drivers: {e}")
    
    return drivers



### main
odbc_drvs = get_odbc_sqlserver_drv()            # Get ODBC drivers

title = f"\nControladores ODBC instalados en {pc_name} ({user}) - {date_time}:"
# Console output
print(f"{title}\n{'-' * len(title)}")
for i, drv in enumerate(odbc_drvs):
    print(f"   {i + 1}.- {drv}")

# Save to .txt file
txt_file = f"odbc_drivers_{pc_name}_{timestamp}.txt"
txt_file = txt_file.replace(" ", "_").replace(":", "_")  # Replace spaces and colons with underscores
with open(txt_file, "w") as f:
    f.write(f"{title}\n{'-' * len(title)}\n")
    for i, drv in enumerate(odbc_drvs):
        f.write(f"   {i + 1}.- {drv}\n")

input("\nPresione Enter para cerrar...")


# Example usage
# driver = get_odbc_sqlserver_drv()
# conn = pyodbc.connect(f'DRIVER={driver};SERVER=your_server;DATABASE=your_database;UID=your_username;PWD=your_password')
