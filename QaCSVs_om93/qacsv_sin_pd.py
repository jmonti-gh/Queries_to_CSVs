##################################################################
title = '''Queries a CSVs sin Pandas'''
##################################################################

'''
qacsv_sin_pd.py
    Script to generate CSVs from SQL Server DBs queries
    It reads a list of queries from an Excel file and generates CSV files
    qacsv_sin_pd.py es sin pandas SOLO para leer el query y escribir el csv
    (para procesar "CSVs_list.xlsx" seguimos usando pandas)

author:
    jm  |  ene2024 - mar2025

ver 1.0:


'''



#// 1. Required Libraries
import datetime as dtm
import pyodbc
import os
import pandas as pd
import sys
import shutil


#// 2. Defining Classes (Classes definition)

class MSSQLdb:
    '''MSSQLdb Class: to manage interaction w/SQLSRV databases'''
    __cnt = 0
    catalog = {'Lista de conexiones a DB NO establecidas': [],
               'Lista de Errores de conexiones a DBs': [],
               'Lista de DBs Conectadas': []}
    
    def __init__(self, srv, db, usr=None, pwd=None, port=1433):
        pyodbc.pooling = False                          # ?
        MSSQLdb.__cnt += 1                              
        self.id = MSSQLdb.__cnt                         # Count of DBs connected
        self.drv = '{ODBC Driver 17 for SQL Server}'    
        self.srv, self.port, self.db = srv, port, db
        self.usr, self.pwd = usr, pwd
        self.id_nm = f'''{self.id} _ * {self.srv} {self.db} *'''
        if usr and pwd:                                 # Conexión usando usuario y password
            cnxstr = f'DRIVER={self.drv};SERVER={self.srv};PORT={self.port};\
                DATABASE={self.db};UID={self.usr};PWD={self.pwd}'
        else:                                           # Conexión usando Windows Authentication  
            cnxstr = f"DRIVER={self.drv};SERVER={self.srv};PORT={self.port};\
                DATABASE={self.db};Trusted_Connection=yes"
        self._cnx = pyodbc.connect(cnxstr)              # connect to the DB
        self._cur = self._cnx.cursor()                  # create a cursor
        self.closed = False                             # flag to check if the connection is closed

    def close(self):
        self._cur.close()
        self._cnx.close()
        self.closed = True
    
    def execute(self, sql, params=None):
        self._cur.execute(sql, params or ())
    
    def qry_to_df(self, sql, params=None):
        self.execute(sql, params)
        cols = [i[0] for i in self._cur.description]
        dats = [list(xx) for xx in self._cur]
        return pd.DataFrame(data=dats, columns=cols)
        
    
class CSV:
    '''CSV Class: to manage CSV files'''
    __cnt = 0
    catalog = {'Lista de CSVs con Error de Procesamiento': [],
              'Lista de Errores de CSVs': [],
              'Lista de CSVs Creados': []}
    
    def __init__(self, folder, name, disk, path):
        CSV.__cnt += 1
        self.id = CSV.__cnt
        self.name = f'''{name}.csv'''
        self.path_folder = f'''{disk}:/{path}/{folder}'''
        self.csvfn = f'''{self.path_folder}/{self.name}'''
        self.id_nm = f'''{self.id} _ < {self.name} >'''

    def mk_folder(self):
        os.makedirs(self.path_folder)

    def wrt_csv_from_df(self, df, sep=';'):
        df.to_csv(self.csvfn, sep=sep, encoding='utf-8-sig', index=False)

    def err_hndl(self, txtln):
        wrt_info(txtln, level='err_')
        CSV.catalog['Lista de Errores de CSVs'].append(txtln)
        CSV.catalog['Lista de CSVs con Error de Procesamiento'].append(self.id_nm) 


#// 3. Global Variables (Constants)
        
## Get input file name with the lists of csvs - default: CSVs_list.xlsx
info = '''\n    Si va a utilizar un archivo de entrada disntinto a "CSVs_list.xlsx"
    ingrese su nombre a continunación (SIN la extensión ".xlsx", y respetando MAYÚSCULAS
    y minúsculas), caso contratio solo presione Enter \n'''   
try:
    print(info)
    lst_fn = input('Ingrese nombre de la planilla de entrada [Enter para "CSVs_list.xlsx"]: ')
    assert lst_fn != ''
    lst_fn = lst_fn + '.xlsx'
except AssertionError:
    lst_fn = 'CSVs_list.xlsx'
except:
    print('ERROR -> al ingresar nombre de archivo de entrada')
    res = input('''--> Presiones 'Enter' para cerrar ''')

