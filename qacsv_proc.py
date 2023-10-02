#############################
title = '''Queries a CSVs'''
#############################
### author: jm - oct2023


#// 1. Required Libraries
import datetime as dtm
import pyodbc
import os
import pandas as pd
import sys
import shutil


#// 2. Global Variables (Constants)

## Some Miscellaneous Vars
prg = sys.argv[0].split('/')[-1].split('.')[0]

dres = dict()
dres['Lista de .cvs NO generados'] = []         # List of uncreated files
dres['Lista de ERRORES'] = []                   # Error list born empty
dres['Lista de .cvs generados'] = []            # CVSs created successfully

mssql_drv = '{ODBC Driver 17 for SQL Server}'   # autodetect!!??
flag_col = 'df_from_sql()¡ERROR!'   # to identify bad vs. empty queries

## Datetime Vars
now = dtm.datetime.now()
now_fname = now.strftime('%Y%m%d%H%M')      # datetime firm for filenames
thisyr, thismnth = now.year, now.month      # To validate period red from list_tasks_file

## Phats adn Filename Vars
# root = 'C:/MTM_PCE/z_GEN_CSVs/'
root = ''           # Empty root, just use relative paths
lsts = 'listas/'
lsts_done = f'{lsts[:-1]}_hechas/'
logs = 'logs/'

lst_fn = 'CSVs_list_loc.xlsx'
log_fn = f'''{prg.split('.')[0]}_{now_fname}.log'''

lst = root + lsts + lst_fn
log = root + logs + log_fn

lst_fn_split = lst_fn.split('.')
lst_done = f'''{root}{lsts_done}{lst_fn_split[0]}_{now_fname}.{lst_fn_split[1]}'''

#-NEED to create intrinsic sudirs (of course 'listas/' exits if not impossible to read .xslx)
for sd in [lsts, lsts_done, logs]:
    try:
        os.mkdir(sd)
    except FileExistsError as e:
        pass


#// 3. Functions Definition

## Write log w/timestamp
def wrt_log(logf, msg):
    with open(logf, 'a') as f:
        f.write(f'''{dtm.datetime.now().strftime('%b %d %H:%M:%S')} ''')
        f.write(msg +'\n')


## Get f_corte (last day of period): AAAAMMDD  - last day of a month
def get_last_day_date(per):
    prd_as_date = dtm.datetime.strptime(per, '%Y%m').date()
    # day 25 exists in every month. 9 days later, it's always next month
    nxt_mnth = prd_as_date.replace(day=25) + dtm.timedelta(days=9)
    # subtracting the number of days of nxt_mnth we'll get last day of original month
    last_day_date = nxt_mnth - dtm.timedelta(days=nxt_mnth.day)
    return dtm.datetime.strftime(last_day_date, '%Y%m%d')


## Get f_corte same month last year (fcorte_12)
def get_corte_last_year(per):
    prd_as_date = dtm.datetime.strptime(per, '%Y%m').date()
    prd_12_date = prd_as_date.replace(year= prd_as_date.year - 1)
    prd_12 = dtm.datetime.strftime(prd_12_date, '%Y%m')
    return get_last_day_date(prd_12)


## Function to Connect to the DB. SQL Srv authentication 
def cnx_db(srv, dbname):
    # mssql_drv just defined: '{ODBC Driver 17 for SQL Server}'
    user = 'soporte'
    passwd = 'Mate+123'

    # Construct the Connection String
    cnx_string = f'DRIVER={mssql_drv};SERVER={srv};' +\
            f'DATABASE={dbname};UID={user};PWD={passwd}'
    #ln = f'''{dtm.datetime.now().strftime('%b %d %H:%M:%S')} Conectando con: {srv} {dbname}...'''
    ln = f''''Conectando con: {srv} {dbname}...'''
    wrt_log(log, ln)
    print(ln)

    # Establishing the connection
    try:
        cnx = pyodbc.connect(cnx_string)
    except pyodbc.Error as e:
        cursor = False
        ln = f'''>ERROR en fun. cnx_db()! Falló la conexión con {srv} {dbname}
            {e} '''
        dres['Lista de ERRORES'].append(ln)
    else:
        cursor = cnx.cursor()
        ln = f'''>ok_ Conexión con {srv} {dbname} ESTABLECIDA!'''
    finally:
        wrt_log(log, ln)
        print(ln)
    
    return cursor

 
## --critical: Convert SQL qry to df
# Aux-function previous, to handle errors
def except_handling(error):
    ln = f'''>ERROR en fun. df_from_sql()! {error}'''
    df = pd.DataFrame({flag_col: [1]})  
    dres['Lista de ERRORES'].append(ln)
    wrt_log(log, ln)
    print(ln)
    return df

