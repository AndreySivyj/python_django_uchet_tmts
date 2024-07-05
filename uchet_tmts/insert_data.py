
import sqlite3
import sys
import pathlib
from openpyxl import load_workbook


try:
    script_dir = pathlib.Path(sys.argv[0]).parent
    db_file = script_dir / 'db.sqlite3'

    # sqlite_connection = sqlite3.connect('db.sqlite3')
    sqlite_connection = sqlite3.connect(db_file)
    cursor = sqlite_connection.cursor()
    print("Подключен к SQLite")
       
    sqlite_insert_query = """INSERT INTO laptop_reestr_tmts_model
                          (status_id, owner_TMTS_id, name_TMTS_id, serial_number, username_responsible_TMTS, responsible_TMTS_id, location, created, creator_account_id, updated, comment, archived, start_of_operation_TMTS)
                          VALUES
                          (?,?,?,?,?,?,?,?,?,?,?,?,?);"""
    
    
    wb = load_workbook(script_dir / 'import_data.xlsx')
    sheet = wb['reestr']

    table_data = {}
    index = 1
    for cellObj in sheet['A2':'M107']:        
        tmp_row = []
        for cell in cellObj:            
            if cell.value == '':
                tmp_row.append(None)
            elif cell.value == None:
                tmp_row.append(" ")
            else:
                tmp_row.append(cell.value)

        table_data[index]=tmp_row
        index +=1

    for key, massive_data_row in table_data.items():
        print(key, massive_data_row)        
        count = cursor.execute(sqlite_insert_query, massive_data_row)
        sqlite_connection.commit()
        print("Запись успешно вставлена ​​в таблицу", cursor.rowcount)        

    cursor.close()

       
    

except sqlite3.Error as error:
    print("Ошибка при работе с SQLite", error)
finally:
    if sqlite_connection:
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")