## Some Miscellaneous Vars
prg = sys.argv[0].split('\\')[-1].split('.')[0]

## Datetime Vars
now = dtm.datetime.now()
thisyr, thismnth = now.year, now.month      # To validate period red from list_tasks_file
now_fname = now.strftime('%Y%m%d%H%M')      # datetime firm for filenames

## Paths and Filename Vars
# root = 'C:/MTM_PCE/z_GEN_CSVs/'
root = ''           # Empty root, just use relative paths
lsts = 'listas/'
lsts_done = f'{lsts[:-1]}_hechas/'
logs = 'logs/'

log_fn = f'''{prg.split('.')[0]}_{now_fname}.log'''

lst = root + lsts + lst_fn
log = root + logs + log_fn

lst_fn_split = lst_fn.split('.')
lst_done = f'''{root}{lsts_done}{lst_fn_split[0]}_{now_fname}.{lst_fn_split[1]}'''
lst_err = f'''{root}{lsts}{lst_fn_split[0]}_{now_fname}_err.{lst_fn_split[1]}'''

#-Creation of necessary subdirectories (of course 'listas/' exits if not impossible to read .xslx)
for sd in [lsts, lsts_done, logs]:
    try:
        os.mkdir(sd)
    except FileExistsError as e:
        pass


#// 4. Functions Definition

#### Make a funct. to write log w/timestamp and to screen
def wrt_info(msg,  logf=log, level='inf_'):
    tstamp = dtm.datetime.now().strftime('%b %d %H:%M:%S')
    ln = f'''{tstamp} {level} {msg}\n'''
    if level == 'err_':
        sys.stderr.write(ln)
    else:
        print(ln, end='')
    with open(logf, 'a') as f:
        f.write(ln)

## Get f_corte (last day of period): AAAAMMDD  - last day of a month
def get_last_day_date(per):
    prd_as_date = dtm.datetime.strptime(per, '%Y%m').date()
    # day 25 exists in every month. 9 days later, it's always next month
    nxt_mnth = prd_as_date.replace(day=25) + dtm.timedelta(days=9)
    # subtracting the number of days of nxt_mnth we'll get last day of original month
    last_day_date = nxt_mnth - dtm.timedelta(days=nxt_mnth.day)
    return dtm.datetime.strftime(last_day_date, '%Y%m%d')

## Get f_corte_12: fecha de corte same month last year
def get_corte_last_year(per):
    prd_as_date = dtm.datetime.strptime(per, '%Y%m').date()
    prd_12_date = prd_as_date.replace(year= prd_as_date.year - 1)
    prd_12 = dtm.datetime.strftime(prd_12_date, '%Y%m')
    return get_last_day_date(prd_12)

## List Directory Tree with os.walk()
def dirtree_os_walk(starting_directory):
    for root, directories, files in os.walk(starting_directory):
        print(f"Directory: {root}")
        for file in files:
            print(f"  File: {file}")

## Exit function - writing Last-log-LINE
def exit_prg(logf=log, msg='llamado a la función exit_prg()', complete=False):
    if not complete:
        txt = f'ABORT Execution: {msg}'
        wrt_info(txt, logf, level='err_')
    res = input('''\n --> Presiones 'Enter' para cerrar ''')
    sys.exit(0)


#// 5. Start LOG and Screen Display

ln = f'''> Ininciando ejecución de: {prg}
~~~~ {title}: construcción de archivos '.csv' según listado en: '{lst}' ~~~~
        --> LOG:  {log}'''
wrt_info(ln)


#// 6. Read list_tasks_file and Get date values from period
## 6.1. Read list tasks_files: CSVs_list.xlsx
try:
    lst_df = pd.read_excel(lst)
except Exception as e:
    ln = f'''>ERROR en 6.1.! Falló la lectura de {lst}
        {e}'''
    wrt_info(ln, level='err_')
    exit_prg()
else:
    # Display little sample of the result
    cols = ['Periodo', 'Carpeta', 'Nombre archivo CSV', 'Server Base']
    ln = f'''> {lst} leído correctamente:\n{lst_df[cols].head(3)}'''
    wrt_info(ln, level='ok_')

## 6.2. Get period, f_corte and fcorte_12 as strings
try:
    period = str(int(lst_df.loc[0, 'Periodo']))

    ## Validate period: 6 chars
    assert len(period) == 6
    peryr, permnth = int(period[:4]), int(period[4:])
    # 4 first digs: year >= 2014 and <= actual year
    assert peryr >= 2013 and peryr <= thisyr
    # last 2 digs: month >= 1 and < actual if year==thisyear else 12
    assert permnth >= 1 and permnth < (thismnth if peryr == thisyr else 13)