### function to convert SQL query to a df
def df_from_sql(qry, cur):
    getcols = getdats = False
    try:
        cur.execute(qry)
    except Exception as e:
        df = except_handling(e)
    else:
        try:
            cols = [i[0] for i in cur.description]
        except Exception as e:
            df = except_handling(e)
        else:
            getcols = True
        try:
            dats = [list(xx) for xx in cur]
        except Exception as e:
            df = except_handling(e)
        else:
            getdats = True
    
    if getcols and getdats:
        df = pd.DataFrame(data=dats, columns=cols)
    
    return df


## Create a folder w/full path
def mk_path_folder(pathf):
    try:
        os.makedirs(pathf)
    except FileExistsError:
        ext_status = f'''1-mk_path_folder(): ya existe '{pathf}' '''
        ln = ext_status
    except Exception as e:
        ln = f'''>ERROR en fun. mk_path_folder! al intentar crear carpeta '{pathf}'
    {e} '''
        ext_status = '2-mk_path_folder(): CRITICO'
        dres['Lista de ERRORES'].append(ln)
    else:
        ln = f'''>ok_ Carpeta '{pathf}' creada! '''
        ext_status = '0-mk_path_folder()'
    finally:
        wrt_log(log, ln)

    return ext_status


## List Directory Tree with os.walk()
def dirtree_os_walk(starting_directory):
    for root, directories, files in os.walk(starting_directory):
        print(f"Directory: {root}")
        for file in files:
            print(f"  File: {file}")


## Exit function - writing Last-log-LINE
def exit_prg(logf=log, msg='llamado a la función exit_prg()'):
    txt = f'ABORT Execution: {msg}'
    wrt_log(logf, txt)
    print(txt)
    sys.exit(0)


#// 4. Start LOG and Screen Display

ln = f'''> Ininciando ejecución de: {prg}

~~~~ {title}: construcción de archivos '.csv' según listado en: '{lst}' ~~~~
    
    --> Archivo LOG:  {log}
'''
wrt_log(log, ln)
print(f'''{dtm.datetime.now().strftime('%b %d %H:%M:%S')} {ln}''')


#// 5. Read list_tasks_file and Get date values from period
## 5.1. Read list tasks_files: CSVs_list.xlsx
try:
    lst_df = pd.read_excel(lst)
except Exception as e:
    ln = f'''>ERROR en 5.1.! Falló la lectura de {lst}
        {e} '''
    ext_status = '1-5.1.'
else:
    # Display little sample of the result
    cols = ['Periodo', 'Carpeta', 'Nombre archivo CSV', 'Server Base']
    ln = f'''>ok_ Leído {lst} CORRECTAMENTE!:\n{lst_df[cols].head(3)} '''
    ext_status = 0
finally:
    wrt_log(log, ln)
    print(ln)
    if ext_status == '1-5.1.':
        exit_prg()

## 5.2. Get period, f_corte and fcorte_12 as strings
try:
    period = str(int(lst_df.loc[0, 'Periodo']))

    ## Validate period: 6 chars
    assert len(period) == 6
    peryr, permnth = int(period[:4]), int(period[4:])
    # 4 first digs: year >= 2014 and <= actual year
    assert peryr >= 2013 and peryr <= thisyr
    # last 2 digs: month >= 1 and < actual if year==thisyear else 12
    assert permnth >= 1 and permnth < (thismnth if peryr == thisyr else 13)
except AssertionError as e:
    ln = f'''>ERROR en 5.2.! Periodo cargado: '{period}' INVALIDO!
        {e} '''
    ext_status = '1-5.2.'
except Exception as e:
    ln = f'''>ERROR en 5.2.! Al intentar leer el Periodo!
        {e} '''
    ext_status = '2-5.2.' 
else:
    f_corte = get_last_day_date(period)
    fcorte_12 = get_corte_last_year(period)
    ln = f'''>ok_ Fecha leída, Periodo: {period}.- Calculados; Fecha de corte: {f_corte},
            Corte del mismo mes del año anterior: {fcorte_12} '''
    ext_status = 0
finally:
    wrt_log(log, ln)
    print(ln)
    if ext_status == '1-5.2.' or ext_status == '2-5.2.':
        exit_prg(msg=f''' ext_status: {ext_status}''')


#// 6. Replace period, f_corte, fcorte_12 in Path and Modo de armado of CVSs_list

lst_df['Path'] = lst_df['Path'].str.replace('periodo', period)
lst_df['Modo de armado'] = lst_df['Modo de armado'].str.replace('f_corte', f_corte)
lst_df['Modo de armado'] = lst_df['Modo de armado'].str.replace('fcorte_12', fcorte_12)
# replace strange "’" that appears w/libre office .xlsx
lst_df['Modo de armado'] = lst_df['Modo de armado'].str.replace("’", "'")


