## Get input file name with the lists of csvs - CSVs_list.xlsx default
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

print(lst_fn)
res = input('''--> Presiones 'Enter' para cerrar ''')