except Exception as e:
    ln = f'''>ERROR en 5.2.! Periodo cargado: '{period}' INVALIDO!
            Períodos válidos: de 201401 a {thisyr}{thismnth-1}
            {e} '''
    wrt_info(ln, level='err_')
    exit_prg()
else:
    f_corte = "'" + get_last_day_date(period) + "'"
    fcorte_12 = f"'{get_corte_last_year(period)}'"
    ln = f'''> Fecha leída, Periodo: {period}.- Calculados; Fecha de corte: {f_corte},
            Corte del mismo mes del año anterior: {fcorte_12} '''
    wrt_info(ln, level='ok_')

## 6.3 Get the total number of Files to be generated
total_files_to_process = len(lst_df)


#// 7. Replace period, f_corte, fcorte_12 in 'Path' and 'Modo de armado' of CVSs_list

lst_df['Path'] = lst_df['Path'].str.replace('periodo', period)
lst_df['Modo de armado'] = lst_df['Modo de armado'].str.replace('f_corte', f_corte)
lst_df['Modo de armado'] = lst_df['Modo de armado'].str.replace('fcorte_12', fcorte_12)
# replace strange "’" that appears w/libre office .xlsx
lst_df['Modo de armado'] = lst_df['Modo de armado'].str.replace("’", "'")


#// 8. Propagate last velid for NaN values in ['Carpeta', 'Server Base', 'Disk', 'Path']
cols_to_ffill = ['Carpeta', 'Server Base', 'Disk', 'Path']
lst_df[cols_to_ffill] = lst_df[cols_to_ffill].ffill()


#// 9. Splits lst_df in mini_dfs in base of server base

# get all diff values of Server_Base
SB_lst = lst_df['Server Base'].unique()

# split mini_lst_df and store in mind_dfs[]
mini_dfs = []
for psb in SB_lst:
    mini_df = lst_df[lst_df['Server Base'] == psb]
    mini_df.reset_index(drop=True, inplace=True)
    mini_dfs.append(mini_df)

ln = f'''Conexiones a DB a establecer:\n {SB_lst}'''
wrt_info(ln)


#// 10. --main-- 

for i in range(len(mini_dfs)):  # 1st loop, for e/mini_df - Cnx Srv-DB
    try:                        # 1. connect to de DB - db_obj
        sb = mini_dfs[i].loc[0, 'Server Base'].split()
        srv, dbnm = sb[0], sb[1]
        srv_db = f'''{srv} {dbnm}'''
        ln = f''' DB_ Conectando con: {srv_db}...'''
        wrt_info(ln)
        db = MSSQLdb(srv, dbnm, 'usr_motor', 'MTM.m0t0R2024')
    except Exception as e:
        ln = f'''>DB_ERROR en 10.a! Falló la conexión con {srv_db}
            {e}'''
        MSSQLdb.catalog['Lista de Errores de conexiones a DBs'].append(ln)
        MSSQLdb.catalog['Lista de conexiones a DB NO establecidas'].append(srv_db )
        wrt_info(ln, level='err_')
        continue
    else:
        ln = f'''> DB_ Conexión con {srv} {dbnm} ESTABLECIDA! ({db.id_nm})'''
        MSSQLdb.catalog['Lista de DBs Conectadas'].append(db.id_nm) 
        wrt_info(ln, level='ok_')

    total_rows = len(mini_dfs[i])
    ln = f'Iniciando procesamiento de queries a {srv} {dbnm} - {total_rows} queries'
    wrt_info(ln)

    for row in range(total_rows):       # 2. loop in e/row of mini_df
        # 2.1. create cvs_obj - prev get vars from row
        folder = mini_dfs[i].loc[row, 'Carpeta']
        fn = mini_dfs[i].loc[row, 'Nombre archivo CSV']
        qry = mini_dfs[i].loc[row, 'Modo de armado']
        disk = mini_dfs[i].loc[row, 'Disk']
        path = mini_dfs[i].loc[row, 'Path']
        
        csv = CSV(folder, fn, disk, path)
        ln = f'''{csv.id_nm} Iniciando armado archivo '{csv.csvfn}'\n Query:\n{qry} '''
        wrt_info(ln)

        try:                        # 2.2. Create the df from qry
            assert 'select' in qry.lower()
            df = db.qry_to_df(qry)
            # To convert Datetime fields to Objet in order to show time even if it's 0.
            for col in df.select_dtypes(include=['datetime64']).columns.tolist():
                df[col] = df[col].apply(lambda x: x.strftime('%F %T.%f')[:-3])
        except AssertionError:
            ln = f'''{csv.id_nm}ERROR en 10.c! Query a la DB NO segura!'''
            csv.err_hndl(ln)
        except Exception as e:
            ln = f'''{csv.id_nm}ERROR en 10.d! Falló  Query a la DB
                {e}'''
            csv.err_hndl(ln)
        else:
            try:                    # 2.3. if not exist Create folder to allocate csv
                if not os.path.isdir(csv.path_folder):
                    csv.mk_folder()
            except Exception as e: 
                ln = f'''{csv.id_nm}ERROR en 10.d! Falló la creación de {csv.path_folder}
                    {e}'''
                csv.err_hndl(ln)
            else:
                try:                # 2.4. Write the .csv
                    csv.wrt_csv_from_df(df)
                except Exception as e: 
                    ln = f'''{csv.id_nm}ERROR en 10.e! Falló la escritura the {csv.csvfn}
                        {e}'''
                    csv.err_hndl(ln)
                else:
                    ln = f'''{csv.id_nm} Creado exitosamente '{csv.csvfn}' '''
                    CSV.catalog['Lista de CSVs Creados'].append(f'{csv.id_nm} - {csv.csvfn}')                                        
                    wrt_info(ln, level='ok_')

        del csv     # delete csv obj.
    db.close()      # close cursor and db cnx.
    del db          # delete db obj.