#// 7. Propagate last velid for NaN values in ['Carpeta', 'Server Base', 'Disk', 'Path']
cols_to_ffill = ['Carpeta', 'Server Base', 'Disk', 'Path']
lst_df[cols_to_ffill] = lst_df[cols_to_ffill].ffill()


#// 8. Splits lst_df in mini_dfs in base of server base

# get all diff values of Server_Base
SB_lst = lst_df['Server Base'].unique()

# split mini_lst_df and store in mini_dfs
mini_dfs = []
for sbp in SB_lst:
    mini_df = lst_df[lst_df['Server Base'] == sbp]
    mini_df.reset_index(drop=True, inplace=True)
    mini_dfs.append(mini_df)

ln = f''' Conexiones a DB a establecer:\n {SB_lst}'''
wrt_log(log, ln)
print(ln)


#// 9. --main-- 

c = 0                           # a file counter, c: keeps track of processed files
for i in range(len(SB_lst)):    # 1st loop, for e/mini_df - Cnx Srv-DB

    ## Establish DB cnx - previously split Server from Base
    sb = SB_lst[i].split(' ')
    server, base = sb[0], sb[1]
    curs = cnx_db(server, base)
    if not curs: continue           # Connection FAILED, continue nex server-Base           
    
    ## Begin process of each row of the mini_df - 2d loop 
    df = mini_dfs[i]
    total_rows = len(df)
    ln = f'Iniciando procesamiento de queries a {server} {base} - {total_rows} queries'
    wrt_log(log, ln)
    print(ln)

    for row in range(total_rows):   # 2d loop, for e/row in the mini_df
        # get row values
        folder = df.loc[row, 'Carpeta']
        csv = df.loc[row, 'Nombre archivo CSV']
        query = df.loc[row, 'Modo de armado']
        disk = df.loc[row, 'Disk']
        path = df.loc[row, 'Path']
        path_folder = f'{disk}:/{path}/{folder}'
        csv_fn = f'{path_folder}/{csv}.csv'

        c += 1
        sub_ln = f'''_ {c} _ <> {csv} <> Iniciando armado archivo '{csv}' -> {csv_fn}'''
        ln = f'''{sub_ln}\n  query:\n{query} '''
        wrt_log(log, ln)
        print(f'''{dtm.datetime.now().strftime('%b %d %H:%M:%S')} {sub_ln}''')

        # Check if a SECURE query
        if 'select' not in query.lower():
            ln = f'''_ {c} _ <> {csv} <>>ERROR en 9.a! DB Query NO segura!'''
            dres['Lista de .cvs NO generados'].append(csv)
            dres['Lista de ERRORES'].append(ln)
            wrt_log(log, ln)
            print(ln)
            continue

        # Execute the query and get the resulted df
        res_df = df_from_sql(query, curs)
        
        # Check if Erroneous result
        if flag_col == res_df.columns[0]:
            ln = f'''_ {c} _ <> {csv} <>>ERROR en 9.b! Fallo al generar '{csv_fn}' '''
            dres['Lista de .cvs NO generados'].append(csv)
            wrt_log(log, ln)
            print(ln)
            continue

        # Write the df as the defined csv - previously create folder
        mk_path_folder(path_folder)

        try:
            res_df.to_csv(csv_fn, sep=';', encoding='utf-8', index=False)
        except Exception as e:
            ln = f'''_ {c} _ <> {csv} <>>ERROR en 9.c! Intentando escribir '{csv_fn}' '''
            dres['Lista de ERRORES'].append[ln]
            dres['Lista de .cvs NO generados'].append(csv)
        else:
            ln = f'''_ {c} _ <> {csv} <>>ok_ {csv_fn} CREADO! '''
            dres['Lista de .cvs generados'].append(csv)
        finally:
            wrt_log(log, ln)
            print(ln)

        #dirtree_os_walk(path_folder)

    ## At the finish of 2d loop must close DB connection!
    try: curs.close()
    except: pass
    try: del curs
    except: pass


#// 10. if not errors move list_tasks_file

if not dres['Lista de ERRORES']:
    try:
        shutil.move(lst, lst_done)
    except Exception as e:
        ln = f'''>ERROR en 10.! Intentando mover {lst} a {lst_done}\n
        {e}'''
    else:
        ln = f'''>ok_ Se movió {lst} a {lst_done}'''
else:
    ln = f'''>info Ocurrieron errores en el procesamiento de {lst}
            por lo que NO se movió a {lst_done}'''

wrt_log(log, ln)
print(ln)

#// 11. Write resultant lists in log and screen
for k, v in dres.items():
    len_lst = len(v)
    lista = f'''- {k} ({len_lst}):\n'''
    for i in range(len_lst):
        lista += f''' {i+1} {v[i]}\n'''
    
    wrt_log(log, lista)
    print(lista)   