#// 11. Rename or mv de list_tasks_files (CSV_lst.xlsx) processed
if (CSV.catalog['Lista de Errores de CSVs'] or
    MSSQLdb.catalog['Lista de Errores de conexiones a DBs']):
    try:
        os.rename(lst, lst_err)
    except Exception as e:
        ln = f'''>ERROR en 11.a! No se pudo renombrar {lst} a {lst_err}
                {e}'''                                        
        level = 'err_'
    else:
        ln = f'''>ok_ Se renombró {lst} a {lst_err}'''
        level = 'ok_'
    finally:
        ren_lst = lst_err
        wrt_info(ln, level=level)
else:    
    try:
        shutil.move(lst, lst_done)
    except Exception as e:
        ln = f'''>ERROR en 11.b! No se pudo mover {lst} a {lst_done}
                {e}'''                                        
        level = 'err_'
    else:
        ln = f'''>ok_ Se movió {lst} a {lst_done}'''
        level = 'ok_'
    finally:
        ren_lst = lst_done
        wrt_info(ln, level=level)


#// 12. Write SUMMARY and Show lists

### Especific funct. for this module
def lst_ln(txt, val):
    return f'''{txt:<25} ->  {val:<50}\n'''

def tbl_ln(v1, v2, v3):
    return f'''{v1:^25}{v2:^25}{v3:^25}\n'''

def show_dic(dic):
    res = ''
    for k, v in dic.items():
        len_lst = len(v)
        res += f''' - {k} ({len_lst}):\n'''
        for i in range(len_lst):
            res += f'''   {i+1} {v[i]}\n'''
        res += '\n'
    return res

### Some Values for the SUMMARY

# _total_files_to_process: len of CSVs_list readed as input
total_created_files = len(CSV.catalog['Lista de CSVs Creados'])
total_uncreated_files = total_files_to_process - total_created_files

ok_processed_files = total_created_files
bad_processed_files = len(CSV.catalog['Lista de CSVs con Error de Procesamiento'])
tot_processed_files = ok_processed_files + bad_processed_files

### core
summary = f'''  \n{'--- RESUMEN  ---':^75}\n\n'''

for t,v in [('Lista de CSVs a Procesar', lst),
            ('Archivo de LOGs', log),
            ('Lista CSVs Renombrada', ren_lst)]:
       summary += lst_ln(t, v)

summary += '\n'
summary += tbl_ln('Nro. de CSVs a Procesar',
                  'Nro. de CSVs Creados',
                  'Nro. de CSVs NO creados')
summary += tbl_ln(total_files_to_process,
                  total_created_files,
                  total_uncreated_files)

summary += '\n'
summary += tbl_ln('Nro. de CSVs Procesados',
                  'Nro. de CSVs Creados',
                  'Nro. de CSVs con Error de Procesamiento')
summary += tbl_ln(tot_processed_files,
                  ok_processed_files,
                  bad_processed_files)

summary += f'''\n# Resultado de CSVs Procesados en Conexiones Exitosas a DBs:\n'''
summary += show_dic(CSV.catalog)
summary += f'''\n# Resultado de Conexiones a DBs Consultadas:\n'''
summary += show_dic(MSSQLdb.catalog)

wrt_info(summary)


#// The End
exit_prg(complete=True)