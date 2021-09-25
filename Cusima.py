from tkinter import *
import time
from tkinter import filedialog as fd
import tkinter.ttk as ttk
from tkinter import messagebox as msg
import collections
import datetime
from itertools import filterfalse
import sqlite3
import os
import shutil
from tkcalendar import DateEntry

chne_values = []
ch_values = []
trans_chne_values = []
trans_ch_values = []
save_tasks_str = ""
save_tasks = ""
replace_finish_tasks_values = ""
doc_list = []
contact_parameters = []
db_data = []#Переменная контактов из базы данных
db_glue = []#Переменаая контактов из базы данных, очищенных от пробелов
trans_data = []#Переменная сделок из базы данных
trans_glue = []#Переменаая сделок из базы данных, очищенных от пробелов
town_lst = []#Переменная списка городов
town_lst_format = ""#Переменная формата отобраения времени, UTC, YEKT, MSK
tz_lst = []

#Функция очистки нужной сроки от мусора
def trash(stroka):
    stroka = stroka.lower()
    stroka = stroka.replace(" ","").replace("-","")
    stroka = stroka.replace(".","").replace(",","")
    stroka = stroka.replace("_","").replace("|","")
    stroka = stroka.replace("=","").replace("(","")
    stroka = stroka.replace(")","").replace("/","")
    stroka = stroka.replace("?","").replace("!","")
    stroka = stroka.replace("\\","").replace(";","")
    stroka = stroka.replace(":","").replace("'","")
    stroka = stroka.replace("[","").replace("]","")
    stroka = stroka.replace("{","").replace("}","")
    stroka = stroka.replace("#","").replace("$","")
    stroka = stroka.replace("%","").replace("^","")
    stroka = stroka.replace("<","").replace(">","")
    stroka = stroka.replace("~","").replace("`","")
    stroka = stroka.replace("№","").replace("ё","е")
    return stroka

#Функция сохранения в строку текущего времени
def time_str():
    base = str(datetime.datetime.now()).split(".")[0]
    base_data = base.split(" ")[0]
    base_time = base.split(" ")[1]
    year = base_data.split("-")[0]
    mounth = base_data.split("-")[1]
    day = base_data.split("-")[2]
    return str(day + "." + mounth + "." + year + " " + base_time)
def time_str_reverse():
    base = str(datetime.datetime.now()).split(".")[0]
    base_data = base.split(" ")[0]
    base_time = base.split(" ")[1]
    year = base_data.split("-")[0]
    mounth = base_data.split("-")[1]
    day = base_data.split("-")[2]
    return str(year + mounth + day + base_time.replace(":", ""))
def time_str_replace(stroka):
    base_date = stroka.split(" ")[0]
    base_time = stroka.split(" ")[1]
    year = base_date.split(".")[2]
    mounth = base_date.split(".")[1]
    day = base_date.split(".")[0]
    return str(year + mounth + day + base_time.replace(":", ""))

#Функция записи в log
def print_log(string):
    with open(r'log\log.txt', 'a') as file:
        file.write("\n{} - {}".format(str(string), time_str()))

#Функция считывания поисковой строки вкладки Картотека
def finder_get():
    get_find = trash(find_str.get())
    split_get_find = get_find.split('*')
    split_get_double_find = []
    for i in split_get_find:
        split_get_double_find.append(i.split('+'))
    return split_get_double_find
#Функция считывания поисковой строки вкладки Сделки
def trans_finder_get():
    trans_get_find = trash(trans_find_str.get())
    trans_split_get_find = trans_get_find.split('*')
    trans_split_get_double_find = []
    for i in trans_split_get_find:
        trans_split_get_double_find.append(i.split('+'))
    return trans_split_get_double_find

#Функция поиска в строке во вкладке Картотека
def find_db():
    find_db_list = []
    len_find_lst = len(finder_get())
    i=0
    while i <= len_find_lst-1:
        for item in db_glue:
            if all(x in item for x in finder_get()[i]):
                find_db_list.append(db_data[db_glue.index(item)])
        i += 1
    return find_db_list
#Функция поиска в строке во вкладке Сделки
def trans_find_db():
    trans_find_db_list = []
    trans_len_find_lst = len(trans_finder_get())
    i=0
    while i <= trans_len_find_lst-1:
        for item in trans_glue:
            if all(x in item for x in trans_finder_get()[i]):
                trans_find_db_list.append(trans_data[trans_glue.index(item)])
        i += 1
    return trans_find_db_list

#Функция обратного вызова при нажатии на кнопку фильтр во вкладке Картотека
def callback_combo_filter():
    combo_combo_filter.set('')
    combo_filter['values'] = contact_parameters
#Функция обратного вызова при нажатии на кнопку фильтр во вкладке Сделки
def trans_callback_combo_filter():
    trans_combo_combo_filter.set('')
    trans_combo_filter['values'] = ["Название сделки", "Компания", "Дата создания", "Обязательства по сделке"]

#Функция посткомманды для второго фильтра вкладки Картотека
def post_double_file_cabinet():
    #Назначаем значения внутри еще нераскрытого списка на основании отсортированного списка значений для предыдущей выбранной колонки
    combo_combo_filter['values'] = sorted(list(set(list(map(str, [x[contact_parameters.index(combo_filter.get())] for x in db_data])))))
#Функция посткомманды для второго фильтра вкладки Сделки
def trans_post_double_file_cabinet():
    #Назначаем значения внутри еще нераскрытого списка на основании отсортированного списка значений для предыдущей выбранной колонки
    trans_combo_combo_filter['values'] = sorted(list(set(list(map(str, [x[["Название сделки", "Компания", "Дата создания", "Обязательства по сделке"].index(trans_combo_filter.get())] for x in trans_data])))))

#Функции SQL запросов
def sql_quest_add():
    x = '?,'*len(contact_parameters)
    x = x[:-1]
    sql_1 = "INSERT INTO db VALUES "+"("+x+")"
    return sql_1

#Функции чтения Базы и Параметры контактов
def show():
    try:
        sqlite_connections = sqlite3.connect(r'db\db.db')
        cursor = sqlite_connections.cursor()
        print_log("DB OPEN")
        cursor.execute("""select * from trans""")
        global trans_data, trans_glue
        trans_data = cursor.fetchall()
        trans_glue = [trash(''.join([str(x) for x in item])) for item in trans_data]
        cursor.execute("""select * from db""")
        global db_data, db_glue, contact_parameters
        db_data = cursor.fetchall()
        db_glue = [trash(''.join([str(x) for x in item])) for item in db_data]
        contact_parameters = [description[0] for description in cursor.description]
        cursor.close()
    except sqlite3.Error as error:
        print_log("DB ERROR")
        print_log(error)
        msg.showerror("Внимание", "Произошла ошибка при чтении базы данных. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
    finally:
        if (sqlite_connections):
            sqlite_connections.close()
            print_log("DB CLOSE")    
show()

#Чтение из файла города и часовые пояса
def read_tz_format():
    global town_lst_format, tz_lst
    with open("db/town_format.txt", "r", encoding = "utf-8") as file:
        A = file.readlines()
    town_lst_format = A[0]
    with open("db/town.txt", "r", encoding = "utf-8") as file:
        B = file.readlines()
    tz_lst = [x.split(", ")[1] for x in B]
read_tz_format()

def read_town_lst():
    global town_lst
    with open("db/town.txt", "r", encoding = "utf-8") as file:
        A = file.readlines()
    town_lst = sorted([x.split(", ")[0] for x in A])
read_town_lst()

#Функция записи в базу данных (нужно добавлять список кортежей)
def create_contact(contacts):
    try:
        sqlite_connections = sqlite3.connect(r'db\db.db')
        cursor = sqlite_connections.cursor()
        print_log("DB OPEN")
        cursor.executemany("""{}""".format(sql_quest_add()), contacts)
        sqlite_connections.commit()
        cursor.close()
        print_log("Контакты {} внесены в базу".format(contacts))
    except sqlite3.Error as error:
        print_log("DB ERROR")
        print_log(error)
        msg.showerror("Внимание", "Произошла ошибка при добавлении контакта. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
    finally:
        if (sqlite_connections):
            sqlite_connections.close()
            print_log("DB CLOSE")    

#Функция удаления контакта
def delete_contact():
    values = [file_cabinet.item(x, option="values") for x in file_cabinet.selection()]
    if values != []:
        if msg.askyesno(title = "Внимание", message = "Удалить контакты: {}?".format(values)):
            for contact in values:
                try:
                    sqlite_connections = sqlite3.connect(r'db\db.db')
                    cursor = sqlite_connections.cursor()
                    print_log("DB OPEN")
                    cursor.execute("""DELETE FROM db WHERE ФИО = '{}'
                                                    AND Телефон = '{}'
                                                    AND Почта = '{}'
                                                    AND Компания = '{}'
                                                    AND Должность = '{}'
                                                    AND Город = '{}'
                                                    AND Дата = '{}'
                                                    AND Примечание = '{}'""".format(contact[0],
                                                                                    contact[1],
                                                                                    contact[2],
                                                                                    contact[3],
                                                                                    contact[4],
                                                                                    contact[5],
                                                                                    contact[6],
                                                                                    contact[7]))
                    sqlite_connections.commit()
                    cursor.close()
                    show()
                    tree_shower()
                    print_log("Контакты {} удалены из базы".format(values))
                except sqlite3.Error as error:
                    print_log("DB ERROR")
                    print_log(error)
                    msg.showerror("Внимание", "Произошла ошибка при удалении контакта. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                finally:
                    if (sqlite_connections):
                        sqlite_connections.close()
                        print_log("DB CLOSE")
    else:
        msg.showerror("Внимание", "Выберите данные для удаления")
def delete_contact_event(event):
    values = [file_cabinet.item(x, option="values") for x in file_cabinet.selection()]
    if values != []:
        if msg.askyesno(title = "Внимание", message = "Удалить контакты: {}?".format(values)):
            for contact in values:
                try:
                    sqlite_connections = sqlite3.connect(r'db\db.db')
                    cursor = sqlite_connections.cursor()
                    print_log("DB OPEN")
                    cursor.execute("""DELETE FROM db WHERE ФИО = '{}'
                                                    AND Телефон = '{}'
                                                    AND Почта = '{}'
                                                    AND Компания = '{}'
                                                    AND Должность = '{}'
                                                    AND Город = '{}'
                                                    AND Дата = '{}'
                                                    AND Примечание = '{}'""".format(contact[0],
                                                                                    contact[1],
                                                                                    contact[2],
                                                                                    contact[3],
                                                                                    contact[4],
                                                                                    contact[5],
                                                                                    contact[6],
                                                                                    contact[7]))
                    sqlite_connections.commit()
                    cursor.close()
                    show()
                    tree_shower()
                    print_log("Контакты {} удалены из базы".format(values))
                except sqlite3.Error as error:
                    print_log("DB ERROR")
                    print_log(error)
                    msg.showerror("Внимание", "Произошла ошибка при удалении контакта. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                finally:
                    if (sqlite_connections):
                        sqlite_connections.close()
                        print_log("DB CLOSE")
    else:
        msg.showerror("Внимание", "Выберите данные для удаления")

#Создание функции, считывающей положение окна root и возвращающей список "отклонение от горизонтали, отклонение от вертикали" для окна root
def size():
    size_root = root.geometry()
    F = []
    size_root = size_root.split("+")
    F.append(size_root[1])
    F.append(size_root[2])
    return F

#Окно добавления контакта в базу данных
def add_db():
    add_window = Toplevel()
    add_window.title("Добавить контакт")
    add_window.resizable(False, False)
    add_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))

    #Создание функций вызова контекстного меню
    def add_popup(event):
        global x, y
        x = event.x
        y = event.y
        add_menu.post(event.x_root, event.y_root)

    def add_popupFocusOut(event):
        add_menu.unpost()
        
    def add_copy_selection():
        try:
            add_window.clipboard_clear()
            add_window.clipboard_append(add_window.focus_get().selection_get())
        except :
            return
            
    def add_paste_cl():
        try:
            add_window.focus_get().insert(INSERT, add_window.clipboard_get())
        except :
            return
    
    add_menu = Menu(tearoff = False)
    add_menu.add_command(label = "Копировать", command = add_copy_selection)
    add_menu.add_command(label = "Вставить", command = add_paste_cl)

    def add_window_quit():
        add_window.destroy()        
    
    #Создание функции, считывающей в список текст из полей ввода
    def add_window_save():
        new_btn_1.configure(state = "disable")
        new_btn_2.configure(state = "disable")
        if msg.askyesno(title = "Внимание", message = "Добавить новый контакт?"):
            n = 0
            N=[]
            while n <= len(contact_parameters)-1:
                N.append(list(list(add_window.children.values())[n].children.values())[1])
                n += 1
            M=[]
            for entr in N:
                if entr.get() != "":
                    M.append(entr.get().replace("\'", ""))
                else:
                    M.append("-")

            MN = [tuple(M)]
            if trash("".join(M).replace("+", "")) != "":
                create_contact(MN)
                show()
                tree_shower()
            else:
                msg.showinfo("Внимание", "Введите данные для сохранения")
        new_btn_1.configure(state = "normal")
        new_btn_2.configure(state = "normal")
        add_window.focus()
        new_entry_2.set("{}".format(time_str()))
    def add_window_save_event(event):
        new_btn_1.configure(state = "disable")
        new_btn_2.configure(state = "disable")
        if msg.askyesno(title = "Внимание", message = "Добавить новый контакт?"):
            n = 0
            N=[]
            while n <= len(contact_parameters)-1:
                N.append(list(list(add_window.children.values())[n].children.values())[1])
                n += 1
            M=[]
            for entr in N:
                if entr.get() != "":
                    M.append(entr.get().replace("\'", ""))
                else:
                    M.append("-")

            MN = [tuple(M)]
            if trash("".join(M).replace("+", "")) != "":
                create_contact(MN)
                show()
                tree_shower()
            else:
                msg.showinfo("Внимание", "Введите данные для сохранения")
        new_btn_1.configure(state = "normal")
        new_btn_2.configure(state = "normal")
        add_window.focus()
        new_entry_2.set("{}".format(time_str()))

    def post_town_lst():
        new_entry_1['values'] = town_lst
    def town_selected(event):
        town_name = new_entry_1.get()
        tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
        if town_lst_format  == "UTC":
            tz_hour += 3
        elif town_lst_format == "YEKT":
            tz_hour -= 2
        if tz_hour >= 0:
            tz_hour = "+"+str(tz_hour)
        new_label_22.config(text = "{}, {}".format(town_lst_format, tz_hour))
    def post_company_name_into():
        x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
        new_entry_4['values'] = x
        return x
    def post_company_name_into_event(event):
        x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
        new_entry_4['values'] = x
        return x
    def post_position_name():
        x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
        new_entry_5['values'] = x
        return x
    def post_position_name_event(event):
        x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
        new_entry_5['values'] = x
        return x
    numer = 1
    while numer <= len(contact_parameters):
        if numer != 4 and numer != 5 and numer != 6 and numer != 7:
            new_frame = Frame(add_window)
            new_frame.pack(fill = X, expand = True)
            new_label = Label(new_frame, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry = Entry(new_frame, width = 50)
            new_label.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry.pack(side = LEFT, fill = BOTH, expand = True)
            new_entry.bind("<Return>", add_window_save_event)
            numer += 1
        elif numer == 4:
            new_frame_4 = Frame(add_window)
            new_frame_4.pack(fill = X, expand = True)
            new_label_4 = Label(new_frame_4, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry_4 = ttk.Combobox(new_frame_4,
                                       values = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data]))))),
                                     postcommand = post_company_name_into,
                                     width = 50)
            new_label_4.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_4.pack(side = LEFT, fill = BOTH, expand = True)
            new_entry_4.bind("<<ComboboxSelected>>", post_company_name_into_event)
            numer += 1
        elif numer == 5:
            new_frame_5 = Frame(add_window)
            new_frame_5.pack(fill = X, expand = True)
            new_label_5 = Label(new_frame_5, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry_5 = ttk.Combobox(new_frame_5,
                                       values = sorted(list(set(list(map(str, [x[4] for x in db_data]))))),
                                     postcommand = post_position_name,
                                     width = 50)
            new_label_5.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_5.pack(side = LEFT, fill = BOTH, expand = True)
            new_entry_5.bind("<<ComboboxSelected>>", post_position_name_event)
            numer += 1
        elif numer == 6:
            new_frame_1 = Frame(add_window)
            new_frame_1.pack(fill = X, expand = True)
            new_label_1 = Label(new_frame_1, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry_1 = ttk.Combobox(new_frame_1, values = town_lst,
                                     postcommand = post_town_lst,
                                     width = 50,
                                     state = 'readonly')
            new_label_1.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_1.pack(side = LEFT, fill = BOTH, expand = True)
            

            new_label_22 = Label(new_frame_1, text = "{}".format(town_lst_format),
                                width = 10, bg = 'lightgreen')
            new_label_22.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_1.bind("<<ComboboxSelected>>", town_selected)
            numer += 1
        elif numer == 7:
            new_frame_2 = Frame(add_window)
            new_frame_2.pack(fill = X, expand = True)
            new_label_2 = Label(new_frame_2, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            def lambda_eval_postcommand():
                new_entry_2['values']=[time_str()]
            new_entry_2 = ttk.Combobox(new_frame_2,
                                     postcommand = lambda_eval_postcommand,
                                     width = 50,
                                     state = 'readonly')
            new_entry_2.set("{}".format(time_str()))
            
            new_label_2.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_2.pack(side = LEFT, fill = BOTH, expand = True)

            numer += 1
            
    new_frame_2 = Frame(add_window)
    new_frame_2.pack(fill = X, expand = True)
    new_btn_1 = Button(new_frame_2, text = "Сохранить", command = add_window_save)
    new_btn_1.pack(side = LEFT, fill = X, expand = True)
    new_btn_2 = Button(new_frame_2, text = "Закрыть", command = add_window_quit)
    new_btn_2.pack(side = LEFT, fill = X, expand = True)

    add_window.bind("<Button-3>", add_popup)
    add_window.bind("<FocusIn>", add_popupFocusOut)
    
    add_window.bind("<Control-C>", add_copy_selection)
    add_window.bind("<Control-V>", add_paste_cl)
    def add_window_key_callback(event):
        if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
            if chr(event.keycode) == "C":
                add_copy_selection()
            elif chr(event.keycode) == "V":
                add_paste_cl()
    add_window.bind("<Key>", add_window_key_callback)

    
    list(list(add_window.children.values())[0].children.values())[1].focus()
def add_db_event(event):
    add_window = Toplevel()
    add_window.title("Добавить контакт")
    add_window.resizable(False, False)
    add_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))

    #Создание функций вызова контекстного меню
    def add_popup(event):
        global x, y
        x = event.x
        y = event.y
        add_menu.post(event.x_root, event.y_root)

    def add_popupFocusOut(event):
        add_menu.unpost()
        
    def add_copy_selection():
        try:
            add_window.clipboard_clear()
            add_window.clipboard_append(add_window.focus_get().selection_get())
        except :
            return
            
    def add_paste_cl():
        try:
            add_window.focus_get().insert(INSERT, add_window.clipboard_get())
        except :
            return
    
    add_menu = Menu(tearoff = False)
    add_menu.add_command(label = "Копировать", command = add_copy_selection)
    add_menu.add_command(label = "Вставить", command = add_paste_cl)

    def add_window_quit():
        add_window.destroy()        
    
    #Создание функции, считывающей в список текст из полей ввода
    def add_window_save():
        new_btn_1.configure(state = "disable")
        new_btn_2.configure(state = "disable")
        if msg.askyesno(title = "Внимание", message = "Добавить новый контакт?"):
            n = 0
            N=[]
            while n <= len(contact_parameters)-1:
                N.append(list(list(add_window.children.values())[n].children.values())[1])
                n += 1
            M=[]
            for entr in N:
                if entr.get() != "":
                    M.append(entr.get().replace("\'", ""))
                else:
                    M.append("-")

            MN = [tuple(M)]
            if trash("".join(M).replace("+", "")) != "":
                create_contact(MN)
                show()
                tree_shower()
            else:
                msg.showinfo("Внимание", "Введите данные для сохранения")
        new_btn_1.configure(state = "normal")
        new_btn_2.configure(state = "normal")
        add_window.focus()
        new_entry_2.set("{}".format(time_str()))
    def add_window_save_event(event):
        new_btn_1.configure(state = "disable")
        new_btn_2.configure(state = "disable")
        if msg.askyesno(title = "Внимание", message = "Добавить новый контакт?"):
            n = 0
            N=[]
            while n <= len(contact_parameters)-1:
                N.append(list(list(add_window.children.values())[n].children.values())[1])
                n += 1
            M=[]
            for entr in N:
                if entr.get() != "":
                    M.append(entr.get().replace("\'", ""))
                else:
                    M.append("-")

            MN = [tuple(M)]
            if trash("".join(M).replace("+", "")) != "":
                create_contact(MN)
                show()
                tree_shower()
            else:
                msg.showinfo("Внимание", "Введите данные для сохранения")
        new_btn_1.configure(state = "normal")
        new_btn_2.configure(state = "normal")
        add_window.focus()
        new_entry_2.set("{}".format(time_str()))

    def post_town_lst():
        new_entry_1['values'] = town_lst
    def town_selected(event):
        town_name = new_entry_1.get()
        tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
        if town_lst_format  == "UTC":
            tz_hour += 3
        elif town_lst_format == "YEKT":
            tz_hour -= 2
        if tz_hour >= 0:
            tz_hour = "+"+str(tz_hour)
        new_label_22.config(text = "{}, {}".format(town_lst_format, tz_hour))
    def post_company_name_into():
        x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
        new_entry_4['values'] = x
        return x
    def post_company_name_into_event(event):
        x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
        new_entry_4['values'] = x
        return x
    def post_position_name():
        x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
        new_entry_5['values'] = x
        return x
    def post_position_name_event(event):
        x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
        new_entry_5['values'] = x
        return x
    numer = 1
    while numer <= len(contact_parameters):
        if numer != 4 and numer != 5 and numer != 6 and numer != 7:
            new_frame = Frame(add_window)
            new_frame.pack(fill = X, expand = True)
            new_label = Label(new_frame, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry = Entry(new_frame, width = 50)
            new_label.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry.pack(side = LEFT, fill = BOTH, expand = True)
            new_entry.bind("<Return>", add_window_save_event)
            numer += 1
        elif numer == 4:
            new_frame_4 = Frame(add_window)
            new_frame_4.pack(fill = X, expand = True)
            new_label_4 = Label(new_frame_4, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry_4 = ttk.Combobox(new_frame_4,
                                       values = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data]))))),
                                     postcommand = post_company_name_into,
                                     width = 50)
            new_label_4.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_4.pack(side = LEFT, fill = BOTH, expand = True)
            new_entry_4.bind("<<ComboboxSelected>>", post_company_name_into_event)
            numer += 1
        elif numer == 5:
            new_frame_5 = Frame(add_window)
            new_frame_5.pack(fill = X, expand = True)
            new_label_5 = Label(new_frame_5, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry_5 = ttk.Combobox(new_frame_5,
                                       values = sorted(list(set(list(map(str, [x[4] for x in db_data]))))),
                                     postcommand = post_position_name,
                                     width = 50)
            new_label_5.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_5.pack(side = LEFT, fill = BOTH, expand = True)
            new_entry_5.bind("<<ComboboxSelected>>", post_position_name_event)
            numer += 1
        elif numer == 6:
            new_frame_1 = Frame(add_window)
            new_frame_1.pack(fill = X, expand = True)
            new_label_1 = Label(new_frame_1, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            new_entry_1 = ttk.Combobox(new_frame_1, values = town_lst,
                                     postcommand = post_town_lst,
                                     width = 50,
                                     state = 'readonly')
            new_label_1.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_1.pack(side = LEFT, fill = BOTH, expand = True)
            new_label_22 = Label(new_frame_1, text = "{}".format(town_lst_format),
                                width = 10, bg = 'lightgreen')
            new_label_22.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_1.bind("<<ComboboxSelected>>", town_selected)
            numer += 1
        elif numer == 7:
            new_frame_2 = Frame(add_window)
            new_frame_2.pack(fill = X, expand = True)
            new_label_2 = Label(new_frame_2, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
            def lambda_eval_postcommand():
                new_entry_2['values']=[time_str()]
            new_entry_2 = ttk.Combobox(new_frame_2,
                                     postcommand = lambda_eval_postcommand,
                                     width = 50,
                                     state = 'readonly')
            new_entry_2.set("{}".format(time_str()))
            new_label_2.pack(side = LEFT, fill = BOTH, expand = False)
            new_entry_2.pack(side = LEFT, fill = BOTH, expand = True)
            numer += 1
    new_frame_2 = Frame(add_window)
    new_frame_2.pack(fill = X, expand = True)
    new_btn_1 = Button(new_frame_2, text = "Сохранить", command = add_window_save)
    new_btn_1.pack(side = LEFT, fill = X, expand = True)
    new_btn_2 = Button(new_frame_2, text = "Закрыть", command = add_window_quit)
    new_btn_2.pack(side = LEFT, fill = X, expand = True)
    add_window.bind("<Button-3>", add_popup)
    add_window.bind("<FocusIn>", add_popupFocusOut)
    add_window.bind("<Control-C>", add_copy_selection)
    add_window.bind("<Control-V>", add_paste_cl)
    def add_window_key_callback(event):
        if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
            if chr(event.keycode) == "C":
                add_copy_selection()
            elif chr(event.keycode) == "V":
                add_paste_cl()
    add_window.bind("<Key>", add_window_key_callback)
    list(list(add_window.children.values())[0].children.values())[1].focus()

#Окно изменения контакта
def ch_db(event):
    try:
        global chne_values
        chne_values = file_cabinet.item(file_cabinet.selection(), option="values")
        if chne_values != "":
            ch_window = Toplevel()
            ch_window.title("Изменить контакт")
            ch_window.resizable(False, False)
            ch_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))

            #Создание функций вызова контекстного меню
            def ch_popup(event):
                global x, y
                x = event.x
                y = event.y
                ch_menu.post(event.x_root, event.y_root)

            def ch_popupFocusOut(event):
                ch_menu.unpost()
                
            def ch_copy_selection():
                try:
                    ch_window.clipboard_clear()
                    ch_window.clipboard_append(ch_window.focus_get().selection_get())
                except :
                    return
                    
            def ch_paste_cl():
                try:
                    ch_window.focus_get().insert(INSERT, ch_window.clipboard_get())
                except :
                    return
            
            ch_menu = Menu(tearoff = False)
            ch_menu.add_command(label = "Копировать", command = ch_copy_selection)
            ch_menu.add_command(label = "Вставить", command = ch_paste_cl)

            def ch_window_quit():
                ch_window.destroy()
            def ch_window_quit_event(event):
                ch_window.destroy()
                
            def post_town_lst():
                new_entry_1['values'] = town_lst
            def town_selected(event):
                town_name = new_entry_1.get()
                tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                if town_lst_format  == "UTC":
                    tz_hour += 3
                elif town_lst_format == "YEKT":
                    tz_hour -= 2
                if tz_hour >= 0:
                    tz_hour = "+"+str(tz_hour)
                new_label_22.config(text = "{}, {}".format(town_lst_format, tz_hour))
            def town_selected_not_event():
                town_name = new_entry_1.get()
                if town_name in town_lst:
                    tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                    if town_lst_format  == "UTC":
                        tz_hour += 3
                    elif town_lst_format == "YEKT":
                        tz_hour -= 2
                    if tz_hour >= 0:
                        tz_hour = "+"+str(tz_hour)
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                else:
                    tz_hour = "???"
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                return new_label_2_txt

            #Создание функции, считывающей в список текст из полей ввода
            def ch_window_save():
                global chne_values
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Изменить контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(ch_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        try:
                            sqlite_connections = sqlite3.connect(r'db\db.db')
                            cursor = sqlite_connections.cursor()
                            print_log("DB OPEN")
                            cursor.execute("""DELETE FROM db WHERE ФИО = '{}'
                                                            AND Телефон = '{}'
                                                            AND Почта = '{}'
                                                            AND Компания = '{}'
                                                            AND Должность = '{}'
                                                            AND Город = '{}'
                                                            AND Дата = '{}'
                                                            AND Примечание = '{}'""".format(chne_values[0],
                                                                                            chne_values[1],
                                                                                            chne_values[2],
                                                                                            chne_values[3],
                                                                                            chne_values[4],
                                                                                            chne_values[5],
                                                                                            chne_values[6],
                                                                                            chne_values[7]))
                            sqlite_connections.commit()
                            cursor.close()
                            show()
                            tree_shower()
                            print_log("Контакты {} удалены из базы".format(chne_values))
                        except sqlite3.Error as error:
                            print_log("DB ERROR")
                            print_log(error)
                            msg.showerror("Внимание", "Произошла ошибка при удалении контакта. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                        finally:
                            if (sqlite_connections):
                                sqlite_connections.close()
                                print_log("DB CLOSE")
                        create_contact(MN)
                        chne_values = [str(x) for x in MN[0]]
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                ch_window.focus()
                new_btn_2.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
            def ch_window_save_event(event):
                global chne_values
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Изменить контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(ch_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        try:
                            sqlite_connections = sqlite3.connect(r'db\db.db')
                            cursor = sqlite_connections.cursor()
                            print_log("DB OPEN")
                            cursor.execute("""DELETE FROM db WHERE ФИО = '{}'
                                                            AND Телефон = '{}'
                                                            AND Почта = '{}'
                                                            AND Компания = '{}'
                                                            AND Должность = '{}'
                                                            AND Город = '{}'
                                                            AND Дата = '{}'
                                                            AND Примечание = '{}'""".format(chne_values[0],
                                                                                            chne_values[1],
                                                                                            chne_values[2],
                                                                                            chne_values[3],
                                                                                            chne_values[4],
                                                                                            chne_values[5],
                                                                                            chne_values[6],
                                                                                            chne_values[7]))
                            sqlite_connections.commit()
                            cursor.close()
                            show()
                            tree_shower()
                            print_log("Контакты {} удалены из базы".format(chne_values))
                        except sqlite3.Error as error:
                            print_log("DB ERROR")
                            print_log(error)
                            msg.showerror("Внимание", "Произошла ошибка при удалении контакта. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                        finally:
                            if (sqlite_connections):
                                sqlite_connections.close()
                                print_log("DB CLOSE")
                        create_contact(MN)
                        chne_values = [str(x) for x in MN[0]]
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                ch_window.focus()
                new_btn_2.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
                
            def post_company_name_into():
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_company_name_into_event(event):
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_position_name():
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x
            def post_position_name_event(event):
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x

            numer = 1
            while numer <= len(contact_parameters):
                if numer != 4 and numer != 5 and numer != 6 and numer != 7:
                    new_frame = Frame(ch_window)
                    new_frame.pack(fill = X, expand = True)
                    new_label = Label(new_frame, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry = Entry(new_frame, width = 50)
                    new_entry.insert(0, "{}".format(chne_values[numer-1]))
                    new_label.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry.bind("<Return>", ch_window_save_event)
                    numer += 1
                elif numer == 4:
                    new_frame_4 = Frame(ch_window)
                    new_frame_4.pack(fill = X, expand = True)
                    new_label_4 = Label(new_frame_4, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_4 = ttk.Combobox(new_frame_4,
                                               values = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data]))))),
                                             postcommand = post_company_name_into,
                                             width = 50)
                    new_entry_4.set("{}".format(chne_values[numer-1]))
                    new_label_4.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_4.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_4.bind("<<ComboboxSelected>>", post_company_name_into_event)
                    numer += 1
                elif numer == 5:
                    new_frame_5 = Frame(ch_window)
                    new_frame_5.pack(fill = X, expand = True)
                    new_label_5 = Label(new_frame_5, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_5 = ttk.Combobox(new_frame_5,
                                               values = sorted(list(set(list(map(str, [x[4] for x in db_data]))))),
                                             postcommand = post_position_name,
                                             width = 50)
                    new_entry_5.set("{}".format(chne_values[numer-1]))
                    new_label_5.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_5.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_5.bind("<<ComboboxSelected>>", post_position_name_event)
                    numer += 1
                elif numer == 6:
                    new_frame_1 = Frame(ch_window)
                    new_frame_1.pack(fill = X, expand = True)
                    new_label_1 = Label(new_frame_1, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_1 = ttk.Combobox(new_frame_1, values = town_lst,
                                             postcommand = post_town_lst,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_1.set("{}".format(chne_values[numer-1]))
                    new_label_1.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.pack(side = LEFT, fill = BOTH, expand = True)
                    new_label_22 = Label(new_frame_1, text = "{}".format(town_selected_not_event()),
                                        width = 10, bg = 'lightgreen')
                    new_label_22.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.bind("<<ComboboxSelected>>", town_selected)
                    numer += 1
                elif numer == 7:
                    new_frame_2 = Frame(ch_window)
                    new_frame_2.pack(fill = X, expand = True)
                    new_label_2 = Label(new_frame_2, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    def new_lambda_eval_postcommand():
                        new_entry_2['values']=[time_str()]
                    new_entry_2 = ttk.Combobox(new_frame_2,
                                             postcommand = new_lambda_eval_postcommand,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_2.set("{}".format(chne_values[numer-1]))
                    new_label_2.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_2.pack(side = LEFT, fill = BOTH, expand = True)
                    numer += 1
            new_frame_2 = Frame(ch_window)
            new_frame_2.pack(fill = X, expand = True)
            new_btn_1 = Button(new_frame_2, text = "Сохранить", command = ch_window_save)
            new_btn_2 = Button(new_frame_2, text = "Закрыть", command = ch_window_quit)
            new_btn_1.pack(side = LEFT, fill = X, expand = True)
            new_btn_2.pack(side = LEFT, fill = X, expand = True)
            new_btn_2.focus()
            ch_window.bind("<Button-3>", ch_popup)
            ch_window.bind("<FocusIn>", ch_popupFocusOut)
            ch_window.bind("<Control-C>", ch_copy_selection)
            ch_window.bind("<Control-V>", ch_paste_cl)
            def ch_window_key_callback(event):
                if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                    if chr(event.keycode) == "C":
                        ch_copy_selection()
                    elif chr(event.keycode) == "V":
                        ch_paste_cl()
            ch_window.bind("<Key>", ch_window_key_callback)
            new_btn_2.bind("<Return>", ch_window_quit_event)
        else:
            msg.showerror("Внимание", "Выберите данные для изменения")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")
def ch_db_not_event():
    try:
        global chne_values
        chne_values = file_cabinet.item(file_cabinet.selection(), option="values")
        if chne_values != "":
            ch_window = Toplevel()
            ch_window.title("Изменить контакт")
            ch_window.resizable(False, False)
            ch_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))

            #Создание функций вызова контекстного меню
            def ch_popup(event):
                global x, y
                x = event.x
                y = event.y
                ch_menu.post(event.x_root, event.y_root)

            def ch_popupFocusOut(event):
                ch_menu.unpost()
                
            def ch_copy_selection():
                try:
                    ch_window.clipboard_clear()
                    ch_window.clipboard_append(ch_window.focus_get().selection_get())
                except :
                    return
                    
            def ch_paste_cl():
                try:
                    ch_window.focus_get().insert(INSERT, ch_window.clipboard_get())
                except :
                    return
            
            ch_menu = Menu(tearoff = False)
            ch_menu.add_command(label = "Копировать", command = ch_copy_selection)
            ch_menu.add_command(label = "Вставить", command = ch_paste_cl)

            def ch_window_quit():
                ch_window.destroy()
            def ch_window_quit_event(event):
                ch_window.destroy()
                
            def post_town_lst():
                new_entry_1['values'] = town_lst
            def town_selected(event):
                town_name = new_entry_1.get()
                tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                if town_lst_format  == "UTC":
                    tz_hour += 3
                elif town_lst_format == "YEKT":
                    tz_hour -= 2
                if tz_hour >= 0:
                    tz_hour = "+"+str(tz_hour)
                new_label_22.config(text = "{}, {}".format(town_lst_format, tz_hour))
            def town_selected_not_event():
                town_name = new_entry_1.get()
                if town_name in town_lst:
                    tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                    if town_lst_format  == "UTC":
                        tz_hour += 3
                    elif town_lst_format == "YEKT":
                        tz_hour -= 2
                    if tz_hour >= 0:
                        tz_hour = "+"+str(tz_hour)
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                else:
                    tz_hour = "???"
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                return new_label_2_txt

            #Создание функции, считывающей в список текст из полей ввода
            def ch_window_save():
                global chne_values
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Изменить контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(ch_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        try:
                            sqlite_connections = sqlite3.connect(r'db\db.db')
                            cursor = sqlite_connections.cursor()
                            print_log("DB OPEN")
                            cursor.execute("""DELETE FROM db WHERE ФИО = '{}'
                                                            AND Телефон = '{}'
                                                            AND Почта = '{}'
                                                            AND Компания = '{}'
                                                            AND Должность = '{}'
                                                            AND Город = '{}'
                                                            AND Дата = '{}'
                                                            AND Примечание = '{}'""".format(chne_values[0],
                                                                                            chne_values[1],
                                                                                            chne_values[2],
                                                                                            chne_values[3],
                                                                                            chne_values[4],
                                                                                            chne_values[5],
                                                                                            chne_values[6],
                                                                                            chne_values[7]))
                            sqlite_connections.commit()
                            cursor.close()
                            show()
                            tree_shower()
                            print_log("Контакты {} удалены из базы".format(chne_values))
                        except sqlite3.Error as error:
                            print_log("DB ERROR")
                            print_log(error)
                            msg.showerror("Внимание", "Произошла ошибка при удалении контакта. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                        finally:
                            if (sqlite_connections):
                                sqlite_connections.close()
                                print_log("DB CLOSE")
                        create_contact(MN)
                        chne_values = [str(x) for x in MN[0]]
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                ch_window.focus()
                new_btn_2.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
            def ch_window_save_event(event):
                global chne_values
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Изменить контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(ch_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        try:
                            sqlite_connections = sqlite3.connect(r'db\db.db')
                            cursor = sqlite_connections.cursor()
                            print_log("DB OPEN")
                            cursor.execute("""DELETE FROM db WHERE ФИО = '{}'
                                                            AND Телефон = '{}'
                                                            AND Почта = '{}'
                                                            AND Компания = '{}'
                                                            AND Должность = '{}'
                                                            AND Город = '{}'
                                                            AND Дата = '{}'
                                                            AND Примечание = '{}'""".format(chne_values[0],
                                                                                            chne_values[1],
                                                                                            chne_values[2],
                                                                                            chne_values[3],
                                                                                            chne_values[4],
                                                                                            chne_values[5],
                                                                                            chne_values[6],
                                                                                            chne_values[7]))
                            sqlite_connections.commit()
                            cursor.close()
                            show()
                            tree_shower()
                            print_log("Контакты {} удалены из базы".format(chne_values))
                        except sqlite3.Error as error:
                            print_log("DB ERROR")
                            print_log(error)
                            msg.showerror("Внимание", "Произошла ошибка при удалении контакта. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                        finally:
                            if (sqlite_connections):
                                sqlite_connections.close()
                                print_log("DB CLOSE")
                        create_contact(MN)
                        chne_values = [str(x) for x in MN[0]]
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                ch_window.focus()
                new_btn_2.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
                
            def post_company_name_into():
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_company_name_into_event(event):
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_position_name():
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x
            def post_position_name_event(event):
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x

            numer = 1
            while numer <= len(contact_parameters):
                if numer != 4 and numer != 5 and numer != 6 and numer != 7:
                    new_frame = Frame(ch_window)
                    new_frame.pack(fill = X, expand = True)
                    new_label = Label(new_frame, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry = Entry(new_frame, width = 50)
                    new_entry.insert(0, "{}".format(chne_values[numer-1]))
                    new_label.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry.bind("<Return>", ch_window_save_event)
                    numer += 1
                elif numer == 4:
                    new_frame_4 = Frame(ch_window)
                    new_frame_4.pack(fill = X, expand = True)
                    new_label_4 = Label(new_frame_4, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_4 = ttk.Combobox(new_frame_4,
                                               values = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data]))))),
                                             postcommand = post_company_name_into,
                                             width = 50)
                    new_entry_4.set("{}".format(chne_values[numer-1]))
                    new_label_4.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_4.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_4.bind("<<ComboboxSelected>>", post_company_name_into_event)
                    numer += 1
                elif numer == 5:
                    new_frame_5 = Frame(ch_window)
                    new_frame_5.pack(fill = X, expand = True)
                    new_label_5 = Label(new_frame_5, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_5 = ttk.Combobox(new_frame_5,
                                               values = sorted(list(set(list(map(str, [x[4] for x in db_data]))))),
                                             postcommand = post_position_name,
                                             width = 50)
                    new_entry_5.set("{}".format(chne_values[numer-1]))
                    new_label_5.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_5.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_5.bind("<<ComboboxSelected>>", post_position_name_event)
                    numer += 1
                elif numer == 6:
                    new_frame_1 = Frame(ch_window)
                    new_frame_1.pack(fill = X, expand = True)
                    new_label_1 = Label(new_frame_1, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_1 = ttk.Combobox(new_frame_1, values = town_lst,
                                             postcommand = post_town_lst,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_1.set("{}".format(chne_values[numer-1]))
                    new_label_1.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.pack(side = LEFT, fill = BOTH, expand = True)
                    new_label_22 = Label(new_frame_1, text = "{}".format(town_selected_not_event()),
                                        width = 10, bg = 'lightgreen')
                    new_label_22.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.bind("<<ComboboxSelected>>", town_selected)
                    numer += 1
                elif numer == 7:
                    new_frame_2 = Frame(ch_window)
                    new_frame_2.pack(fill = X, expand = True)
                    new_label_2 = Label(new_frame_2, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    def new_lambda_eval_postcommand():
                        new_entry_2['values']=[time_str()]
                    new_entry_2 = ttk.Combobox(new_frame_2,
                                             postcommand = new_lambda_eval_postcommand,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_2.set("{}".format(chne_values[numer-1]))
                    new_label_2.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_2.pack(side = LEFT, fill = BOTH, expand = True)
                    numer += 1
                
            new_frame_2 = Frame(ch_window)
            new_frame_2.pack(fill = X, expand = True)
            new_btn_1 = Button(new_frame_2, text = "Сохранить", command = ch_window_save)
            new_btn_2 = Button(new_frame_2, text = "Закрыть", command = ch_window_quit)
            new_btn_1.pack(side = LEFT, fill = X, expand = True)
            new_btn_2.pack(side = LEFT, fill = X, expand = True)
            new_btn_2.focus()
            ch_window.bind("<Button-3>", ch_popup)
            ch_window.bind("<FocusIn>", ch_popupFocusOut)
            ch_window.bind("<Control-C>", ch_copy_selection)
            ch_window.bind("<Control-V>", ch_paste_cl)
            def ch_window_key_callback(event):
                if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                    if chr(event.keycode) == "C":
                        ch_copy_selection()
                    elif chr(event.keycode) == "V":
                        ch_paste_cl()
            ch_window.bind("<Key>", ch_window_key_callback)
            new_btn_2.bind("<Return>", ch_window_quit_event)
        else:
            msg.showerror("Внимание", "Выберите данные для изменения")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")

#Функция создать копию и изменить
def copy_db(event):
    try:
        values = file_cabinet.item(file_cabinet.selection(), option="values")
        if values != "":
            copy_window = Toplevel()
            copy_window.title("Добавить контакт")
            copy_window.resizable(False, False)
            copy_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))

            #Создание функций вызова контекстного меню
            def copy_popup(event):
                global x, y
                x = event.x
                y = event.y
                copy_menu.post(event.x_root, event.y_root)

            def copy_popupFocusOut(event):
                copy_menu.unpost()
                
            def copy_copy_selection():
                try:
                    copy_window.clipboard_clear()
                    copy_window.clipboard_append(copy_window.focus_get().selection_get())
                except :
                    return
                    
            def copy_paste_cl():
                try:
                    copy_window.focus_get().insert(INSERT, copy_window.clipboard_get())
                except :
                    return
            
            copy_menu = Menu(tearoff = False)
            copy_menu.add_command(label = "Копировать", command = copy_copy_selection)
            copy_menu.add_command(label = "Вставить", command = copy_paste_cl)

            def copy_window_quit():
                copy_window.destroy()
            
            def post_town_lst():
                new_entry_1['values'] = town_lst
            def town_selected(event):
                town_name = new_entry_1.get()
                tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                if town_lst_format  == "UTC":
                    tz_hour += 3
                elif town_lst_format == "YEKT":
                    tz_hour -= 2
                if tz_hour >= 0:
                    tz_hour = "+"+str(tz_hour)
                new_label_22.config(text = "{}, {}".format(town_lst_format, tz_hour))
            def town_selected_not_event():
                town_name = new_entry_1.get()
                if town_name in town_lst:
                    tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                    if town_lst_format  == "UTC":
                        tz_hour += 3
                    elif town_lst_format == "YEKT":
                        tz_hour -= 2
                    if tz_hour >= 0:
                        tz_hour = "+"+str(tz_hour)
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                else:
                    tz_hour = "???"
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                return new_label_2_txt

            #Создание функции, считывающей в список текст из полей ввода
            def copy_window_save():
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Записать новый контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(copy_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        create_contact(MN)
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                copy_window.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
                new_entry_2.set("{}".format(time_str()))
            def copy_window_save_event(event):
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Записать новый контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(copy_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        create_contact(MN)
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                copy_window.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
                new_entry_2.set("{}".format(time_str()))
                
            def post_company_name_into():
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_company_name_into_event(event):
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_position_name():
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x
            def post_position_name_event(event):
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x

            numer = 1
            while numer <= len(contact_parameters):
                if numer != 4 and numer != 5 and numer != 6 and numer != 7:
                    new_frame = Frame(copy_window)
                    new_frame.pack(fill = X, expand = True)
                    new_label = Label(new_frame, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry = Entry(new_frame, width = 50)
                    new_entry.insert(0, "{}".format(values[numer-1]))
                    new_label.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry.bind("<Return>", copy_window_save_event)
                    numer += 1
                elif numer == 4:
                    new_frame_4 = Frame(copy_window)
                    new_frame_4.pack(fill = X, expand = True)
                    new_label_4 = Label(new_frame_4, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_4 = ttk.Combobox(new_frame_4,
                                               values = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data]))))),
                                             postcommand = post_company_name_into,
                                             width = 50)
                    new_entry_4.set("{}".format(values[numer-1]))
                    new_label_4.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_4.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_4.bind("<<ComboboxSelected>>", post_company_name_into_event)
                    numer += 1
                elif numer == 5:
                    new_frame_5 = Frame(copy_window)
                    new_frame_5.pack(fill = X, expand = True)
                    new_label_5 = Label(new_frame_5, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_5 = ttk.Combobox(new_frame_5,
                                               values = sorted(list(set(list(map(str, [x[4] for x in db_data]))))),
                                             postcommand = post_position_name,
                                             width = 50)
                    new_entry_5.set("{}".format(values[numer-1]))
                    new_label_5.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_5.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_5.bind("<<ComboboxSelected>>", post_position_name_event)
                    numer += 1
                elif numer == 6:
                    new_frame_1 = Frame(copy_window)
                    new_frame_1.pack(fill = X, expand = True)
                    new_label_1 = Label(new_frame_1, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_1 = ttk.Combobox(new_frame_1, values = town_lst,
                                             postcommand = post_town_lst,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_1.set("{}".format(values[numer-1]))
                    new_label_1.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.pack(side = LEFT, fill = BOTH, expand = True)
                    new_label_22 = Label(new_frame_1, text = "{}".format(town_selected_not_event()),
                                        width = 10, bg = 'lightgreen')
                    new_label_22.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.bind("<<ComboboxSelected>>", town_selected)
                    numer += 1
                elif numer == 7:
                    new_frame_2 = Frame(copy_window)
                    new_frame_2.pack(fill = X, expand = True)
                    new_label_2 = Label(new_frame_2, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    def new_lambda_eval_postcommand():
                        new_entry_2['values']=[time_str()]
                    new_entry_2 = ttk.Combobox(new_frame_2,
                                             postcommand = new_lambda_eval_postcommand,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_2.set("{}".format(time_str()))
                    new_label_2.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_2.pack(side = LEFT, fill = BOTH, expand = True)
                    numer += 1
            new_frame_2 = Frame(copy_window)
            new_frame_2.pack(fill = X, expand = True)
            new_btn_1 = Button(new_frame_2, text = "Сохранить", command = copy_window_save)
            new_btn_1.pack(side = LEFT, fill = X, expand = True)
            new_btn_2 = Button(new_frame_2, text = "Закрыть", command = copy_window_quit)
            new_btn_2.pack(side = LEFT, fill = X, expand = True)
            copy_window.bind("<Button-3>", copy_popup)
            copy_window.bind("<FocusIn>", copy_popupFocusOut)
            copy_window.bind("<Control-C>", copy_copy_selection)
            copy_window.bind("<Control-V>", copy_paste_cl)
            def copy_window_key_callback(event):
                if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                    if chr(event.keycode) == "C":
                        copy_copy_selection()
                    elif chr(event.keycode) == "V":
                        copy_paste_cl()
            copy_window.bind("<Key>", copy_window_key_callback)
        else:
            msg.showerror("Внимание", "Выберите данные для редактирования")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")
def copy_db_not_event():
    try:
        values = file_cabinet.item(file_cabinet.selection(), option="values")
        if values != "":
            copy_window = Toplevel()
            copy_window.title("Добавить контакт")
            copy_window.resizable(False, False)
            copy_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))

            #Создание функций вызова контекстного меню
            def copy_popup(event):
                global x, y
                x = event.x
                y = event.y
                copy_menu.post(event.x_root, event.y_root)

            def copy_popupFocusOut(event):
                copy_menu.unpost()
                
            def copy_copy_selection():
                try:
                    copy_window.clipboard_clear()
                    copy_window.clipboard_append(copy_window.focus_get().selection_get())
                except :
                    return
                    
            def copy_paste_cl():
                try:
                    copy_window.focus_get().insert(INSERT, copy_window.clipboard_get())
                except :
                    return
            
            copy_menu = Menu(tearoff = False)
            copy_menu.add_command(label = "Копировать", command = copy_copy_selection)
            copy_menu.add_command(label = "Вставить", command = copy_paste_cl)

            def copy_window_quit():
                copy_window.destroy()
            
            def post_town_lst():
                new_entry_1['values'] = town_lst
            def town_selected(event):
                town_name = new_entry_1.get()
                tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                if town_lst_format  == "UTC":
                    tz_hour += 3
                elif town_lst_format == "YEKT":
                    tz_hour -= 2
                if tz_hour >= 0:
                    tz_hour = "+"+str(tz_hour)
                new_label_22.config(text = "{}, {}".format(town_lst_format, tz_hour))
            def town_selected_not_event():
                town_name = new_entry_1.get()
                if town_name in town_lst:
                    tz_hour = int(tz_lst[town_lst.index(town_name)][:-1])
                    if town_lst_format  == "UTC":
                        tz_hour += 3
                    elif town_lst_format == "YEKT":
                        tz_hour -= 2
                    if tz_hour >= 0:
                        tz_hour = "+"+str(tz_hour)
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                else:
                    tz_hour = "???"
                    new_label_2_txt = "{}, {}".format(town_lst_format, tz_hour)
                return new_label_2_txt

            #Создание функции, считывающей в список текст из полей ввода
            def copy_window_save():
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Записать новый контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(copy_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        create_contact(MN)
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                copy_window.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
                new_entry_2.set("{}".format(time_str()))
            def copy_window_save_event(event):
                new_btn_1.configure(state = "disable")
                new_btn_2.configure(state = "disable")
                if msg.askyesno(title = "Внимание", message = "Записать новый контакт?"):
                    n = 0
                    N=[]
                    while n <= len(contact_parameters)-1:
                        N.append(list(list(copy_window.children.values())[n].children.values())[1])
                        n += 1
                    M=[]
                    for entr in N:
                        if entr.get() != "":
                            M.append(entr.get().replace("\'", ""))
                        else:
                            M.append("-")
                    MN = [tuple(M)]
                    if trash("".join(M).replace("+", "")) != "":
                        create_contact(MN)
                        show()
                        tree_shower()
                    else:
                        msg.showinfo("Внимание", "Введите данные для сохранения")
                copy_window.focus()
                new_btn_1.configure(state = "normal")
                new_btn_2.configure(state = "normal")
                new_entry_2.set("{}".format(time_str()))
                
            def post_company_name_into():
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_company_name_into_event(event):
                x = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))
                new_entry_4['values'] = x
                return x
            def post_position_name():
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x
            def post_position_name_event(event):
                x = sorted(list(set(list(map(str, [x[4] for x in db_data])))))
                new_entry_5['values'] = x
                return x

            numer = 1
            while numer <= len(contact_parameters):
                if numer != 4 and numer != 5 and numer != 6 and numer != 7:
                    new_frame = Frame(copy_window)
                    new_frame.pack(fill = X, expand = True)
                    new_label = Label(new_frame, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry = Entry(new_frame, width = 50)
                    new_entry.insert(0, "{}".format(values[numer-1]))
                    new_label.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry.bind("<Return>", copy_window_save_event)
                    numer += 1
                elif numer == 4:
                    new_frame_4 = Frame(copy_window)
                    new_frame_4.pack(fill = X, expand = True)
                    new_label_4 = Label(new_frame_4, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_4 = ttk.Combobox(new_frame_4,
                                               values = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data]))))),
                                             postcommand = post_company_name_into,
                                             width = 50)
                    new_entry_4.set("{}".format(values[numer-1]))
                    new_label_4.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_4.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_4.bind("<<ComboboxSelected>>", post_company_name_into_event)
                    numer += 1
                elif numer == 5:
                    new_frame_5 = Frame(copy_window)
                    new_frame_5.pack(fill = X, expand = True)
                    new_label_5 = Label(new_frame_5, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_5 = ttk.Combobox(new_frame_5,
                                               values = sorted(list(set(list(map(str, [x[4] for x in db_data]))))),
                                             postcommand = post_position_name,
                                             width = 50)
                    new_entry_5.set("{}".format(values[numer-1]))
                    new_label_5.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_5.pack(side = LEFT, fill = BOTH, expand = True)
                    new_entry_5.bind("<<ComboboxSelected>>", post_position_name_event)
                    numer += 1
                elif numer == 6:
                    new_frame_1 = Frame(copy_window)
                    new_frame_1.pack(fill = X, expand = True)
                    new_label_1 = Label(new_frame_1, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    new_entry_1 = ttk.Combobox(new_frame_1, values = town_lst,
                                             postcommand = post_town_lst,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_1.set("{}".format(values[numer-1]))
                    new_label_1.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.pack(side = LEFT, fill = BOTH, expand = True)
                    new_label_22 = Label(new_frame_1, text = "{}".format(town_selected_not_event()),
                                        width = 10, bg = 'lightgreen')
                    new_label_22.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_1.bind("<<ComboboxSelected>>", town_selected)
                    numer += 1
                elif numer == 7:
                    new_frame_2 = Frame(copy_window)
                    new_frame_2.pack(fill = X, expand = True)
                    new_label_2 = Label(new_frame_2, text = "{}:".format(str(contact_parameters[numer-1])), width = 20)
                    def new_lambda_eval_postcommand():
                        new_entry_2['values']=[time_str()]
                    new_entry_2 = ttk.Combobox(new_frame_2,
                                             postcommand = new_lambda_eval_postcommand,
                                             width = 50,
                                             state = 'readonly')
                    new_entry_2.set("{}".format(time_str()))
                    new_label_2.pack(side = LEFT, fill = BOTH, expand = False)
                    new_entry_2.pack(side = LEFT, fill = BOTH, expand = True)
                    numer += 1

            new_frame_2 = Frame(copy_window)
            new_frame_2.pack(fill = X, expand = True)
            new_btn_1 = Button(new_frame_2, text = "Сохранить", command = copy_window_save)
            new_btn_1.pack(side = LEFT, fill = X, expand = True)
            new_btn_2 = Button(new_frame_2, text = "Закрыть", command = copy_window_quit)
            new_btn_2.pack(side = LEFT, fill = X, expand = True)
            copy_window.bind("<Button-3>", copy_popup)
            copy_window.bind("<FocusIn>", copy_popupFocusOut)
            copy_window.bind("<Control-C>", copy_copy_selection)
            copy_window.bind("<Control-V>", copy_paste_cl)
            def copy_window_key_callback(event):
                if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                    if chr(event.keycode) == "C":
                        copy_copy_selection()
                    elif chr(event.keycode) == "V":
                        copy_paste_cl()
            copy_window.bind("<Key>", copy_window_key_callback)
        else:
            msg.showerror("Внимание", "Выберите данные для редактирования")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")

#Функция отображения Картотеки
def tree_show(event):
    file_cabinet.delete(*file_cabinet.get_children())
    file_cabinet['columns']=contact_parameters
    for header in contact_parameters:
        file_cabinet.heading(header, text = header, anchor = 'w')
        file_cabinet.column('{}'.format(header), width = 200, stretch = True, minwidth = 200)
    a = find_db()
    b = filter_list()
    show = []
    for item in a:
        if item in show:
            continue
        for jtem in b:
            if item == jtem:
                show.append(item)
    A = []
    index_filter = contact_parameters.index(combo_filter.get())
    for i in show:
        i = list(i)
        u = [i[index_filter]]
        i.pop(index_filter)
        i = u + i
        if index_filter == 6:
            i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
        A.append(i)
    A_Z = AZ_filter.get()
    if A_Z == "А-Я":
        A = sorted(A)
        if index_filter == 6:
            B = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                B.append(i)
            for i in B:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = B
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = A
    else:
        A = sorted(A, reverse = True)
        if index_filter == 6:
            C = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                C.append(i)
            for i in C:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = C
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = A
    counter = 1
    for row in show:
        file_cabinet.insert(
                parent = '',
                index = 'end',
                text = '{}'.format(counter),
                values = row,
                tag = '{}'.format(counter%2)
                )
        counter += 1
    counter_lbl.configure(text = "Контакты: {}".format(len(show)))
def tree_shower():
    file_cabinet.delete(*file_cabinet.get_children())
    file_cabinet['columns']=contact_parameters
    for header in contact_parameters:
        file_cabinet.heading(header, text = header, anchor = 'w')
        file_cabinet.column('{}'.format(header), width = 200, stretch = True, minwidth = 200)
    a = find_db()
    b = filter_list()
    show = []
    for item in a:
        if item in show:
            continue
        for jtem in b:
            if item == jtem:
                show.append(item)
    A = []
    index_filter = contact_parameters.index(combo_filter.get())
    for i in show:
        i = list(i)
        u = [i[index_filter]]
        i.pop(index_filter)
        i = u + i
        if index_filter == 6:
            i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
        A.append(i)
    A_Z = AZ_filter.get()
    if A_Z == "А-Я":
        A = sorted(A)
        if index_filter == 6:
            B = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                B.append(i)
            for i in B:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = B
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = A
    else:
        A = sorted(A, reverse = True)
        if index_filter == 6:
            C = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                C.append(i)
            for i in C:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = C
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            show = A
    counter = 1
    for row in show:
        file_cabinet.insert(
                parent = '',
                index = 'end',
                text = '{}'.format(counter),
                values = row,
                tag = '{}'.format(counter%2)
                )
        counter += 1
    counter_lbl.configure(text = "Контакты: {}".format(len(show)))

#Функция отображения Сделок
def trans_tree_show(event):
    transactions.delete(*transactions.get_children())
    transactions['columns']=["Название сделки", "Компания",
                             "Дата создания","Обязательства по сделке"]
    for header in ["Название сделки", "Компания",
                             "Дата создания","Обязательства по сделке"]:
        transactions.heading(header, text = header, anchor = 'w')
        if header == "Обязательства по сделке":
            transactions.column('{}'.format(header), width = 1500, stretch = True, minwidth = 1500)
        else:
            transactions.column('{}'.format(header), width = 200, stretch = True, minwidth = 200)
    a = trans_find_db()
    b = trans_filter_list()
    trans_data = []
    for item in a:
        if item in trans_data:
            continue
        for jtem in b:
            if item == jtem:
                trans_data.append(item)
    trans_green_save_tasks = []
    trans_red_save_tasks = []
    trans_grey_save_tasks = []
    for row in trans_data:
        if row[4] == "":
            identy = ['nothing']
        else:
            identy = [x.split(", ")[2][1:-1] for x in row[4][1:-1].split("), (")]
        time_identy = [x.split(", ")[0][1:-1] for x in row[4][1:-1].split("), (")]
        I = []
        for i in identy:
            if i == 'nothing':
                I.append("grey")
            elif i == '':
                if time_str_replace(time_identy[identy.index(i)]) >= time_str_reverse():
                    I.append("green")
                else:
                    I.append("red")
            elif i != '':
                I.append("grey")
        if 'red' in I:
            trans_red_save_tasks.append(row)
        else:
            if 'green' in I:
                trans_green_save_tasks.append(row)
            else:
                trans_grey_save_tasks.append(row)
    trans_data = []
    if green_radio_btn.state() == ('alternate',) or green_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or green_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or green_radio_btn.state() == ('selected',) or green_radio_btn.state() == ('selected', 'alternate') or green_radio_btn.state() == ('focus', 'alternate') or green_radio_btn.state() == ('focus', 'selected', 'alternate'):
        trans_data = trans_data + trans_green_save_tasks
    if red_radio_btn.state() == ('alternate',) or red_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or red_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or red_radio_btn.state() == ('selected',) or red_radio_btn.state() == ('selected', 'alternate') or red_radio_btn.state() == ('focus', 'alternate') or red_radio_btn.state() == ('focus', 'selected', 'alternate'):
        trans_data = trans_data + trans_red_save_tasks
    if grey_radio_btn.state() == ('alternate',) or grey_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or grey_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or grey_radio_btn.state() == ('selected',) or grey_radio_btn.state() == ('selected', 'alternate') or grey_radio_btn.state() == ('focus', 'alternate') or grey_radio_btn.state() == ('focus', 'selected', 'alternate'):
        trans_data = trans_data + trans_grey_save_tasks
    A = []
    index_filter = ["Название сделки", "Компания", "Дата создания", "Обязательства по сделке"].index(trans_combo_filter.get())
    for i in trans_data:
        i = list(i)
        u = [i[index_filter]]
        i.pop(index_filter)
        i = u + i
        if index_filter == 2:
            i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
        A.append(i)
    A_Z = trans_AZ_filter.get()
    if A_Z == "А-Я":
        A = sorted(A)
        if index_filter == 2:
            B = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                B.append(i)
            for i in B:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = B
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = A
    else:
        A = sorted(A, reverse = True)
        if index_filter == 2:
            C = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                C.append(i)
            for i in C:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = C
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = A
    for row in trans_data:
        if row[4] == "":
            identy = ['nothing']
        else:
            identy = [x.split(", ")[2][1:-1] for x in row[4][1:-1].split("), (")]
        time_identy = [x.split(", ")[0][1:-1] for x in row[4][1:-1].split("), (")]
        I = []
        for i in identy:
            if i == 'nothing':
                I.append("grey")
            elif i == '':
                if time_str_replace(time_identy[identy.index(i)]) >= time_str_reverse():
                    I.append("green")
                else:
                    I.append("red")
            elif i != '':
                I.append("grey")
        if 'red' in I:
            tag_row = 'red'
        else:
            if 'green' in I:
                tag_row = "green"
            else:
                tag_row = "grey"
        transactions.insert(
                parent = '',
                index = 'end',
                values = row[0:4],
                tag = '{}'.format(tag_row)
                )
    trans_lbl.configure(text = "Сделки: {}".format(len(trans_data)))
    tasks_lbl.configure(text = "Задачи: ")
def trans_tree_shower():
    transactions.delete(*transactions.get_children())
    transactions['columns']=["Название сделки", "Компания",
                             "Дата создания","Обязательства по сделке"]
    for header in ["Название сделки", "Компания",
                             "Дата создания","Обязательства по сделке"]:
        transactions.heading(header, text = header, anchor = 'w')
        if header == "Обязательства по сделке":
            transactions.column('{}'.format(header), width = 500, stretch = True, minwidth = 200)
        else:
            transactions.column('{}'.format(header), width = 200, stretch = True, minwidth = 200)
    a = trans_find_db()
    b = trans_filter_list()
    trans_data = []
    for item in a:
        if item in trans_data:
            continue
        for jtem in b:
            if item == jtem:
                trans_data.append(item)
    trans_green_save_tasks = []
    trans_red_save_tasks = []
    trans_grey_save_tasks = []
    for row in trans_data:
        if row[4] == "":
            identy = ['nothing']
        else:
            identy = [x.split(", ")[2][1:-1] for x in row[4][1:-1].split("), (")]
        time_identy = [x.split(", ")[0][1:-1] for x in row[4][1:-1].split("), (")]
        I = []
        for i in identy:
            if i == 'nothing':
                I.append("grey")
            elif i == '':
                if time_str_replace(time_identy[identy.index(i)]) >= time_str_reverse():
                    I.append("green")
                else:
                    I.append("red")
            elif i != '':
                I.append("grey")
        if 'red' in I:
            trans_red_save_tasks.append(row)
        else:
            if 'green' in I:
                trans_green_save_tasks.append(row)
            else:
                trans_grey_save_tasks.append(row)
    trans_data = []
    if green_radio_btn.state() == ('alternate',) or green_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or green_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or green_radio_btn.state() == ('selected',) or green_radio_btn.state() == ('selected', 'alternate') or green_radio_btn.state() == ('focus', 'alternate') or green_radio_btn.state() == ('focus', 'selected', 'alternate'):
        trans_data = trans_data + trans_green_save_tasks
    if red_radio_btn.state() == ('alternate',) or red_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or red_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or red_radio_btn.state() == ('selected',) or red_radio_btn.state() == ('selected', 'alternate') or red_radio_btn.state() == ('focus', 'alternate') or red_radio_btn.state() == ('focus', 'selected', 'alternate'):
        trans_data = trans_data + trans_red_save_tasks
    if grey_radio_btn.state() == ('alternate',) or grey_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or grey_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or grey_radio_btn.state() == ('selected',) or grey_radio_btn.state() == ('selected', 'alternate') or grey_radio_btn.state() == ('focus', 'alternate') or grey_radio_btn.state() == ('focus', 'selected', 'alternate'):
        trans_data = trans_data + trans_grey_save_tasks
    A = []
    index_filter = ["Название сделки", "Компания", "Дата создания", "Обязательства по сделке"].index(trans_combo_filter.get())
    for i in trans_data:
        i = list(i)
        u = [i[index_filter]]
        i.pop(index_filter)
        i = u + i
        if index_filter == 2:
            i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
        A.append(i)
    A_Z = trans_AZ_filter.get()
    if A_Z == "А-Я":
        A = sorted(A)
        if index_filter == 2:
            B = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                B.append(i)
            for i in B:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = B
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = A
    else:
        A = sorted(A, reverse = True)
        if index_filter == 2:
            C = []
            for i in A:
                i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                C.append(i)
            for i in C:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = C
        else:
            for i in A:
                i_index_null = i[0]
                i.pop(0)
                i.insert(index_filter, i_index_null)
            trans_data = A
    for row in trans_data:
        if row[4] == "":
            identy = ['nothing']
        else:
            identy = [x.split(", ")[2][1:-1] for x in row[4][1:-1].split("), (")]
        time_identy = [x.split(", ")[0][1:-1] for x in row[4][1:-1].split("), (")]
        I = []
        for i in identy:
            if i == 'nothing':
                I.append("grey")
            elif i == '':
                if time_str_replace(time_identy[identy.index(i)]) >= time_str_reverse():
                    I.append("green")
                else:
                    I.append("red")
            elif i != '':
                I.append("grey")
        if 'red' in I:
            tag_row = 'red'
        else:
            if 'green' in I:
                tag_row = "green"
            else:
                tag_row = "grey"
        transactions.insert(
                parent = '',
                index = 'end',
                values = row[0:4],
                tag = '{}'.format(tag_row)
                )
    trans_lbl.configure(text = "Сделки: {}".format(len(trans_data)))
    tasks_lbl.configure(text = "Задачи: ")

#Функция очистки области поиска Картотека
def clear_find_str(event):
    find_str.delete(0, END)
    combo_filter.current(0)
    combo_combo_filter.set('')
    AZ_filter.current(0)
    find_str.focus()
#Функция очистки области поиска Сделки
def trans_clear_find_str(event):
    trans_find_str.delete(0, END)
    trans_combo_filter.current(0)
    trans_combo_combo_filter.set('')
    trans_AZ_filter.current(0)
    green_radio_btn.state(['alternate'])
    red_radio_btn.state(['alternate'])
    grey_radio_btn.state(['alternate'])
    trans_name.set("")
    company_name.set("")
    data_name.set("{}".format(time_str()))
    commitments_name.delete(1.0, END)
    trans_find_str.focus()

#Создание функции выхода из программы
def root_quit():
    if msg.askyesno(title = "Внимание", message = "Выйти из программы?"):
        root.quit()
        root.destroy()
        exit()
def root_quit_event(event):
    if msg.askyesno(title = "Внимание", message = "Выйти из программы?"):
        root.quit()
        root.destroy()
        exit()

#Функция фильтра Картотека
def filter_list():
    filter_spisok = []
    sps = [x[contact_parameters.index(combo_filter.get())] for x in db_data]
    if combo_combo_filter.get() == "":
        filter_spisok = db_data
    else:
        ch = 0
        while ch+1 <= len(sps):
            if sps[ch] == combo_combo_filter.get():
                filter_spisok.append(db_data[ch])
            ch += 1
    return filter_spisok
#Функция фильтра Сделки
def trans_filter_list():
    trans_filter_spisok = []
    trans_sps = [x[["Название сделки", "Компания", "Дата создания", "Обязательства по сделке"].index(trans_combo_filter.get())] for x in trans_data]
    if trans_combo_combo_filter.get() == "":
        trans_filter_spisok = trans_data
    else:
        trans_ch = 0
        while trans_ch+1 <= len(trans_sps):
            if trans_sps[trans_ch] == trans_combo_combo_filter.get():
                trans_filter_spisok.append(trans_data[trans_ch])
            trans_ch += 1
    return trans_filter_spisok

#ФУНКЦИИ ДЛЯ ВКЛАДКИ СДЕЛКИ
#Функция отображения сделки
def trans_view(event):
    try:
        values = transactions.item(transactions.selection(), option="values")
        trans_name.set("{}".format(values[0]))
        company_name.set("{}".format(values[1]))
        data_name.set("{}".format(values[2]))
        commitments_name.delete(1.0, END)
        commitments_name.insert(END, "{}".format(values[3]))
        for i in trans_data:
            if i[0] == values[0] and i[1] == values[1] and i[2] == values[2] and i[3] == values[3]:
                save_tasks_str = i[4]
        save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
        if save_tasks == [['']]:
            save_tasks = []
        tasks_lbl.configure(text = "Задачи: {}".format(len(save_tasks)))
    except TclError:
        trans_name.set("")
        company_name.set("")
        data_name.set("")
        commitments_name.delete(1.0, END)
        valueses = [transactions.item(x, option="values") for x in transactions.selection()]
        save_tasks = []
        for values in valueses:
            for i in trans_data:
                if i[0] == values[0] and i[1] == values[1] and i[2] == values[2] and i[3] == values[3]:
                    save_tasks_str = i[4]
            A = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
            if A == [['']]:
                A = []
            save_tasks += A
        tasks_lbl.configure(text = "Задачи: {}".format(len(save_tasks)))
def trans_view_not_event():
    try:
        values = transactions.item(transactions.selection(), option="values")
        trans_name.set("{}".format(values[0]))
        company_name.set("{}".format(values[1]))
        data_name.set("{}".format(values[2]))
        commitments_name.delete(1.0, END)
        commitments_name.insert(END, "{}".format(values[3]))
        for i in trans_data:
            if i[0] == values[0] and i[1] == values[1] and i[2] == values[2] and i[3] == values[3]:
                save_tasks_str = i[4]
        save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
        if save_tasks == [['']]:
            save_tasks = []
        tasks_lbl.configure(text = "Задачи: {}".format(len(save_tasks)))
    except TclError:
        trans_name.set("")
        company_name.set("")
        data_name.set("")
        commitments_name.delete(1.0, END)
        valueses = [transactions.item(x, option="values") for x in transactions.selection()]
        save_tasks = []
        for values in valueses:
            for i in trans_data:
                if i[0] == values[0] and i[1] == values[1] and i[2] == values[2] and i[3] == values[3]:
                    save_tasks_str = i[4]
            A = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
            if A == [['']]:
                A = []
            save_tasks += A
        tasks_lbl.configure(text = "Задачи: {}".format(len(save_tasks)))

def post_date_name():
    #Назначаем значения внутри еще нераскрытого списка на основании отсортированного списка значений для предыдущей выбранной колонки
    data_name['values'] = [time_str()]

def post_trans_name():
    #Назначаем значения внутри еще нераскрытого списка на основании отсортированного списка значений для предыдущей выбранной колонки
    trans_name['values'] = sorted(list(set(list(map(str, [x[0] for x in trans_data])))))
def post_company_name():
    company_name['values'] = sorted(list(set(list(map(str, [x[3] for x in db_data]+[x[1] for x in trans_data])))))

#Функция записи в базу сделок (нужно добавлять список кортежей)
def trans_create_contact(trans_name, company_name, data_name,
                         commitments, tasks):
    try:
        sqlite_connections = sqlite3.connect(r'db\db.db')
        cursor = sqlite_connections.cursor()
        print_log("DB OPEN")
        sqlite_insert_query = """INSERT INTO trans(Сделка, Компания, Дата, Обязательства, Задачи)VALUES (?, ?, ?, ?, ?)"""
        data_tuple = (trans_name, company_name, data_name,
                         commitments, tasks)
        cursor.execute(sqlite_insert_query, data_tuple)
        sqlite_connections.commit()
        cursor.close()
        print_log("Сделка '{}' внесена в базу".format(trans_name))
    except sqlite3.Error as error:
        print_log("DB ERROR")
        print_log(error)
        msg.showerror("Внимание", "Произошла ошибка при добавлении сделки. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
    finally:
        if (sqlite_connections):
            sqlite_connections.close()
            print_log("DB CLOSE")    

def add_trans_click():
    new_trans_name = trans_name.get().replace("\'", "")
    new_company_name = company_name.get().replace("\'", "")
    new_data_name = data_name.get()
    new_commitments_name = commitments_name.get(1.0, END).replace("\n", " ").replace("\'", "")
    new_document_name = new_data_name.replace(" ", "").replace(".", "").replace(":", "") + new_trans_name + new_company_name
    if new_document_name == '':
        msg.showinfo("Внимание", "Введите недостающие данные!")
    else:
        if msg.askyesno("Внимание", "Добавить новую сделку '{}' в базу?".format(new_trans_name)):
            os.chdir("db")
            os.chdir("trans")
            if new_document_name not in os.listdir():
                os.chdir("..")
                os.chdir("..")
                trans_create_contact(new_trans_name, new_company_name, new_data_name,
                             new_commitments_name, "")
                os.chdir("db")
                os.chdir("trans")
                os.mkdir("{}".format(new_document_name))
                os.chdir("..")
                os.chdir("..")
                show()
                trans_tree_shower()
            else:
                msg.showinfo("Внимание", "Такая сделка уже существует!")
                os.chdir("..")
                os.chdir("..")
    data_name.set("{}".format(time_str()))
    
#Функция удаления сделки
def trans_delete_contact():
    valueses = [transactions.item(x, option="values") for x in transactions.selection()]
    if valueses != []:
        if msg.askyesno(title = "Внимание",
                        message = "Удалить выбранные сделки вместе с задачами и прикрепленными документами?"):
            for values in valueses:
                save_document_name = values[2].replace(" ", "").replace(".", "").replace(":", "") + values[0] + values[1]
                try:
                    sqlite_connections = sqlite3.connect(r'db\db.db')
                    cursor = sqlite_connections.cursor()
                    print_log("DB OPEN")
                    cursor.execute("""DELETE FROM trans WHERE Сделка = '{}'
                                                    AND Компания = '{}'
                                                    AND Дата = '{}'
                                                    AND Обязательства = '{}'""".format(values[0],
                                                                                    values[1],
                                                                                    values[2],
                                                                                    values[3]))
                    sqlite_connections.commit()
                    cursor.close()
                    show()
                    trans_tree_shower()
                    print_log("Сделка {} удалена из базы".format(values))

                    os.chdir("db")
                    os.chdir("trans")
                    now_time = time_str().replace(" ", "").replace(".", "").replace(":","")
                    os.mkdir("delete{}".format(now_time))
                    os.chdir("delete{}".format(now_time))
                    path_name = os.getcwd()
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    os.chdir("{}".format(save_document_name))
                    for i in os.listdir():
                        os.replace("{}".format(i), "{}/{}".format(path_name, i))
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    shutil.rmtree("{}".format(save_document_name), ignore_errors = True)
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    shutil.rmtree("delete{}".format(now_time),
                                  ignore_errors = True)
                    os.chdir("..")
                    os.chdir("..")

                    trans_name.set("")
                    company_name.set("")
                    data_name.set("")
                    commitments_name.delete(1.0, END)
                except sqlite3.Error as error:
                    print_log("DB ERROR")
                    print_log(error)
                    msg.showerror("Внимание", "Произошла ошибка при удалении сделки. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                finally:
                    if (sqlite_connections):
                        sqlite_connections.close()
                        print_log("DB CLOSE")
    else:
        msg.showerror("Внимание", "Выберите данные для удаления")
    trans_name.set("")
    company_name.set("")
    data_name.set("{}".format(time_str()))
    commitments_name.delete(1.0, END)

def trans_delete_contact_event(event):
    valueses = [transactions.item(x, option="values") for x in transactions.selection()]
    if valueses != []:
        if msg.askyesno(title = "Внимание",
                        message = "Удалить выбранные сделки вместе с задачами и прикрепленными документами?"):
            for values in valueses:
                save_document_name = values[2].replace(" ", "").replace(".", "").replace(":", "") + values[0] + values[1]
                try:
                    sqlite_connections = sqlite3.connect(r'db\db.db')
                    cursor = sqlite_connections.cursor()
                    print_log("DB OPEN")
                    cursor.execute("""DELETE FROM trans WHERE Сделка = '{}'
                                                    AND Компания = '{}'
                                                    AND Дата = '{}'
                                                    AND Обязательства = '{}'""".format(values[0],
                                                                                    values[1],
                                                                                    values[2],
                                                                                    values[3]))
                    sqlite_connections.commit()
                    cursor.close()
                    show()
                    trans_tree_shower()
                    print_log("Сделка {} удалена из базы".format(values))

                    os.chdir("db")
                    os.chdir("trans")
                    now_time = time_str().replace(" ", "").replace(".", "").replace(":","")
                    os.mkdir("delete{}".format(now_time))
                    os.chdir("delete{}".format(now_time))
                    path_name = os.getcwd()
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    os.chdir("{}".format(save_document_name))
                    for i in os.listdir():
                        os.replace("{}".format(i), "{}/{}".format(path_name, i))
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    shutil.rmtree("{}".format(save_document_name), ignore_errors = True)
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    shutil.rmtree("delete{}".format(now_time),
                                  ignore_errors = True)
                    os.chdir("..")
                    os.chdir("..")

                    trans_name.set("")
                    company_name.set("")
                    data_name.set("")
                    commitments_name.delete(1.0, END)
                except sqlite3.Error as error:
                    print_log("DB ERROR")
                    print_log(error)
                    msg.showerror("Внимание", "Произошла ошибка при удалении сделки. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                finally:
                    if (sqlite_connections):
                        sqlite_connections.close()
                        print_log("DB CLOSE")
    else:
        msg.showerror("Внимание", "Выберите данные для удаления")
    trans_name.set("")
    company_name.set("")
    data_name.set("{}".format(time_str()))
    commitments_name.delete(1.0, END)

def trans_ch_db(event):
    try:
        trans_chne_values = transactions.item(transactions.selection(), option="values")    
        if trans_chne_values != "":
            for i in trans_data:
                if i[0] == trans_chne_values[0] and i[1] == trans_chne_values[1] and i[2] == trans_chne_values[2] and i[3] == trans_chne_values[3]:
                    save_tasks = i[4]
            save_document_name = trans_chne_values[2].replace(" ", "").replace(".", "").replace(":", "") + trans_chne_values[0] + trans_chne_values[1]
            new_trans_name = trans_name.get().replace("\'", "")
            new_company_name = company_name.get().replace("\'", "")
            new_data_name = data_name.get()
            new_commitments_name = commitments_name.get(1.0, END).replace("\n", " ").replace("\'", "")
            new_document_name = new_data_name.replace(" ", "").replace(".", "").replace(":", "") + new_trans_name + new_company_name
            if new_document_name == '':
                msg.showinfo("Внимание", "Введите недостающие данные!")
            else:
                os.chdir("db")
                os.chdir("trans")
                os.rename("{}".format(save_document_name), "del{}".format(save_document_name))
                if new_document_name not in os.listdir():
                    os.chdir("..")
                    os.chdir("..")
                    try:
                        sqlite_connections = sqlite3.connect(r'db\db.db')
                        cursor = sqlite_connections.cursor()
                        print_log("DB OPEN")
                        cursor.execute("""DELETE FROM trans WHERE Сделка = '{}'
                                                                AND Компания = '{}'
                                                                AND Дата = '{}'
                                                                AND Обязательства = '{}'""".format(trans_chne_values[0],
                                                                                                trans_chne_values[1],
                                                                                                trans_chne_values[2],
                                                                                                trans_chne_values[3]))
                        sqlite_connections.commit()
                        cursor.close()
                    except sqlite3.Error as error:
                        print_log("DB ERROR")
                        print_log(error)
                        msg.showerror("Внимание", "Произошла ошибка при удалении сделки. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                    finally:
                        if (sqlite_connections):
                            sqlite_connections.close()
                            print_log("DB CLOSE")
                    print_log("Сделка {} удалена из базы".format(trans_chne_values[0]))

                    trans_name.set("")
                    company_name.set("")
                    data_name.set("")
                    commitments_name.delete(1.0, END)

                    trans_create_contact(new_trans_name, new_company_name, new_data_name,
                                     new_commitments_name, save_tasks)
                    os.chdir("db")
                    os.chdir("trans")
                    os.mkdir("{}".format(new_document_name))
                    os.chdir("{}".format(new_document_name))
                    path_name = os.getcwd()
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    os.chdir("del{}".format(save_document_name))
                    for i in os.listdir():
                        os.replace("{}".format(i), "{}/{}".format(path_name, i))
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    shutil.rmtree("del{}".format(save_document_name),
                                  ignore_errors = True)
                    os.chdir("..")
                    os.chdir("..")

                    show()
                    trans_tree_shower()
                else:
                    msg.showinfo("Внимание", "Такая сделка уже существует!")
                    os.rename("del{}".format(save_document_name), "{}".format(save_document_name))
                    os.chdir("..")
                    os.chdir("..")
        else:
            msg.showerror("Внимание", "Выберите сделку для изменения и сохранения")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")
    trans_name.set("")
    company_name.set("")
    data_name.set("{}".format(time_str()))
    commitments_name.delete(1.0, END)

def trans_ch_db_not_event():
    try:
        trans_chne_values = transactions.item(transactions.selection(), option="values")    
        if trans_chne_values != "":
            for i in trans_data:
                if i[0] == trans_chne_values[0] and i[1] == trans_chne_values[1] and i[2] == trans_chne_values[2] and i[3] == trans_chne_values[3]:
                    save_tasks = i[4]
            save_document_name = trans_chne_values[2].replace(" ", "").replace(".", "").replace(":", "") + trans_chne_values[0] + trans_chne_values[1]
            new_trans_name = trans_name.get().replace("\'", "")
            new_company_name = company_name.get().replace("\'", "")
            new_data_name = data_name.get()
            new_commitments_name = commitments_name.get(1.0, END).replace("\n", " ").replace("\'", "")
            new_document_name = new_data_name.replace(" ", "").replace(".", "").replace(":", "") + new_trans_name + new_company_name
            if new_document_name == '':
                msg.showinfo("Внимание", "Введите недостающие данные!")
            else:
                os.chdir("db")
                os.chdir("trans")
                os.rename("{}".format(save_document_name), "del{}".format(save_document_name))
                if new_document_name not in os.listdir():
                    os.chdir("..")
                    os.chdir("..")
                    try:
                        sqlite_connections = sqlite3.connect(r'db\db.db')
                        cursor = sqlite_connections.cursor()
                        print_log("DB OPEN")
                        cursor.execute("""DELETE FROM trans WHERE Сделка = '{}'
                                                                AND Компания = '{}'
                                                                AND Дата = '{}'
                                                                AND Обязательства = '{}'""".format(trans_chne_values[0],
                                                                                                trans_chne_values[1],
                                                                                                trans_chne_values[2],
                                                                                                trans_chne_values[3]))
                        sqlite_connections.commit()
                        cursor.close()
                    except sqlite3.Error as error:
                        print_log("DB ERROR")
                        print_log(error)
                        msg.showerror("Внимание", "Произошла ошибка при удалении сделки. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                    finally:
                        if (sqlite_connections):
                            sqlite_connections.close()
                            print_log("DB CLOSE")
                    print_log("Сделка {} удалена из базы".format(trans_chne_values[0]))

                    trans_name.set("")
                    company_name.set("")
                    data_name.set("")
                    commitments_name.delete(1.0, END)

                    trans_create_contact(new_trans_name, new_company_name, new_data_name,
                                     new_commitments_name, save_tasks)
                    os.chdir("db")
                    os.chdir("trans")
                    os.mkdir("{}".format(new_document_name))
                    os.chdir("{}".format(new_document_name))
                    path_name = os.getcwd()
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    os.chdir("del{}".format(save_document_name))
                    for i in os.listdir():
                        os.replace("{}".format(i), "{}/{}".format(path_name, i))
                    os.chdir("..")
                    os.chdir("..")
                    os.chdir("..")

                    os.chdir("db")
                    os.chdir("trans")
                    shutil.rmtree("del{}".format(save_document_name),
                                  ignore_errors = True)
                    os.chdir("..")
                    os.chdir("..")

                    show()
                    trans_tree_shower()
                else:
                    msg.showinfo("Внимание", "Такая сделка уже существует!")
                    os.rename("del{}".format(save_document_name), "{}".format(save_document_name))
                    os.chdir("..")
                    os.chdir("..")
        else:
            msg.showerror("Внимание", "Выберите сделку для изменения и сохранения")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")
    trans_name.set("")
    company_name.set("")
    data_name.set("{}".format(time_str()))
    commitments_name.delete(1.0, END)

def file_show():
    try:
        file_values = transactions.item(transactions.selection(), option="values")
        path_name = os.getcwd()
        if file_values != "":
            save_file_name = file_values[2].replace(" ", "").replace(".", "").replace(":", "") + file_values[0] + file_values[1]
            file_name = fd.askopenfilenames(initialdir = "{}/db/trans/{}".format(path_name, save_file_name))
        else:
            msg.showerror("Внимание", "Выберите сделку для отображения прикрепленных документов")
    except TclError:
        msg.showerror("Внимание", "Мноственное редактирование не поддерживается")

def tasks_show():
    try:
        tasks_values = transactions.item(transactions.selection(), option="values")
        if tasks_values != "":
            global save_tasks_str, save_tasks
            for i in trans_data:
                if i[0] == tasks_values[0] and i[1] == tasks_values[1] and i[2] == tasks_values[2] and i[3] == tasks_values[3]:
                    save_tasks_str = i[4]
            save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]

            def tasksview():
                tasks_list.delete(*tasks_list.get_children())
                global save_tasks_str, save_tasks
                for i in trans_data:
                    if i[0] == tasks_values[0] and i[1] == tasks_values[1] and i[2] == tasks_values[2] and i[3] == tasks_values[3]:
                        save_tasks_str = i[4]
                save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
                green_save_tasks = []
                red_save_tasks = []
                grey_save_tasks = []
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            grey_save_tasks.append(row)
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                green_save_tasks.append(row)
                            else:
                                red_save_tasks.append(row)
                save_tasks = []
                if tasks_green_radio_btn.state() == ('alternate',) or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_green_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + green_save_tasks
                if tasks_red_radio_btn.state() == ('alternate',) or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_red_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + red_save_tasks
                if tasks_grey_radio_btn.state() == ('alternate',) or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_grey_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + grey_save_tasks
                A = []
                for i in save_tasks:
                    i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                    A.append(i)
                A_Z = tasks_AZ_filter.get()
                if A_Z == "А-Я":
                    A = sorted(A)
                    B = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        B.append(i)
                    save_tasks = B
                else:
                    A = sorted(A, reverse = True)
                    C = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        C.append(i)
                    save_tasks = C
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            tag_row = 'grey'
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                tag_row = 'green'
                            else:
                                tag_row = 'red'
                        tasks_list.insert(
                                parent = '',
                                index = 'end',
                                values = row,
                                tag = '{}'.format(tag_row)
                                )
                else:
                    tasks_list.delete(*tasks_list.get_children())
            def tasksview_event(event):
                tasks_list.delete(*tasks_list.get_children())
                global save_tasks_str, save_tasks
                for i in trans_data:
                    if i[0] == tasks_values[0] and i[1] == tasks_values[1] and i[2] == tasks_values[2] and i[3] == tasks_values[3]:
                        save_tasks_str = i[4]
                save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
                green_save_tasks = []
                red_save_tasks = []
                grey_save_tasks = []
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            grey_save_tasks.append(row)
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                green_save_tasks.append(row)
                            else:
                                red_save_tasks.append(row)
                save_tasks = []
                if tasks_green_radio_btn.state() == ('alternate',) or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_green_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + green_save_tasks
                if tasks_red_radio_btn.state() == ('alternate',) or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_red_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + red_save_tasks
                if tasks_grey_radio_btn.state() == ('alternate',) or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_grey_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + grey_save_tasks
                A = []
                for i in save_tasks:
                    i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                    A.append(i)
                A_Z = tasks_AZ_filter.get()
                if A_Z == "А-Я":
                    A = sorted(A)
                    B = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        B.append(i)
                    save_tasks = B
                else:
                    A = sorted(A, reverse = True)
                    C = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        C.append(i)
                    save_tasks = C
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            tag_row = 'grey'
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                tag_row = 'green'
                            else:
                                tag_row = 'red'
                        tasks_list.insert(
                                parent = '',
                                index = 'end',
                                values = row,
                                tag = '{}'.format(tag_row)
                                )
                else:
                    tasks_list.delete(*tasks_list.get_children())

            def tasks_add(tasks_list):
                try:
                    sqlite_connections = sqlite3.connect(r'db\db.db')
                    cursor = sqlite_connections.cursor()
                    print_log("DB OPEN")
                    cursor.execute("""UPDATE trans SET Задачи = '{}' WHERE Сделка = '{}'
                                                    AND Компания = '{}'
                                                    AND Дата = '{}'
                                                    AND Обязательства = '{}'""".format(tasks_list, tasks_values[0],
                                                                                    tasks_values[1],
                                                                                    tasks_values[2],
                                                                                    tasks_values[3]))
                    sqlite_connections.commit()
                    cursor.close()
                except sqlite3.Error as error:
                    print_log("DB ERROR")
                    print_log(error)
                    msg.showerror("Внимание", "Произошла ошибка при добавления задания. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                finally:
                    if (sqlite_connections):
                        sqlite_connections.close()
                        print_log("DB CLOSE")  

            def finish_tasks():
                try:
                    finish_tasks_values = tasks_list.item(tasks_list.selection(), option="values")
                    if finish_tasks_values != "":
                        global replace_finish_tasks_values
                        replace_finish_tasks_values = "("+str([[x] for x in finish_tasks_values])[1:-1].replace("'", "")+")"
                        finish_tasks_window = Toplevel()
                        finish_tasks_window.grab_set()
                        finish_tasks_window.title("Редактировать задачу для сделки \'{}\'".format(tasks_values[0]))
                        finish_tasks_window.resizable(False, False)
                        finish_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                        finish_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                        def finish_tasks_window_quit():
                            finish_tasks_window.destroy()
                        def finish_tasks_window_quit_event(event):
                            finish_tasks_window.destroy()

                        def finish_tasks_save_func():
                            finish_tasks_hour_get = finish_tasks_hour.get()
                            finish_tasks_minute_get = finish_tasks_minute.get()
                            finish_tasks_second_get = finish_tasks_second.get()
                            finish_tasks_date_get = finish_tasks_date.get()
                            finish_tasks_text_get = finish_tasks_text.get(1.0, END).replace("\n", "").replace("\'", "")
                            fin_text = finish_entry.get().replace("\'", "")
                            finish_tasks_add_list_get = str([["{} {}:{}:{}".format(finish_tasks_date_get,
                                                                            finish_tasks_hour_get,
                                                                            finish_tasks_minute_get,
                                                                            finish_tasks_second_get)],
                                                      [finish_tasks_text_get], [fin_text]]).replace("'", "")
                            finish_save_tasks_get = str("{}, ({})".format(save_tasks_str, finish_tasks_add_list_get[1:-1]))
                            tasks_add(finish_save_tasks_get)
                            show()
                            tasksview()
                            trans_view_not_event()
                            global replace_finish_tasks_values
                            tasks_add(save_tasks_str.replace(", {}".format(replace_finish_tasks_values), "").replace("{}, ".format(replace_finish_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                            replace_finish_tasks_values = "("+finish_tasks_add_list_get[1:-1]+")"
                        
                        def finish_calendar_tomorrow():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            if now_day == "31":
                                tomorrow_day = "01"
                                if now_month == "12":
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)    
                                else:
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                            elif now_day == "30":
                                if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tommorrow_month = now_month
                                    tommorrow_year = now_year
                            elif now_day == "29":
                                if now_month == "02":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "28":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                tomorrow_day = str(int(now_day)+1)
                                if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                                    
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_week():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 21:
                                tomorrow_day = str(int(now_day)+7)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            elif now_day == "22":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = now_month
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "23":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "24":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "03"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                minus = int(now_day)-25
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = str(3+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = str(4+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = str(2+minus)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                elif now_month == "12":
                                    tomorrow_day = "01"
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_month():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 28:
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "29" or now_day == "30":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "31":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                                    tomorrow_day = "30"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        #Создание функции вызова контекстного меню
                        def finish_tasks_text_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_tasks_text_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_tasks_text_popupFocusOut(event):
                            finish_tasks_text_con_menu.unpost()
                        def finish_tasks_text_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_tasks_text.selection_get())
                            except :
                                return
                        def finish_tasks_text_paste_cl():
                            try:
                                finish_tasks_text.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_tasks_text_con_menu = Menu(tearoff = False)
                        finish_tasks_text_con_menu.add_command(label = "Копировать", command = finish_tasks_text_copy_selection)
                        finish_tasks_text_con_menu.add_command(label = "Вставить", command = finish_tasks_text_paste_cl)

                        #Создание функции вызова контекстного меню
                        def finish_entry_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_entry_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_entry_popupFocusOut(event):
                            finish_entry_con_menu.unpost()
                        def finish_entry_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_entry.selection_get())
                            except :
                                return
                        def finish_entry_paste_cl():
                            try:
                                finish_entry.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_entry_con_menu = Menu(tearoff = False)
                        finish_entry_con_menu.add_command(label = "Копировать", command = finish_entry_copy_selection)
                        finish_entry_con_menu.add_command(label = "Вставить", command = finish_entry_paste_cl)


                        finish_tasks_frame_1 = LabelFrame(finish_tasks_window, text = "Срок завершения")
                        finish_tasks_frame_1.pack(fill = X, expand = True)

                        finish_lbl_hour = Label(finish_tasks_frame_1,
                                                text = "Час/Мин/Сек:", width = 15)
                        finish_lbl_hour.pack(side = LEFT, expand = False)
                        finish_tasks_hour = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=23,
                                        width = 5, state = 'readonly')
                        finish_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_hour.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[0]))
                        finish_tasks_minute = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_minute.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[1]))
                        finish_tasks_second = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_second.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[2]))
                        finish_lbl_date = Label(finish_tasks_frame_1, text = "Дата:", width = 8)
                        finish_lbl_date.pack(side = LEFT, expand = False)
                        finish_tasks_date = DateEntry(finish_tasks_frame_1, width = 15,
                                                      locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                                      state = 'readonly')
                        finish_tasks_date.pack(side = LEFT, expand = False)
                        finish_tasks_date.delete(0, END)
                        finish_tasks_date.insert(0, "{}".format(finish_tasks_values[0].split(" ")[0]))

                        finish_tasks_frame_btn = LabelFrame(finish_tasks_window)
                        finish_tasks_frame_btn.pack(fill = X, expand = True)
                        finish_tasks_btn_tomorrow = Button(finish_tasks_frame_btn, text = "Завтра",
                                                        width = 17, command = finish_calendar_tomorrow)
                        finish_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_week = Button(finish_tasks_frame_btn, text = "Через неделю",
                                                    width = 17, command = finish_calendar_week)
                        finish_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_month = Button(finish_tasks_frame_btn, text = "Через месяц",
                                                     width = 17, command = finish_calendar_month)
                        finish_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)

                        finish_tasks_lbl_frame = LabelFrame(finish_tasks_window,
                                                            text = "Описание задачи")
                        finish_tasks_lbl_frame.pack(fill = BOTH, expand = True)
                        finish_tasks_text = Text(finish_tasks_lbl_frame, height = 5, width = 50)
                        finish_tasks_text.pack(fill = BOTH, expand = True)
                        finish_tasks_text.insert(1.0, "{}".format(finish_tasks_values[1]))
                        finish_tasks_text.bind("<Button-3>", finish_tasks_text_popup)
                        finish_tasks_text.bind("<FocusIn>", finish_tasks_text_popupFocusOut)  
                        finish_tasks_text.bind("<Control-C>", finish_tasks_text_copy_selection)
                        finish_tasks_text.bind("<Control-V>", finish_tasks_text_paste_cl)
                        def finish_tasks_text_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_tasks_text_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_tasks_text_paste_cl()
                        finish_tasks_text.bind("<Key>", finish_tasks_text_key_callback)

                        finish_text_frame = LabelFrame(finish_tasks_window, text = "Отметка о выполнении")
                        finish_text_frame.pack(fill = BOTH, expand = True)
                        finish_entry = Entry(finish_text_frame)
                        finish_entry.insert(END, "{}".format(finish_tasks_values[2]))
                        finish_entry.pack(side = LEFT, fill = X, expand = True)
                        finish_entry.bind("<Button-3>", finish_entry_popup)
                        finish_entry.bind("<FocusIn>", finish_entry_popupFocusOut)  
                        finish_entry.bind("<Control-C>", finish_entry_copy_selection)
                        finish_entry.bind("<Control-V>", finish_entry_paste_cl)
                        def finish_entry_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_entry_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_entry_paste_cl()
                        finish_entry.bind("<Key>", finish_entry_key_callback)

                        finish_tasks_save_btn = Button(finish_text_frame, width = 15, text = "Сохранить",
                                                       command = finish_tasks_save_func)
                        finish_tasks_save_btn.pack(side = LEFT, fill = BOTH, expand = False, padx = 1, pady = 1)
                        finish_tasks_cancel_btn = Button(finish_text_frame, width = 15, text = "Закрыть",
                                                         command = finish_tasks_window_quit)
                        finish_tasks_cancel_btn.pack(side = LEFT, fill = BOTH, expand = False,padx = 1, pady = 1)
                        finish_tasks_cancel_btn.bind("<Return>", finish_tasks_window_quit_event)
                        finish_tasks_cancel_btn.focus()
                    else:
                        tasks_window.attributes("-topmost", False)
                        if msg.showerror("Внимание", "Выберите задачу для редактирования"):
                            tasks_window.attributes("-topmost", True)
                except TclError:
                    tasks_window.attributes("-topmost", False)
                    if msg.showinfo("Внимание", "Множественное редактирование не поддерживается"):
                        tasks_window.attributes("-topmost", True)
            def finish_tasks_event(event):
                try:
                    finish_tasks_values = tasks_list.item(tasks_list.selection(), option="values")
                    if finish_tasks_values != "":
                        global replace_finish_tasks_values
                        replace_finish_tasks_values = "("+str([[x] for x in finish_tasks_values])[1:-1].replace("'", "")+")"
                        finish_tasks_window = Toplevel()
                        finish_tasks_window.grab_set()
                        finish_tasks_window.title("Редактировать задачу для сделки \'{}\'".format(tasks_values[0]))
                        finish_tasks_window.resizable(False, False)
                        finish_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                        finish_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                        def finish_tasks_window_quit():
                            finish_tasks_window.destroy()
                        def finish_tasks_window_quit_event(event):
                            finish_tasks_window.destroy()

                        def finish_tasks_save_func():
                            finish_tasks_hour_get = finish_tasks_hour.get()
                            finish_tasks_minute_get = finish_tasks_minute.get()
                            finish_tasks_second_get = finish_tasks_second.get()
                            finish_tasks_date_get = finish_tasks_date.get()
                            finish_tasks_text_get = finish_tasks_text.get(1.0, END).replace("\n", "").replace("\'", "")
                            fin_text = finish_entry.get().replace("\'", "")
                            finish_tasks_add_list_get = str([["{} {}:{}:{}".format(finish_tasks_date_get,
                                                                            finish_tasks_hour_get,
                                                                            finish_tasks_minute_get,
                                                                            finish_tasks_second_get)],
                                                      [finish_tasks_text_get], [fin_text]]).replace("'", "")
                            finish_save_tasks_get = str("{}, ({})".format(save_tasks_str, finish_tasks_add_list_get[1:-1]))
                            tasks_add(finish_save_tasks_get)
                            show()
                            tasksview()
                            trans_view_not_event()
                            global replace_finish_tasks_values
                            tasks_add(save_tasks_str.replace(", {}".format(replace_finish_tasks_values), "").replace("{}, ".format(replace_finish_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                            replace_finish_tasks_values = "("+finish_tasks_add_list_get[1:-1]+")"
                        
                        def finish_calendar_tomorrow():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            if now_day == "31":
                                tomorrow_day = "01"
                                if now_month == "12":
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)    
                                else:
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                            elif now_day == "30":
                                if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tommorrow_month = now_month
                                    tommorrow_year = now_year
                            elif now_day == "29":
                                if now_month == "02":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "28":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                tomorrow_day = str(int(now_day)+1)
                                if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                                    
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_week():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 21:
                                tomorrow_day = str(int(now_day)+7)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            elif now_day == "22":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = now_month
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "23":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "24":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "03"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                minus = int(now_day)-25
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = str(3+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = str(4+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = str(2+minus)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                elif now_month == "12":
                                    tomorrow_day = "01"
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_month():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 28:
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "29" or now_day == "30":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "31":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                                    tomorrow_day = "30"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        #Создание функции вызова контекстного меню
                        def finish_tasks_text_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_tasks_text_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_tasks_text_popupFocusOut(event):
                            finish_tasks_text_con_menu.unpost()
                        def finish_tasks_text_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_tasks_text.selection_get())
                            except :
                                return
                        def finish_tasks_text_paste_cl():
                            try:
                                finish_tasks_text.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_tasks_text_con_menu = Menu(tearoff = False)
                        finish_tasks_text_con_menu.add_command(label = "Копировать", command = finish_tasks_text_copy_selection)
                        finish_tasks_text_con_menu.add_command(label = "Вставить", command = finish_tasks_text_paste_cl)

                        #Создание функции вызова контекстного меню
                        def finish_entry_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_entry_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_entry_popupFocusOut(event):
                            finish_entry_con_menu.unpost()
                        def finish_entry_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_entry.selection_get())
                            except :
                                return
                            #root.after(10, copy_selection2, widget)
                        def finish_entry_paste_cl():
                            try:
                                finish_entry.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_entry_con_menu = Menu(tearoff = False)
                        finish_entry_con_menu.add_command(label = "Копировать", command = finish_entry_copy_selection)
                        finish_entry_con_menu.add_command(label = "Вставить", command = finish_entry_paste_cl)


                        finish_tasks_frame_1 = LabelFrame(finish_tasks_window, text = "Срок завершения")
                        finish_tasks_frame_1.pack(fill = X, expand = True)

                        finish_lbl_hour = Label(finish_tasks_frame_1,
                                                text = "Час/Мин/Сек:", width = 15)
                        finish_lbl_hour.pack(side = LEFT, expand = False)
                        finish_tasks_hour = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=23,
                                        width = 5, state = 'readonly')
                        finish_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_hour.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[0]))
                        finish_tasks_minute = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_minute.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[1]))
                        finish_tasks_second = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_second.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[2]))
                        finish_lbl_date = Label(finish_tasks_frame_1, text = "Дата:", width = 8)
                        finish_lbl_date.pack(side = LEFT, expand = False)
                        finish_tasks_date = DateEntry(finish_tasks_frame_1, width = 15,
                                                   locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                                      state = 'readonly')
                        finish_tasks_date.pack(side = LEFT, expand = False)
                        finish_tasks_date.delete(0, END)
                        finish_tasks_date.insert(0, "{}".format(finish_tasks_values[0].split(" ")[0]))

                        finish_tasks_frame_btn = LabelFrame(finish_tasks_window)
                        finish_tasks_frame_btn.pack(fill = X, expand = True)
                        finish_tasks_btn_tomorrow = Button(finish_tasks_frame_btn, text = "Завтра",
                                                        width = 17, command = finish_calendar_tomorrow)
                        finish_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_week = Button(finish_tasks_frame_btn, text = "Через неделю",
                                                    width = 17, command = finish_calendar_week)
                        finish_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_month = Button(finish_tasks_frame_btn, text = "Через месяц",
                                                     width = 17, command = finish_calendar_month)
                        finish_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)

                        finish_tasks_lbl_frame = LabelFrame(finish_tasks_window,
                                                            text = "Описание задачи")
                        finish_tasks_lbl_frame.pack(fill = BOTH, expand = True)
                        finish_tasks_text = Text(finish_tasks_lbl_frame, height = 5, width = 50)
                        finish_tasks_text.pack(fill = BOTH, expand = True)
                        finish_tasks_text.insert(1.0, "{}".format(finish_tasks_values[1]))
                        finish_tasks_text.bind("<Button-3>", finish_tasks_text_popup)
                        finish_tasks_text.bind("<FocusIn>", finish_tasks_text_popupFocusOut)  
                        finish_tasks_text.bind("<Control-C>", finish_tasks_text_copy_selection)
                        finish_tasks_text.bind("<Control-V>", finish_tasks_text_paste_cl)
                        def finish_tasks_text_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_tasks_text_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_tasks_text_paste_cl()
                        finish_tasks_text.bind("<Key>", finish_tasks_text_key_callback)

                        finish_text_frame = LabelFrame(finish_tasks_window, text = "Отметка о выполнении")
                        finish_text_frame.pack(fill = BOTH, expand = True)
                        finish_entry = Entry(finish_text_frame)
                        finish_entry.insert(END, "{}".format(finish_tasks_values[2]))
                        finish_entry.pack(side = LEFT, fill = X, expand = True)
                        finish_entry.bind("<Button-3>", finish_entry_popup)
                        finish_entry.bind("<FocusIn>", finish_entry_popupFocusOut)  
                        finish_entry.bind("<Control-C>", finish_entry_copy_selection)
                        finish_entry.bind("<Control-V>", finish_entry_paste_cl)
                        def finish_entry_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_entry_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_entry_paste_cl()
                        finish_entry.bind("<Key>", finish_entry_key_callback)

                        finish_tasks_save_btn = Button(finish_text_frame, width = 15, text = "Сохранить",
                                                       command = finish_tasks_save_func)
                        finish_tasks_save_btn.pack(side = LEFT, fill = BOTH, expand = False, padx = 1, pady = 1)
                        finish_tasks_cancel_btn = Button(finish_text_frame, width = 15, text = "Закрыть",
                                                         command = finish_tasks_window_quit)
                        finish_tasks_cancel_btn.pack(side = LEFT, fill = BOTH, expand = False,padx = 1, pady = 1)
                        finish_tasks_cancel_btn.bind("<Return>", finish_tasks_window_quit_event)
                        finish_tasks_cancel_btn.focus()
                    else:
                        tasks_window.attributes("-topmost", False)
                        if msg.showerror("Внимание", "Выберите задачу для редактирования"):
                            tasks_window.attributes("-topmost", True)
                except TclError:
                    tasks_window.attributes("-topmost", False)
                    if msg.showinfo("Внимание", "Множственное редактирование не поддерживается"):
                        tasks_window.attributes("-topmost", True)

            def delete_tasks():
                delete_tasks_valueses = [tasks_list.item(x, option="values") for x in tasks_list.selection()]
                if delete_tasks_valueses != []:
                    tasks_window.attributes("-topmost", False)
                    if msg.askyesno("Внимание", "Удалить выбранные задачи?"):
                        for delete_tasks_values in delete_tasks_valueses:
                            replace_delete_tasks_values = "("+str([[x] for x in delete_tasks_values])[1:-1].replace("'", "")+")"
                            tasks_add(save_tasks_str.replace(", {}".format(replace_delete_tasks_values), "").replace("{}, ".format(replace_delete_tasks_values), "").replace("{}".format(replace_delete_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                        tasks_window.attributes("-topmost", True)
                    tasks_window.attributes("-topmost", True)
                else:
                    tasks_window.attributes("-topmost", False)
                    if msg.showerror("Внимание", "Выберите задачу для удаления"):
                        tasks_window.attributes("-topmost", True)
            def delete_tasks_event(event):
                delete_tasks_valueses = [tasks_list.item(x, option="values") for x in tasks_list.selection()]
                if delete_tasks_valueses != []:
                    tasks_window.attributes("-topmost", False)
                    if msg.askyesno("Внимание", "Удалить выбранные задачи?"):
                        for delete_tasks_values in delete_tasks_valueses:
                            replace_delete_tasks_values = "("+str([[x] for x in delete_tasks_values])[1:-1].replace("'", "")+")"
                            tasks_add(save_tasks_str.replace(", {}".format(replace_delete_tasks_values), "").replace("{}, ".format(replace_delete_tasks_values), "").replace("{}".format(replace_delete_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                        tasks_window.attributes("-topmost", True)
                    tasks_window.attributes("-topmost", True)
                else:
                    tasks_window.attributes("-topmost", False)
                    if msg.showerror("Внимание", "Выберите задачу для удаления"):
                        tasks_window.attributes("-topmost", True)

            def new_tasks():
                new_tasks_window = Toplevel()
                new_tasks_window.grab_set()
                new_tasks_window.title("Новая задача для сделки \'{}\'".format(tasks_values[0]))
                new_tasks_window.resizable(False, False)
                new_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                new_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                def new_tasks_add():
                    new_tasks_hour_get = new_tasks_hour.get()
                    new_tasks_minute_get = new_tasks_minute.get()
                    new_tasks_second_get = new_tasks_second.get()
                    new_tasks_date_get = new_tasks_date.get()
                    new_tasks_text_get = text_tasks.get(1.0, END).replace("\n", "").replace("\'", "")
                    new_tasks_add_list_get = str([["{} {}:{}:{}".format(new_tasks_date_get,
                                                                        new_tasks_hour_get,
                                                                        new_tasks_minute_get,
                                                                        new_tasks_second_get)],
                                                  [new_tasks_text_get], []]).replace("'", "")
                    if save_tasks == []:
                        new_save_tasks_get = str("({})".format(new_tasks_add_list_get[1:-1]))
                    else:
                        new_save_tasks_get = str("{}, ({})".format(save_tasks_str, new_tasks_add_list_get[1:-1]))
                    tasks_add(new_save_tasks_get)
                    show()
                    tasksview()
                    trans_view_not_event()

                def calendar_tomorrow():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    if now_day == "31":
                        tomorrow_day = "01"
                        if now_month == "12":
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)    
                        else:
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                    elif now_day == "30":
                        if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tommorrow_month = now_month
                            tommorrow_year = now_year
                    elif now_day == "29":
                        if now_month == "02":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "28":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        tomorrow_day = str(int(now_day)+1)
                        if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                            
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_week():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 21:
                        tomorrow_day = str(int(now_day)+7)
                        if len(tomorrow_day) == 1:
                            tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                    elif now_day == "22":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "23":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "24":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "03"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        minus = int(now_day)-25
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = str(3+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = str(4+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = str(2+minus)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        elif now_month == "12":
                            tomorrow_day = "01"
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_month():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 28:
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "29" or now_day == "30":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "31":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                            tomorrow_day = "30"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                #Создание функции вызова контекстного меню
                def text_tasks_popup(event):
                    global x, y
                    x = event.x
                    y = event.y
                    text_tasks_con_menu.post(event.x_root, event.y_root)
                    root.focus()

                def text_tasks_popupFocusOut(event):
                    text_tasks_con_menu.unpost()
                def text_tasks_copy_selection():
                    try:
                        root.clipboard_clear()
                        root.clipboard_append(text_tasks.selection_get())
                    except :
                        return
                def text_tasks_paste_cl():
                    try:
                        text_tasks.insert(INSERT, root.clipboard_get())
                    except :
                        return
                    
                text_tasks_con_menu = Menu(tearoff = False)
                text_tasks_con_menu.add_command(label = "Копировать", command = text_tasks_copy_selection)
                text_tasks_con_menu.add_command(label = "Вставить", command = text_tasks_paste_cl)

                new_tasks_frame_1 = LabelFrame(new_tasks_window, text = "Срок завершения")
                new_tasks_frame_1.pack(fill = X, expand = True)

                new_lbl_hour = Label(new_tasks_frame_1, text = "Час/Мин/Сек:", width = 15)
                new_lbl_hour.pack(side = LEFT, expand = False)
                new_tasks_hour = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=23,
                                width = 5, state = 'readonly')
                new_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_hour.set("12")
                new_tasks_minute = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_minute.set("00")
                new_tasks_second = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_second.set("00")
                new_lbl_date = Label(new_tasks_frame_1, text = "Дата:", width = 8)
                new_lbl_date.pack(side = LEFT, expand = False)
                new_tasks_date = DateEntry(new_tasks_frame_1, width = 15,
                                           locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                           state = 'readonly')
                new_tasks_date.pack(side = LEFT, expand = False)

                new_tasks_frame_btn = LabelFrame(new_tasks_window)
                new_tasks_frame_btn.pack(fill = X, expand = True)
                new_tasks_btn_tomorrow = Button(new_tasks_frame_btn, text = "Завтра",
                                                width = 17, command = calendar_tomorrow)
                new_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_week = Button(new_tasks_frame_btn, text = "Через неделю",
                                            width = 17, command = calendar_week)
                new_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_month = Button(new_tasks_frame_btn, text = "Через месяц",
                                             width = 17, command = calendar_month)
                new_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)
                
                new_tasks_frame_2 = LabelFrame(new_tasks_window, text = "Описание задачи")
                new_tasks_frame_2.pack(fill = X, expand = True)
                text_tasks = Text(new_tasks_frame_2, height = 3, width = 53)
                text_tasks.pack(fill = X, expand = True)
                text_tasks.bind("<Button-3>", text_tasks_popup)
                text_tasks.bind("<FocusIn>", text_tasks_popupFocusOut)  
                text_tasks.bind("<Control-C>", text_tasks_copy_selection)
                text_tasks.bind("<Control-V>", text_tasks_paste_cl)
                def text_tasks_key_callback(event):
                    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                        if chr(event.keycode) == "C":
                            text_tasks_copy_selection()
                        elif chr(event.keycode) == "V":
                            text_tasks_paste_cl()
                text_tasks.bind("<Key>", text_tasks_key_callback)

                new_tasks_frame_3 = LabelFrame(new_tasks_window)
                new_tasks_frame_3.pack(fill = X, expand = True)
                new_tasks_add_btn = Button(new_tasks_frame_3, text = "Добавить",
                                           width = 20, command = new_tasks_add)
                new_tasks_add_btn.pack(side = RIGHT, fill = BOTH, expand = False)
            def new_tasks_event(event):
                new_tasks_window = Toplevel()
                new_tasks_window.grab_set()
                new_tasks_window.title("Новая задача для сделки \'{}\'".format(tasks_values[0]))
                new_tasks_window.resizable(False, False)
                new_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                new_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                def new_tasks_add():
                    new_tasks_hour_get = new_tasks_hour.get()
                    new_tasks_minute_get = new_tasks_minute.get()
                    new_tasks_second_get = new_tasks_second.get()
                    new_tasks_date_get = new_tasks_date.get()
                    new_tasks_text_get = text_tasks.get(1.0, END).replace("\n", "").replace("\'", "")
                    new_tasks_add_list_get = str([["{} {}:{}:{}".format(new_tasks_date_get,
                                                                        new_tasks_hour_get,
                                                                        new_tasks_minute_get,
                                                                        new_tasks_second_get)],
                                                  [new_tasks_text_get], []]).replace("'", "")
                    if save_tasks == []:
                        new_save_tasks_get = str("({})".format(new_tasks_add_list_get[1:-1]))
                    else:
                        new_save_tasks_get = str("{}, ({})".format(save_tasks_str, new_tasks_add_list_get[1:-1]))
                    tasks_add(new_save_tasks_get)
                    show()
                    tasksview()
                    trans_view_not_event()

                def calendar_tomorrow():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    if now_day == "31":
                        tomorrow_day = "01"
                        if now_month == "12":
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)    
                        else:
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                    elif now_day == "30":
                        if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tommorrow_month = now_month
                            tommorrow_year = now_year
                    elif now_day == "29":
                        if now_month == "02":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "28":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        tomorrow_day = str(int(now_day)+1)
                        if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                            
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_week():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 21:
                        tomorrow_day = str(int(now_day)+7)
                        if len(tomorrow_day) == 1:
                            tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                    elif now_day == "22":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "23":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "24":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "03"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        minus = int(now_day)-25
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = str(3+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = str(4+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = str(2+minus)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        elif now_month == "12":
                            tomorrow_day = "01"
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_month():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 28:
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "29" or now_day == "30":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "31":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                            tomorrow_day = "30"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                #Создание функции вызова контекстного меню
                def text_tasks_popup(event):
                    global x, y
                    x = event.x
                    y = event.y
                    text_tasks_con_menu.post(event.x_root, event.y_root)
                    root.focus()

                def text_tasks_popupFocusOut(event):
                    text_tasks_con_menu.unpost()
                def text_tasks_copy_selection():
                    try:
                        root.clipboard_clear()
                        root.clipboard_append(text_tasks.selection_get())
                    except :
                        return
                def text_tasks_paste_cl():
                    try:
                        text_tasks.insert(INSERT, root.clipboard_get())
                    except :
                        return
                    
                text_tasks_con_menu = Menu(tearoff = False)
                text_tasks_con_menu.add_command(label = "Копировать", command = text_tasks_copy_selection)
                text_tasks_con_menu.add_command(label = "Вставить", command = text_tasks_paste_cl)

                new_tasks_frame_1 = LabelFrame(new_tasks_window, text = "Срок завершения")
                new_tasks_frame_1.pack(fill = X, expand = True)

                new_lbl_hour = Label(new_tasks_frame_1, text = "Час/Мин/Сек:", width = 15)
                new_lbl_hour.pack(side = LEFT, expand = False)
                new_tasks_hour = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=23,
                                width = 5, state = 'readonly')
                new_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_hour.set("12")
                new_tasks_minute = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_minute.set("00")
                new_tasks_second = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_second.set("00")
                new_lbl_date = Label(new_tasks_frame_1, text = "Дата:", width = 8)
                new_lbl_date.pack(side = LEFT, expand = False)
                new_tasks_date = DateEntry(new_tasks_frame_1, width = 15,
                                           locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                           state = 'readonly')
                new_tasks_date.pack(side = LEFT, expand = False)

                new_tasks_frame_btn = LabelFrame(new_tasks_window)
                new_tasks_frame_btn.pack(fill = X, expand = True)
                new_tasks_btn_tomorrow = Button(new_tasks_frame_btn, text = "Завтра",
                                                width = 17, command = calendar_tomorrow)
                new_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_week = Button(new_tasks_frame_btn, text = "Через неделю",
                                            width = 17, command = calendar_week)
                new_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_month = Button(new_tasks_frame_btn, text = "Через месяц",
                                             width = 17, command = calendar_month)
                new_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)
                
                new_tasks_frame_2 = LabelFrame(new_tasks_window, text = "Описание задачи")
                new_tasks_frame_2.pack(fill = X, expand = True)
                text_tasks = Text(new_tasks_frame_2, height = 3, width = 53)
                text_tasks.pack(fill = X, expand = True)
                text_tasks.bind("<Button-3>", text_tasks_popup)
                text_tasks.bind("<FocusIn>", text_tasks_popupFocusOut)  
                text_tasks.bind("<Control-C>", text_tasks_copy_selection)
                text_tasks.bind("<Control-V>", text_tasks_paste_cl)
                def text_tasks_key_callback(event):
                    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                        if chr(event.keycode) == "C":
                            text_tasks_copy_selection()
                        elif chr(event.keycode) == "V":
                            text_tasks_paste_cl()
                text_tasks.bind("<Key>", text_tasks_key_callback)

                new_tasks_frame_3 = LabelFrame(new_tasks_window)
                new_tasks_frame_3.pack(fill = X, expand = True)
                new_tasks_add_btn = Button(new_tasks_frame_3, text = "Добавить",
                                           width = 20, command = new_tasks_add)
                new_tasks_add_btn.pack(side = RIGHT, fill = BOTH, expand = False)

            #Создание функции вызова контекстного меню для поля задач
            def tasks_popup(event):
                global x, y, tasks_menu
                x = event.x
                y = event.y
                valueses = [tasks_list.item(x, option="values") for x in tasks_list.selection()]
                def finish_all_tasks_in_window():
                    values_in_trans = [transactions.item(x, option="values") for x in transactions.selection()]
                    for values in values_in_trans:
                        for i in trans_data:
                            if i[0] == values[0] and i[1] == values[1] and i[2] == values[2] and i[3] == values[3]:
                                save_tasks_str = i[4]
                        save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
                    valueses_list = [list(x) for x in valueses]
                    for item in valueses_list:
                        if item[2].replace(" ", "") == '':
                            item[2] = '+'
                    for i in valueses_list:
                        for j in save_tasks:
                            if j[0] == i[0] and j[1] == i[1]:
                                j[2] = i[2]
                    save_tasks_replace_str = ""
                    for i in save_tasks:
                        i_str = ""
                        for element in i:
                            i_str += "["+str(element)+"], "
                        save_tasks_replace_str += "("+str(i_str[:-2]).replace("\'", "")+"), "
                    try:
                        sqlite_connections = sqlite3.connect(r'db\db.db')
                        cursor = sqlite_connections.cursor()
                        print_log("DB OPEN")
                        cursor.execute("""Update trans set Задачи = "{}" WHERE Сделка = '{}'
                                        AND Компания = '{}'
                                        AND Дата = '{}'
                                        AND Обязательства = '{}'""".format(save_tasks_replace_str[:-2],
                                                                            values_in_trans[0][0],
                                                                            values_in_trans[0][1],
                                                                            values_in_trans[0][2],
                                                                            values_in_trans[0][3]))
                        sqlite_connections.commit()
                        cursor.close()
                    except sqlite3.Error as error:
                        print_log("DB ERROR")
                        print_log(error)
                        msg.showerror("Внимание", "Произошла ошибка при чтении базы данных. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                    finally:
                        if (sqlite_connections):
                            sqlite_connections.close()
                            print_log("DB CLOSE")
                    show()
                    tasksview()

                if len(valueses) == 0:
                    tasks_menu = Menu(tearoff = False)
                    tasks_menu.add_command(label = "Редактировать",
                                           command = finish_tasks,
                                           state = 'disabled')
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Удалить",
                                          command = delete_tasks,
                                           state = 'disabled')
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Новая задача",
                                          command = new_tasks)
                    tasks_menu.add_command(label = "Завершить задачи",
                                           command = finish_all_tasks_in_window,
                                           state = 'disabled')
                elif len(valueses) == 1:
                    tasks_menu = Menu(tearoff = False)
                    tasks_menu.add_command(label = "Редактировать",
                                           command = finish_tasks)
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Удалить",
                                          command = delete_tasks)
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Новая задача",
                                          command = new_tasks)
                    tasks_menu.add_command(label = "Завершить задачи",
                                           command = finish_all_tasks_in_window)
                else:
                    tasks_menu = Menu(tearoff = False)
                    tasks_menu.add_command(label = "Редактировать",
                                           command = finish_tasks,
                                           state = 'disabled')
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Удалить",
                                          command = delete_tasks)
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Новая задача",
                                          command = new_tasks)
                    tasks_menu.add_command(label = "Завершить задачи",
                                           command = finish_all_tasks_in_window) 
                tasks_menu.post(event.x_root, event.y_root)
                tasks_window.focus()

            def tasks_popupFocusOut(event):
                global tasks_menu
                tasks_menu.unpost()

            def tasks_exit():
                tasks_window.destroy()
            def tasks_exit_event(event):
                tasks_window.destroy()
            
            tasks_window = Toplevel()
            tasks_window.grab_set()
            tasks_window.title("Задачи для сделки \'{}\'".format(tasks_values[0]))
            tasks_window.resizable(True, True)
            tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
            tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"
            w = tasks_window.winfo_screenwidth()
            h = tasks_window.winfo_screenheight()
            w = int(w//2.2)
            h = int(h//2.5)
            tasks_window.geometry("{}x{}+200+200".format(w, h))
            tasks_window.minsize(w, h)

            tasks_frame_label = LabelFrame(tasks_window)
            tasks_frame_label.pack(fill = X, expand = False)
            tasks_frame_1 = LabelFrame(tasks_window)
            tasks_frame_1.pack(fill = BOTH, expand = True)
            tasks_frame_2 = Frame(tasks_window)
            tasks_frame_2.pack(fill = X, expand = False)

            tasks_frame_3 = LabelFrame(tasks_window)
            tasks_frame_3.pack(fill = X, expand = False)
            tasks_lbl_green = Label(tasks_frame_label, width = 2, bg = 'lightgreen')
            tasks_lbl_red = Label(tasks_frame_label, width = 2, bg = 'pink')
            tasks_lbl_grey = Label(tasks_frame_label, width = 2, bg = 'lightgrey')

            tasks_green_radio_btn = ttk.Checkbutton(tasks_frame_label)
            tasks_red_radio_btn = ttk.Checkbutton(tasks_frame_label)
            tasks_grey_radio_btn = ttk.Checkbutton(tasks_frame_label)

            tasks_lbl_green.pack(side = LEFT, expand = False)
            tasks_green_radio_btn.pack(side = LEFT, expand = False)
            tasks_lbl_red.pack(side = LEFT, expand = False)
            tasks_red_radio_btn.pack(side = LEFT, expand = False)
            tasks_lbl_grey.pack(side = LEFT, expand = False)
            tasks_grey_radio_btn.pack(side = LEFT, expand = False)

            tasks_green_radio_btn.bind("<ButtonRelease-1>", tasksview_event)
            tasks_red_radio_btn.bind("<ButtonRelease-1>", tasksview_event)
            tasks_grey_radio_btn.bind("<ButtonRelease-1>", tasksview_event)
            
            tasks_AZ_filter = ttk.Combobox(tasks_frame_label, values = ["А-Я", "Я-А"], state = 'readonly', width = 4)
            tasks_AZ_filter.pack(side = LEFT, expand = False)
            tasks_AZ_filter.current(0)
            tasks_AZ_filter.bind("<<ComboboxSelected>>", tasksview_event)
            
            tasks_list = ttk.Treeview(tasks_frame_1, show = "headings")
            tasks_list.tag_configure('green', background = 'lightgreen')
            tasks_list.tag_configure('red', background = 'pink')
            tasks_list.tag_configure('grey', background = 'lightgrey')
            tasks_list.bind("<Double-Button-1>", finish_tasks_event)
            tasks_list.bind("<Button-3>", tasks_popup)
            tasks_list.bind("<FocusIn>", tasks_popupFocusOut)
            tasks_list.bind("<Return>", finish_tasks_event)
            tasks_list.bind("<Delete>", delete_tasks_event)

            tasks_list['columns']=["Срок завершения", "Описание задачи", "Отметка о выполнении"]
            for header in ["Срок завершения", "Описание задачи", "Отметка о выполнении"]:
                tasks_list.heading(header, text = header, anchor = 'w')
                tasks_list.column('{}'.format(header))

            tasks_scroll_y = ttk.Scrollbar(tasks_frame_1, command = tasks_list.yview)#Создаем вертикальную полосу прокрутки для дерева сделок во фрейме frame3_in_file_cabinet
            tasks_list.configure(yscrollcommand = tasks_scroll_y.set)#Конфигурируем дерево контактов на зависимость от вертикальной полосы прокрутки
            tasks_scroll_y.pack(side = LEFT, fill = Y)#Упаковываем вертикальную полосу прокрутки в левой стороне фрейма, растягиваем вертикально по фрейму
            tasks_list.pack(side = LEFT, fill = BOTH, expand = True)#Упаковываем дерево контакта рядом с полосой прокрутки, растягиваем на всю оставшуюся область фрейма
            tasks_scroll_x = ttk.Scrollbar (tasks_frame_2, orient="horizontal", command = tasks_list.xview)#Создаем горизонтальную полосу прокрутки, устанавливаем горизонтальную ориентацию, привязываем к дереву контактов
            tasks_list.configure(xscrollcommand = tasks_scroll_x.set)#Конфигурируем дерево контактов на зависимость от горизонтальной полосы прокрутки
            tasks_scroll_x.pack(fill = X)#Упаковываем горизонтальную полосу, растягиваем по оси X

            tasks_exit_btn = Button(tasks_frame_3, text = "Выход",
                                    command = tasks_exit)
            tasks_exit_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_exit_btn.bind("<Return>", tasks_exit_event)
            tasks_exit_btn.focus()
            tasks_edit_btn = Button(tasks_frame_3, text = "Редактировать",
                                    command = finish_tasks)
            tasks_edit_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_edit_btn.bind("<Return>", finish_tasks_event)
            tasks_delete_in_btn = Button(tasks_frame_3, text = "Удалить",
                                    command = delete_tasks)
            tasks_delete_in_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_delete_in_btn.bind("<Return>", delete_tasks_event)
            tasks_newtasks_btn = Button(tasks_frame_3, text = "Новая",
                                    command = new_tasks)
            tasks_newtasks_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_newtasks_btn.bind("<Return>", new_tasks_event)
            tasksview()
        else:
            msg.showerror("Внимание", "Выберите сделку для отображения списка задач")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")
def tasks_show_event(event):
    try:
        tasks_values = transactions.item(transactions.selection(), option="values")
        if tasks_values != "":
            global save_tasks_str, save_tasks
            for i in trans_data:
                if i[0] == tasks_values[0] and i[1] == tasks_values[1] and i[2] == tasks_values[2] and i[3] == tasks_values[3]:
                    save_tasks_str = i[4]
            save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]

            def tasksview():
                tasks_list.delete(*tasks_list.get_children())
                global save_tasks_str, save_tasks
                for i in trans_data:
                    if i[0] == tasks_values[0] and i[1] == tasks_values[1] and i[2] == tasks_values[2] and i[3] == tasks_values[3]:
                        save_tasks_str = i[4]
                save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
                green_save_tasks = []
                red_save_tasks = []
                grey_save_tasks = []
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            grey_save_tasks.append(row)
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                green_save_tasks.append(row)
                            else:
                                red_save_tasks.append(row)
                save_tasks = []
                if tasks_green_radio_btn.state() == ('alternate',) or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_green_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + green_save_tasks
                if tasks_red_radio_btn.state() == ('alternate',) or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_red_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + red_save_tasks
                if tasks_grey_radio_btn.state() == ('alternate',) or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_grey_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + grey_save_tasks
                A = []
                for i in save_tasks:
                    i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                    A.append(i)
                A_Z = tasks_AZ_filter.get()
                if A_Z == "А-Я":
                    A = sorted(A)
                    B = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        B.append(i)
                    save_tasks = B
                else:
                    A = sorted(A, reverse = True)
                    C = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        C.append(i)
                    save_tasks = C
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            tag_row = 'grey'
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                tag_row = 'green'
                            else:
                                tag_row = 'red'
                        tasks_list.insert(
                                parent = '',
                                index = 'end',
                                values = row,
                                tag = '{}'.format(tag_row)
                                )
                else:
                    tasks_list.delete(*tasks_list.get_children())
            def tasksview_event(event):
                tasks_list.delete(*tasks_list.get_children())
                global save_tasks_str, save_tasks
                for i in trans_data:
                    if i[0] == tasks_values[0] and i[1] == tasks_values[1] and i[2] == tasks_values[2] and i[3] == tasks_values[3]:
                        save_tasks_str = i[4]
                save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
                green_save_tasks = []
                red_save_tasks = []
                grey_save_tasks = []
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            grey_save_tasks.append(row)
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                green_save_tasks.append(row)
                            else:
                                red_save_tasks.append(row)
                save_tasks = []
                if tasks_green_radio_btn.state() == ('alternate',) or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_green_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_green_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + green_save_tasks
                if tasks_red_radio_btn.state() == ('alternate',) or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_red_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_red_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + red_save_tasks
                if tasks_grey_radio_btn.state() == ('alternate',) or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'alternate', 'hover') or tasks_grey_radio_btn.state() == ('active', 'focus', 'pressed', 'hover') or tasks_grey_radio_btn.state() == ('selected',):
                    save_tasks = save_tasks + grey_save_tasks
                A = []
                for i in save_tasks:
                    i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                    A.append(i)
                A_Z = tasks_AZ_filter.get()
                if A_Z == "А-Я":
                    A = sorted(A)
                    B = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        B.append(i)
                    save_tasks = B
                else:
                    A = sorted(A, reverse = True)
                    C = []
                    for i in A:
                        i[0] = str(i[0].split(" ")[0].split(".")[2] +"."+ i[0].split(" ")[0].split(".")[1] +"."+ i[0].split(" ")[0].split(".")[0] +" "+ i[0].split(" ")[1])
                        C.append(i)
                    save_tasks = C
                if save_tasks != [['']]:
                    for row in save_tasks:
                        if row[2] != '':
                            tag_row = 'grey'
                        elif row[2] == '':
                            if time_str_replace(row[0]) >= time_str_reverse():
                                tag_row = 'green'
                            else:
                                tag_row = 'red'
                        tasks_list.insert(
                                parent = '',
                                index = 'end',
                                values = row,
                                tag = '{}'.format(tag_row)
                                )
                else:
                    tasks_list.delete(*tasks_list.get_children())

            def tasks_add(tasks_list):
                try:
                    sqlite_connections = sqlite3.connect(r'db\db.db')
                    cursor = sqlite_connections.cursor()
                    print_log("DB OPEN")
                    cursor.execute("""UPDATE trans SET Задачи = '{}' WHERE Сделка = '{}'
                                                    AND Компания = '{}'
                                                    AND Дата = '{}'
                                                    AND Обязательства = '{}'""".format(tasks_list, tasks_values[0],
                                                                                    tasks_values[1],
                                                                                    tasks_values[2],
                                                                                    tasks_values[3]))
                    sqlite_connections.commit()
                    cursor.close()
                except sqlite3.Error as error:
                    print_log("DB ERROR")
                    print_log(error)
                    msg.showerror("Внимание", "Произошла ошибка при добавления задания. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                finally:
                    if (sqlite_connections):
                        sqlite_connections.close()
                        print_log("DB CLOSE")  

            def finish_tasks():
                try:
                    finish_tasks_values = tasks_list.item(tasks_list.selection(), option="values")
                    if finish_tasks_values != "":
                        global replace_finish_tasks_values
                        replace_finish_tasks_values = "("+str([[x] for x in finish_tasks_values])[1:-1].replace("'", "")+")"
                        finish_tasks_window = Toplevel()
                        finish_tasks_window.grab_set()
                        finish_tasks_window.title("Редактировать задачу для сделки \'{}\'".format(tasks_values[0]))
                        finish_tasks_window.resizable(False, False)
                        finish_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                        finish_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                        def finish_tasks_window_quit():
                            finish_tasks_window.destroy()
                        def finish_tasks_window_quit_event(event):
                            finish_tasks_window.destroy()

                        def finish_tasks_save_func():
                            finish_tasks_hour_get = finish_tasks_hour.get()
                            finish_tasks_minute_get = finish_tasks_minute.get()
                            finish_tasks_second_get = finish_tasks_second.get()
                            finish_tasks_date_get = finish_tasks_date.get()
                            finish_tasks_text_get = finish_tasks_text.get(1.0, END).replace("\n", "").replace("\'", "")
                            fin_text = finish_entry.get().replace("\'", "")
                            finish_tasks_add_list_get = str([["{} {}:{}:{}".format(finish_tasks_date_get,
                                                                            finish_tasks_hour_get,
                                                                            finish_tasks_minute_get,
                                                                            finish_tasks_second_get)],
                                                      [finish_tasks_text_get], [fin_text]]).replace("'", "")
                            finish_save_tasks_get = str("{}, ({})".format(save_tasks_str, finish_tasks_add_list_get[1:-1]))
                            tasks_add(finish_save_tasks_get)
                            show()
                            tasksview()
                            trans_view_not_event()
                            global replace_finish_tasks_values
                            tasks_add(save_tasks_str.replace(", {}".format(replace_finish_tasks_values), "").replace("{}, ".format(replace_finish_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                            replace_finish_tasks_values = "("+finish_tasks_add_list_get[1:-1]+")"
                        
                        def finish_calendar_tomorrow():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            if now_day == "31":
                                tomorrow_day = "01"
                                if now_month == "12":
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)    
                                else:
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                            elif now_day == "30":
                                if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tommorrow_month = now_month
                                    tommorrow_year = now_year
                            elif now_day == "29":
                                if now_month == "02":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "28":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                tomorrow_day = str(int(now_day)+1)
                                if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                                    
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_week():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 21:
                                tomorrow_day = str(int(now_day)+7)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            elif now_day == "22":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = now_month
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "23":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "24":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "03"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                minus = int(now_day)-25
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = str(3+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = str(4+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = str(2+minus)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                elif now_month == "12":
                                    tomorrow_day = "01"
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_month():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 28:
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "29" or now_day == "30":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "31":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                                    tomorrow_day = "30"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        #Создание функции вызова контекстного меню
                        def finish_tasks_text_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_tasks_text_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_tasks_text_popupFocusOut(event):
                            finish_tasks_text_con_menu.unpost()
                        def finish_tasks_text_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_tasks_text.selection_get())
                            except :
                                return
                        def finish_tasks_text_paste_cl():
                            try:
                                finish_tasks_text.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_tasks_text_con_menu = Menu(tearoff = False)
                        finish_tasks_text_con_menu.add_command(label = "Копировать", command = finish_tasks_text_copy_selection)
                        finish_tasks_text_con_menu.add_command(label = "Вставить", command = finish_tasks_text_paste_cl)

                        #Создание функции вызова контекстного меню
                        def finish_entry_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_entry_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_entry_popupFocusOut(event):
                            finish_entry_con_menu.unpost()
                        def finish_entry_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_entry.selection_get())
                            except :
                                return
                        def finish_entry_paste_cl():
                            try:
                                finish_entry.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_entry_con_menu = Menu(tearoff = False)
                        finish_entry_con_menu.add_command(label = "Копировать", command = finish_entry_copy_selection)
                        finish_entry_con_menu.add_command(label = "Вставить", command = finish_entry_paste_cl)

                        finish_tasks_frame_1 = LabelFrame(finish_tasks_window, text = "Срок завершения")
                        finish_tasks_frame_1.pack(fill = X, expand = True)

                        finish_lbl_hour = Label(finish_tasks_frame_1,
                                                text = "Час/Мин/Сек:", width = 15)
                        finish_lbl_hour.pack(side = LEFT, expand = False)
                        finish_tasks_hour = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=23,
                                        width = 5, state = 'readonly')
                        finish_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_hour.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[0]))
                        finish_tasks_minute = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_minute.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[1]))
                        finish_tasks_second = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_second.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[2]))
                        finish_lbl_date = Label(finish_tasks_frame_1, text = "Дата:", width = 8)
                        finish_lbl_date.pack(side = LEFT, expand = False)
                        finish_tasks_date = DateEntry(finish_tasks_frame_1, width = 15,
                                                      locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                                      state = 'readonly')
                        finish_tasks_date.pack(side = LEFT, expand = False)
                        finish_tasks_date.delete(0, END)
                        finish_tasks_date.insert(0, "{}".format(finish_tasks_values[0].split(" ")[0]))

                        finish_tasks_frame_btn = LabelFrame(finish_tasks_window)
                        finish_tasks_frame_btn.pack(fill = X, expand = True)
                        finish_tasks_btn_tomorrow = Button(finish_tasks_frame_btn, text = "Завтра",
                                                        width = 17, command = finish_calendar_tomorrow)
                        finish_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_week = Button(finish_tasks_frame_btn, text = "Через неделю",
                                                    width = 17, command = finish_calendar_week)
                        finish_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_month = Button(finish_tasks_frame_btn, text = "Через месяц",
                                                     width = 17, command = finish_calendar_month)
                        finish_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)

                        finish_tasks_lbl_frame = LabelFrame(finish_tasks_window,
                                                            text = "Описание задачи")
                        finish_tasks_lbl_frame.pack(fill = BOTH, expand = True)
                        finish_tasks_text = Text(finish_tasks_lbl_frame, height = 5, width = 50)
                        finish_tasks_text.pack(fill = BOTH, expand = True)
                        finish_tasks_text.insert(1.0, "{}".format(finish_tasks_values[1]))
                        finish_tasks_text.bind("<Button-3>", finish_tasks_text_popup)
                        finish_tasks_text.bind("<FocusIn>", finish_tasks_text_popupFocusOut)  
                        finish_tasks_text.bind("<Control-C>", finish_tasks_text_copy_selection)
                        finish_tasks_text.bind("<Control-V>", finish_tasks_text_paste_cl)
                        def finish_tasks_text_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_tasks_text_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_tasks_text_paste_cl()
                        finish_tasks_text.bind("<Key>", finish_tasks_text_key_callback)

                        finish_text_frame = LabelFrame(finish_tasks_window, text = "Отметка о выполнении")
                        finish_text_frame.pack(fill = BOTH, expand = True)
                        finish_entry = Entry(finish_text_frame)
                        finish_entry.insert(END, "{}".format(finish_tasks_values[2]))
                        finish_entry.pack(side = LEFT, fill = X, expand = True)
                        finish_entry.bind("<Button-3>", finish_entry_popup)
                        finish_entry.bind("<FocusIn>", finish_entry_popupFocusOut)  
                        finish_entry.bind("<Control-C>", finish_entry_copy_selection)
                        finish_entry.bind("<Control-V>", finish_entry_paste_cl)
                        def finish_entry_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_entry_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_entry_paste_cl()
                        finish_entry.bind("<Key>", finish_entry_key_callback)

                        finish_tasks_save_btn = Button(finish_text_frame, width = 15, text = "Сохранить",
                                                       command = finish_tasks_save_func)
                        finish_tasks_save_btn.pack(side = LEFT, fill = BOTH, expand = False, padx = 1, pady = 1)
                        finish_tasks_cancel_btn = Button(finish_text_frame, width = 15, text = "Закрыть",
                                                         command = finish_tasks_window_quit)
                        finish_tasks_cancel_btn.pack(side = LEFT, fill = BOTH, expand = False,padx = 1, pady = 1)
                        finish_tasks_cancel_btn.bind("<Return>", finish_tasks_window_quit_event)
                        finish_tasks_cancel_btn.focus()
                    else:
                        tasks_window.attributes("-topmost", False)
                        if msg.showerror("Внимание", "Выберите задачу для редактирования"):
                            tasks_window.attributes("-topmost", True)
                except TclError:
                    tasks_window.attributes("-topmost", False)
                    if msg.showinfo("Внимание", "Множественное редактирование не поддерживается"):
                        tasks_window.attributes("-topmost", True)
            def finish_tasks_event(event):
                try:
                    finish_tasks_values = tasks_list.item(tasks_list.selection(), option="values")
                    if finish_tasks_values != "":
                        global replace_finish_tasks_values
                        replace_finish_tasks_values = "("+str([[x] for x in finish_tasks_values])[1:-1].replace("'", "")+")"
                        finish_tasks_window = Toplevel()
                        finish_tasks_window.grab_set()
                        finish_tasks_window.title("Редактировать задачу для сделки \'{}\'".format(tasks_values[0]))
                        finish_tasks_window.resizable(False, False)
                        finish_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                        finish_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                        def finish_tasks_window_quit():
                            finish_tasks_window.destroy()
                        def finish_tasks_window_quit_event(event):
                            finish_tasks_window.destroy()


                        def finish_tasks_save_func():
                            finish_tasks_hour_get = finish_tasks_hour.get()
                            finish_tasks_minute_get = finish_tasks_minute.get()
                            finish_tasks_second_get = finish_tasks_second.get()
                            finish_tasks_date_get = finish_tasks_date.get()
                            finish_tasks_text_get = finish_tasks_text.get(1.0, END).replace("\n", "").replace("\'", "")
                            fin_text = finish_entry.get().replace("\'", "")
                            finish_tasks_add_list_get = str([["{} {}:{}:{}".format(finish_tasks_date_get,
                                                                            finish_tasks_hour_get,
                                                                            finish_tasks_minute_get,
                                                                            finish_tasks_second_get)],
                                                      [finish_tasks_text_get], [fin_text]]).replace("'", "")
                            finish_save_tasks_get = str("{}, ({})".format(save_tasks_str, finish_tasks_add_list_get[1:-1]))
                            tasks_add(finish_save_tasks_get)
                            show()
                            tasksview()
                            trans_view_not_event()
                            global replace_finish_tasks_values
                            tasks_add(save_tasks_str.replace(", {}".format(replace_finish_tasks_values), "").replace("{}, ".format(replace_finish_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                            replace_finish_tasks_values = "("+finish_tasks_add_list_get[1:-1]+")"
                        
                        def finish_calendar_tomorrow():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            if now_day == "31":
                                tomorrow_day = "01"
                                if now_month == "12":
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)    
                                else:
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                            elif now_day == "30":
                                if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tommorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tommorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tommorrow_month = now_month
                                    tommorrow_year = now_year
                            elif now_day == "29":
                                if now_month == "02":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "28":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+1)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                tomorrow_day = str(int(now_day)+1)
                                if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                                    
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_week():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 21:
                                tomorrow_day = str(int(now_day)+7)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            elif now_day == "22":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = now_month
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "23":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "01"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            elif now_day == "24":
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "02"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "03"
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = "01"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            else:
                                minus = int(now_day)-25
                                if now_month == "02":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = str(3+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = str(4+minus)
                                        if len(tomorrow_day) == 1:
                                            tomorrow_day = "0"+tomorrow_day
                                        tomorrow_month = "03"
                                        tomorrow_year = now_year
                                elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                                    tomorrow_day = str(2+minus)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                elif now_month == "12":
                                    tomorrow_day = "01"
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = str(int(now_day)+7)
                                    if len(tomorrow_day) == 1:
                                        tomorrow_day = "0"+tomorrow_day
                                    tomorrow_month = now_month
                                    tomorrow_year = now_year
                            
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        def finish_calendar_month():
                            now_year = time_str().split(" ")[0].split(".")[2]
                            now_month = time_str().split(" ")[0].split(".")[1]
                            now_day = time_str().split(" ")[0].split(".")[0]
                            finish_tasks_date.configure(state = 'normal')
                            finish_tasks_date.delete(0, END)

                            if int(now_day) <= 28:
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "29" or now_day == "30":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                else:
                                    tomorrow_day = now_day
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            elif now_day == "31":
                                if now_month == "12":
                                    tomorrow_day = now_day
                                    tomorrow_month = "01"
                                    tomorrow_year = str(int(now_year)+1)
                                elif now_month == "01":
                                    if int(now_year)%4 == 0:
                                        tomorrow_day = "29"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                    else:
                                        tomorrow_day = "28"
                                        tomorrow_month = "02"
                                        tomorrow_year = now_year
                                elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                                    tomorrow_day = "30"
                                    tomorrow_month = str(int(now_month)+1)
                                    if len(tomorrow_month) == 1:
                                        tomorrow_month = "0"+tomorrow_month
                                    tomorrow_year = now_year
                            finish_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                            finish_tasks_date.configure(state = 'readonly')

                        #Создание функции вызова контекстного меню
                        def finish_tasks_text_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_tasks_text_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_tasks_text_popupFocusOut(event):
                            finish_tasks_text_con_menu.unpost()
                        def finish_tasks_text_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_tasks_text.selection_get())
                            except :
                                return
                        def finish_tasks_text_paste_cl():
                            try:
                                finish_tasks_text.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_tasks_text_con_menu = Menu(tearoff = False)
                        finish_tasks_text_con_menu.add_command(label = "Копировать", command = finish_tasks_text_copy_selection)
                        finish_tasks_text_con_menu.add_command(label = "Вставить", command = finish_tasks_text_paste_cl)

                        #Создание функции вызова контекстного меню
                        def finish_entry_popup(event):
                            global x, y
                            x = event.x
                            y = event.y
                            finish_entry_con_menu.post(event.x_root, event.y_root)
                            root.focus()

                        def finish_entry_popupFocusOut(event):
                            finish_entry_con_menu.unpost()
                        def finish_entry_copy_selection():
                            try:
                                root.clipboard_clear()
                                root.clipboard_append(finish_entry.selection_get())
                            except :
                                return
                            #root.after(10, copy_selection2, widget)
                        def finish_entry_paste_cl():
                            try:
                                finish_entry.insert(INSERT, root.clipboard_get())
                            except :
                                return
                            
                        finish_entry_con_menu = Menu(tearoff = False)
                        finish_entry_con_menu.add_command(label = "Копировать", command = finish_entry_copy_selection)
                        finish_entry_con_menu.add_command(label = "Вставить", command = finish_entry_paste_cl)


                        finish_tasks_frame_1 = LabelFrame(finish_tasks_window, text = "Срок завершения")
                        finish_tasks_frame_1.pack(fill = X, expand = True)

                        finish_lbl_hour = Label(finish_tasks_frame_1,
                                                text = "Час/Мин/Сек:", width = 15)
                        finish_lbl_hour.pack(side = LEFT, expand = False)
                        finish_tasks_hour = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=23,
                                        width = 5, state = 'readonly')
                        finish_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_hour.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[0]))
                        finish_tasks_minute = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_minute.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[1]))
                        finish_tasks_second = ttk.Spinbox(finish_tasks_frame_1, from_=0, to_=59,
                                        width = 5, state = 'readonly')
                        finish_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                        finish_tasks_second.set("{}".format(finish_tasks_values[0].split(" ")[1].split(":")[2]))
                        finish_lbl_date = Label(finish_tasks_frame_1, text = "Дата:", width = 8)
                        finish_lbl_date.pack(side = LEFT, expand = False)
                        finish_tasks_date = DateEntry(finish_tasks_frame_1, width = 15,
                                                      locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                                      state = 'readonly')
                        finish_tasks_date.pack(side = LEFT, expand = False)
                        finish_tasks_date.delete(0, END)
                        finish_tasks_date.insert(0, "{}".format(finish_tasks_values[0].split(" ")[0]))

                        finish_tasks_frame_btn = LabelFrame(finish_tasks_window)
                        finish_tasks_frame_btn.pack(fill = X, expand = True)
                        finish_tasks_btn_tomorrow = Button(finish_tasks_frame_btn, text = "Завтра",
                                                        width = 17, command = finish_calendar_tomorrow)
                        finish_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_week = Button(finish_tasks_frame_btn, text = "Через неделю",
                                                    width = 17, command = finish_calendar_week)
                        finish_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                        finish_tasks_btn_month = Button(finish_tasks_frame_btn, text = "Через месяц",
                                                     width = 17, command = finish_calendar_month)
                        finish_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)

                        finish_tasks_lbl_frame = LabelFrame(finish_tasks_window,
                                                            text = "Описание задачи")
                        finish_tasks_lbl_frame.pack(fill = BOTH, expand = True)
                        finish_tasks_text = Text(finish_tasks_lbl_frame, height = 5, width = 50)
                        finish_tasks_text.pack(fill = BOTH, expand = True)
                        finish_tasks_text.insert(1.0, "{}".format(finish_tasks_values[1]))
                        finish_tasks_text.bind("<Button-3>", finish_tasks_text_popup)
                        finish_tasks_text.bind("<FocusIn>", finish_tasks_text_popupFocusOut)  
                        finish_tasks_text.bind("<Control-C>", finish_tasks_text_copy_selection)
                        finish_tasks_text.bind("<Control-V>", finish_tasks_text_paste_cl)
                        def finish_tasks_text_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_tasks_text_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_tasks_text_paste_cl()
                        finish_tasks_text.bind("<Key>", finish_tasks_text_key_callback)

                        finish_text_frame = LabelFrame(finish_tasks_window, text = "Отметка о выполнении")
                        finish_text_frame.pack(fill = BOTH, expand = True)
                        finish_entry = Entry(finish_text_frame)
                        finish_entry.insert(END, "{}".format(finish_tasks_values[2]))
                        finish_entry.pack(side = LEFT, fill = X, expand = True)
                        finish_entry.bind("<Button-3>", finish_entry_popup)
                        finish_entry.bind("<FocusIn>", finish_entry_popupFocusOut)  
                        finish_entry.bind("<Control-C>", finish_entry_copy_selection)
                        finish_entry.bind("<Control-V>", finish_entry_paste_cl)
                        def finish_entry_key_callback(event):
                            if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                                if chr(event.keycode) == "C":
                                    finish_entry_copy_selection()
                                elif chr(event.keycode) == "V":
                                    finish_entry_paste_cl()
                        finish_entry.bind("<Key>", finish_entry_key_callback)

                        finish_tasks_save_btn = Button(finish_text_frame, width = 15, text = "Сохранить",
                                                       command = finish_tasks_save_func)
                        finish_tasks_save_btn.pack(side = LEFT, fill = BOTH, expand = False, padx = 1, pady = 1)
                        finish_tasks_cancel_btn = Button(finish_text_frame, width = 15, text = "Закрыть",
                                                         command = finish_tasks_window_quit)
                        finish_tasks_cancel_btn.pack(side = LEFT, fill = BOTH, expand = False,padx = 1, pady = 1)
                        finish_tasks_cancel_btn.bind("<Return>", finish_tasks_window_quit_event)
                        finish_tasks_cancel_btn.focus()
                    else:
                        tasks_window.attributes("-topmost", False)
                        if msg.showerror("Внимание", "Выберите задачу для редактирования"):
                            tasks_window.attributes("-topmost", True)
                except TclError:
                    tasks_window.attributes("-topmost", False)
                    if msg.showinfo("Внимание", "Множственное редактирование не поддерживается"):
                        tasks_window.attributes("-topmost", True)

            def delete_tasks():
                delete_tasks_valueses = [tasks_list.item(x, option="values") for x in tasks_list.selection()]
                if delete_tasks_valueses != []:
                    tasks_window.attributes("-topmost", False)
                    if msg.askyesno("Внимание", "Удалить выбранные задачи?"):
                        for delete_tasks_values in delete_tasks_valueses:
                            replace_delete_tasks_values = "("+str([[x] for x in delete_tasks_values])[1:-1].replace("'", "")+")"
                            tasks_add(save_tasks_str.replace(", {}".format(replace_delete_tasks_values), "").replace("{}, ".format(replace_delete_tasks_values), "").replace("{}".format(replace_delete_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                        tasks_window.attributes("-topmost", True)
                    tasks_window.attributes("-topmost", True)
                else:
                    tasks_window.attributes("-topmost", False)
                    if msg.showerror("Внимание", "Выберите задачу для удаления"):
                        tasks_window.attributes("-topmost", True)
            def delete_tasks_event(event):
                delete_tasks_valueses = [tasks_list.item(x, option="values") for x in tasks_list.selection()]
                if delete_tasks_valueses != []:
                    tasks_window.attributes("-topmost", False)
                    if msg.askyesno("Внимание", "Удалить выбранные задачи?"):
                        for delete_tasks_values in delete_tasks_valueses:
                            replace_delete_tasks_values = "("+str([[x] for x in delete_tasks_values])[1:-1].replace("'", "")+")"
                            tasks_add(save_tasks_str.replace(", {}".format(replace_delete_tasks_values), "").replace("{}, ".format(replace_delete_tasks_values), "").replace("{}".format(replace_delete_tasks_values), ""))
                            show()
                            tasksview()
                            trans_view_not_event()
                        tasks_window.attributes("-topmost", True)
                    tasks_window.attributes("-topmost", True)
                else:
                    tasks_window.attributes("-topmost", False)
                    if msg.showerror("Внимание", "Выберите задачу для удаления"):
                        tasks_window.attributes("-topmost", True)

            def new_tasks():
                new_tasks_window = Toplevel()
                new_tasks_window.grab_set()
                new_tasks_window.title("Новая задача для сделки \'{}\'".format(tasks_values[0]))
                new_tasks_window.resizable(False, False)
                new_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                new_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                def new_tasks_add():
                    new_tasks_hour_get = new_tasks_hour.get()
                    new_tasks_minute_get = new_tasks_minute.get()
                    new_tasks_second_get = new_tasks_second.get()
                    new_tasks_date_get = new_tasks_date.get()
                    new_tasks_text_get = text_tasks.get(1.0, END).replace("\n", "").replace("\'", "")
                    new_tasks_add_list_get = str([["{} {}:{}:{}".format(new_tasks_date_get,
                                                                        new_tasks_hour_get,
                                                                        new_tasks_minute_get,
                                                                        new_tasks_second_get)],
                                                  [new_tasks_text_get], []]).replace("'", "")
                    if save_tasks == []:
                        new_save_tasks_get = str("({})".format(new_tasks_add_list_get[1:-1]))
                    else:
                        new_save_tasks_get = str("{}, ({})".format(save_tasks_str, new_tasks_add_list_get[1:-1]))
                    tasks_add(new_save_tasks_get)
                    show()
                    tasksview()
                    trans_view_not_event()

                def calendar_tomorrow():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    if now_day == "31":
                        tomorrow_day = "01"
                        if now_month == "12":
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)    
                        else:
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                    elif now_day == "30":
                        if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tommorrow_month = now_month
                            tommorrow_year = now_year
                    elif now_day == "29":
                        if now_month == "02":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "28":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        tomorrow_day = str(int(now_day)+1)
                        if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                            
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_week():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 21:
                        tomorrow_day = str(int(now_day)+7)
                        if len(tomorrow_day) == 1:
                            tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                    elif now_day == "22":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "23":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "24":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "03"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        minus = int(now_day)-25
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = str(3+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = str(4+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = str(2+minus)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        elif now_month == "12":
                            tomorrow_day = "01"
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_month():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 28:
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "29" or now_day == "30":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "31":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                            tomorrow_day = "30"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                #Создание функции вызова контекстного меню
                def text_tasks_popup(event):
                    global x, y
                    x = event.x
                    y = event.y
                    text_tasks_con_menu.post(event.x_root, event.y_root)
                    root.focus()

                def text_tasks_popupFocusOut(event):
                    text_tasks_con_menu.unpost()
                def text_tasks_copy_selection():
                    try:
                        root.clipboard_clear()
                        root.clipboard_append(text_tasks.selection_get())
                    except :
                        return
                    #root.after(10, copy_selection2, widget)
                def text_tasks_paste_cl():
                    try:
                        text_tasks.insert(INSERT, root.clipboard_get())
                    except :
                        return
                    
                text_tasks_con_menu = Menu(tearoff = False)
                text_tasks_con_menu.add_command(label = "Копировать", command = text_tasks_copy_selection)
                text_tasks_con_menu.add_command(label = "Вставить", command = text_tasks_paste_cl)

                new_tasks_frame_1 = LabelFrame(new_tasks_window, text = "Срок завершения")
                new_tasks_frame_1.pack(fill = X, expand = True)

                new_lbl_hour = Label(new_tasks_frame_1, text = "Час/Мин/Сек:", width = 15)
                new_lbl_hour.pack(side = LEFT, expand = False)
                new_tasks_hour = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=23,
                                width = 5, state = 'readonly')
                new_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_hour.set("12")
                new_tasks_minute = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_minute.set("00")
                new_tasks_second = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_second.set("00")
                new_lbl_date = Label(new_tasks_frame_1, text = "Дата:", width = 8)
                new_lbl_date.pack(side = LEFT, expand = False)
                new_tasks_date = DateEntry(new_tasks_frame_1, width = 15,
                                           locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                           state = 'readonly')
                new_tasks_date.pack(side = LEFT, expand = False)

                new_tasks_frame_btn = LabelFrame(new_tasks_window)
                new_tasks_frame_btn.pack(fill = X, expand = True)
                new_tasks_btn_tomorrow = Button(new_tasks_frame_btn, text = "Завтра",
                                                width = 17, command = calendar_tomorrow)
                new_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_week = Button(new_tasks_frame_btn, text = "Через неделю",
                                            width = 17, command = calendar_week)
                new_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_month = Button(new_tasks_frame_btn, text = "Через месяц",
                                             width = 17, command = calendar_month)
                new_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)
                
                new_tasks_frame_2 = LabelFrame(new_tasks_window, text = "Описание задачи")
                new_tasks_frame_2.pack(fill = X, expand = True)
                text_tasks = Text(new_tasks_frame_2, height = 3, width = 53)
                text_tasks.pack(fill = X, expand = True)
                text_tasks.bind("<Button-3>", text_tasks_popup)
                text_tasks.bind("<FocusIn>", text_tasks_popupFocusOut)  
                text_tasks.bind("<Control-C>", text_tasks_copy_selection)
                text_tasks.bind("<Control-V>", text_tasks_paste_cl)
                def text_tasks_key_callback(event):
                    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                        if chr(event.keycode) == "C":
                            text_tasks_copy_selection()
                        elif chr(event.keycode) == "V":
                            text_tasks_paste_cl()
                text_tasks.bind("<Key>", text_tasks_key_callback)

                new_tasks_frame_3 = LabelFrame(new_tasks_window)
                new_tasks_frame_3.pack(fill = X, expand = True)
                new_tasks_add_btn = Button(new_tasks_frame_3, text = "Добавить",
                                           width = 20, command = new_tasks_add)
                new_tasks_add_btn.pack(side = RIGHT, fill = BOTH, expand = False)
            def new_tasks_event(event):
                new_tasks_window = Toplevel()
                new_tasks_window.grab_set()
                new_tasks_window.title("Новая задача для сделки \'{}\'".format(tasks_values[0]))
                new_tasks_window.resizable(False, False)
                new_tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
                new_tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

                def new_tasks_add():
                    new_tasks_hour_get = new_tasks_hour.get()
                    new_tasks_minute_get = new_tasks_minute.get()
                    new_tasks_second_get = new_tasks_second.get()
                    new_tasks_date_get = new_tasks_date.get()
                    new_tasks_text_get = text_tasks.get(1.0, END).replace("\n", "").replace("\'", "")
                    new_tasks_add_list_get = str([["{} {}:{}:{}".format(new_tasks_date_get,
                                                                        new_tasks_hour_get,
                                                                        new_tasks_minute_get,
                                                                        new_tasks_second_get)],
                                                  [new_tasks_text_get], []]).replace("'", "")
                    if save_tasks == []:
                        new_save_tasks_get = str("({})".format(new_tasks_add_list_get[1:-1]))
                    else:
                        new_save_tasks_get = str("{}, ({})".format(save_tasks_str, new_tasks_add_list_get[1:-1]))
                    tasks_add(new_save_tasks_get)
                    show()
                    tasksview()
                    trans_view_not_event()

                def calendar_tomorrow():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    if now_day == "31":
                        tomorrow_day = "01"
                        if now_month == "12":
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)    
                        else:
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                    elif now_day == "30":
                        if now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tommorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tommorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tommorrow_month = now_month
                            tommorrow_year = now_year
                    elif now_day == "29":
                        if now_month == "02":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "28":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+1)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        tomorrow_day = str(int(now_day)+1)
                        if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                            
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_week():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 21:
                        tomorrow_day = str(int(now_day)+7)
                        if len(tomorrow_day) == 1:
                            tomorrow_day = "0"+tomorrow_day
                        tomorrow_month = now_month
                        tomorrow_year = now_year
                    elif now_day == "22":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = now_month
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "23":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "01"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    elif now_day == "24":
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "02"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "03"
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = "01"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    else:
                        minus = int(now_day)-25
                        if now_month == "02":
                            if int(now_year)%4 == 0:
                                tomorrow_day = str(3+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = str(4+minus)
                                if len(tomorrow_day) == 1:
                                    tomorrow_day = "0"+tomorrow_day
                                tomorrow_month = "03"
                                tomorrow_year = now_year
                        elif now_month == "04" or now_month == "06" or now_month == "09" or now_month == "11":
                            tomorrow_day = str(2+minus)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                        elif now_month == "12":
                            tomorrow_day = "01"
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = str(int(now_day)+7)
                            if len(tomorrow_day) == 1:
                                tomorrow_day = "0"+tomorrow_day
                            tomorrow_month = now_month
                            tomorrow_year = now_year
                    
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                def calendar_month():
                    now_year = time_str().split(" ")[0].split(".")[2]
                    now_month = time_str().split(" ")[0].split(".")[1]
                    now_day = time_str().split(" ")[0].split(".")[0]
                    new_tasks_date.configure(state = 'normal')
                    new_tasks_date.delete(0, END)

                    if int(now_day) <= 28:
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "29" or now_day == "30":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        else:
                            tomorrow_day = now_day
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    elif now_day == "31":
                        if now_month == "12":
                            tomorrow_day = now_day
                            tomorrow_month = "01"
                            tomorrow_year = str(int(now_year)+1)
                        elif now_month == "01":
                            if int(now_year)%4 == 0:
                                tomorrow_day = "29"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                            else:
                                tomorrow_day = "28"
                                tomorrow_month = "02"
                                tomorrow_year = now_year
                        elif now_month == "03" or now_month == "05" or now_month == "08" or now_month == "10":
                            tomorrow_day = "30"
                            tomorrow_month = str(int(now_month)+1)
                            if len(tomorrow_month) == 1:
                                tomorrow_month = "0"+tomorrow_month
                            tomorrow_year = now_year
                    new_tasks_date.insert(0, "{}.{}.{}".format(tomorrow_day, tomorrow_month, tomorrow_year))
                    new_tasks_date.configure(state = 'readonly')

                #Создание функции вызова контекстного меню
                def text_tasks_popup(event):
                    global x, y
                    x = event.x
                    y = event.y
                    text_tasks_con_menu.post(event.x_root, event.y_root)
                    root.focus()

                def text_tasks_popupFocusOut(event):
                    text_tasks_con_menu.unpost()
                def text_tasks_copy_selection():
                    try:
                        root.clipboard_clear()
                        root.clipboard_append(text_tasks.selection_get())
                    except :
                        return
                    #root.after(10, copy_selection2, widget)
                def text_tasks_paste_cl():
                    try:
                        text_tasks.insert(INSERT, root.clipboard_get())
                    except :
                        return
                    
                text_tasks_con_menu = Menu(tearoff = False)
                text_tasks_con_menu.add_command(label = "Копировать", command = text_tasks_copy_selection)
                text_tasks_con_menu.add_command(label = "Вставить", command = text_tasks_paste_cl)

                new_tasks_frame_1 = LabelFrame(new_tasks_window, text = "Срок завершения")
                new_tasks_frame_1.pack(fill = X, expand = True)

                new_lbl_hour = Label(new_tasks_frame_1, text = "Час/Мин/Сек:", width = 15)
                new_lbl_hour.pack(side = LEFT, expand = False)
                new_tasks_hour = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=23,
                                width = 5, state = 'readonly')
                new_tasks_hour.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_hour.set("12")
                new_tasks_minute = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_minute.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_minute.set("00")
                new_tasks_second = ttk.Spinbox(new_tasks_frame_1, from_=0, to_=59,
                                width = 5, state = 'readonly')
                new_tasks_second.pack(side = LEFT, fill = BOTH, expand = False)
                new_tasks_second.set("00")
                new_lbl_date = Label(new_tasks_frame_1, text = "Дата:", width = 8)
                new_lbl_date.pack(side = LEFT, expand = False)
                new_tasks_date = DateEntry(new_tasks_frame_1, width = 15,
                                           locale = 'ru_RU', date_pattern = 'dd.mm.y',
                                           state = 'readonly')
                new_tasks_date.pack(side = LEFT, expand = False)

                new_tasks_frame_btn = LabelFrame(new_tasks_window)
                new_tasks_frame_btn.pack(fill = X, expand = True)
                new_tasks_btn_tomorrow = Button(new_tasks_frame_btn, text = "Завтра",
                                                width = 17, command = calendar_tomorrow)
                new_tasks_btn_tomorrow.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_week = Button(new_tasks_frame_btn, text = "Через неделю",
                                            width = 17, command = calendar_week)
                new_tasks_btn_week.pack(side = LEFT, fill = BOTH, expand = True)
                new_tasks_btn_month = Button(new_tasks_frame_btn, text = "Через месяц",
                                             width = 17, command = calendar_month)
                new_tasks_btn_month.pack(side = LEFT, fill = BOTH, expand = True)
                
                new_tasks_frame_2 = LabelFrame(new_tasks_window, text = "Описание задачи")
                new_tasks_frame_2.pack(fill = X, expand = True)
                text_tasks = Text(new_tasks_frame_2, height = 3, width = 53)
                text_tasks.pack(fill = X, expand = True)
                text_tasks.bind("<Button-3>", text_tasks_popup)
                text_tasks.bind("<FocusIn>", text_tasks_popupFocusOut)  
                text_tasks.bind("<Control-C>", text_tasks_copy_selection)
                text_tasks.bind("<Control-V>", text_tasks_paste_cl)
                def text_tasks_key_callback(event):
                    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
                        if chr(event.keycode) == "C":
                            text_tasks_copy_selection()
                        elif chr(event.keycode) == "V":
                            text_tasks_paste_cl()
                text_tasks.bind("<Key>", text_tasks_key_callback)

                new_tasks_frame_3 = LabelFrame(new_tasks_window)
                new_tasks_frame_3.pack(fill = X, expand = True)
                new_tasks_add_btn = Button(new_tasks_frame_3, text = "Добавить",
                                           width = 20, command = new_tasks_add)
                new_tasks_add_btn.pack(side = RIGHT, fill = BOTH, expand = False)

            #Создание функции вызова контекстного меню для поля задач
            def tasks_popup(event):
                global x, y, tasks_menu
                x = event.x
                y = event.y
                valueses = [tasks_list.item(x, option="values") for x in tasks_list.selection()]
                def finish_all_tasks_in_window():
                    values_in_trans = [transactions.item(x, option="values") for x in transactions.selection()]
                    for values in values_in_trans:
                        for i in trans_data:
                            if i[0] == values[0] and i[1] == values[1] and i[2] == values[2] and i[3] == values[3]:
                                save_tasks_str = i[4]
                        save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
                    valueses_list = [list(x) for x in valueses]
                    for item in valueses_list:
                        if item[2].replace(" ", "") == '':
                            item[2] = '+'
                    for i in valueses_list:
                        for j in save_tasks:
                            if j[0] == i[0] and j[1] == i[1]:
                                j[2] = i[2]
                    save_tasks_replace_str = ""
                    for i in save_tasks:
                        i_str = ""
                        for element in i:
                            i_str += "["+str(element)+"], "
                        save_tasks_replace_str += "("+str(i_str[:-2]).replace("\'", "")+"), "
                    try:
                        sqlite_connections = sqlite3.connect(r'db\db.db')
                        cursor = sqlite_connections.cursor()
                        print_log("DB OPEN")
                        cursor.execute("""Update trans set Задачи = "{}" WHERE Сделка = '{}'
                                        AND Компания = '{}'
                                        AND Дата = '{}'
                                        AND Обязательства = '{}'""".format(save_tasks_replace_str[:-2],
                                                                            values_in_trans[0][0],
                                                                            values_in_trans[0][1],
                                                                            values_in_trans[0][2],
                                                                            values_in_trans[0][3]))
                        sqlite_connections.commit()
                        cursor.close()
                    except sqlite3.Error as error:
                        print_log("DB ERROR")
                        print_log(error)
                        msg.showerror("Внимание", "Произошла ошибка при чтении базы данных. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
                    finally:
                        if (sqlite_connections):
                            sqlite_connections.close()
                            print_log("DB CLOSE")
                    show()
                    tasksview()
                if len(valueses) == 0:
                    tasks_menu = Menu(tearoff = False)
                    tasks_menu.add_command(label = "Редактировать",
                                           command = finish_tasks,
                                           state = 'disabled')
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Удалить",
                                          command = delete_tasks,
                                           state = 'disabled')
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Новая задача",
                                          command = new_tasks)
                    tasks_menu.add_command(label = "Завершить задачи",
                                           command = finish_all_tasks_in_window,
                                           state = 'disabled')
                elif len(valueses) == 1:
                    tasks_menu = Menu(tearoff = False)
                    tasks_menu.add_command(label = "Редактировать",
                                           command = finish_tasks)
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Удалить",
                                          command = delete_tasks)
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Новая задача",
                                          command = new_tasks)
                    tasks_menu.add_command(label = "Завершить задачи",
                                           command = finish_all_tasks_in_window)
                else:
                    tasks_menu = Menu(tearoff = False)
                    tasks_menu.add_command(label = "Редактировать",
                                           command = finish_tasks,
                                           state = 'disabled')
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Удалить",
                                          command = delete_tasks)
                    tasks_menu.add_separator()
                    tasks_menu.add_command(label = "Новая задача",
                                          command = new_tasks)
                    tasks_menu.add_command(label = "Завершить задачи",
                                           command = finish_all_tasks_in_window) 
                tasks_menu.post(event.x_root, event.y_root)
                tasks_window.focus()

            def tasks_popupFocusOut(event):
                global tasks_menu
                tasks_menu.unpost()

            def tasks_exit():
                tasks_window.destroy()
            def tasks_exit_event(event):
                tasks_window.destroy()
            
            tasks_window = Toplevel()
            tasks_window.grab_set()
            tasks_window.title("Задачи для сделки \'{}\'".format(tasks_values[0]))
            tasks_window.resizable(True, True)
            tasks_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
            tasks_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"
            w = tasks_window.winfo_screenwidth()
            h = tasks_window.winfo_screenheight()
            w = int(w//2.2)
            h = int(h//2.5)
            tasks_window.geometry("{}x{}+200+200".format(w, h))
            tasks_window.minsize(w, h)

            tasks_frame_label = LabelFrame(tasks_window)
            tasks_frame_label.pack(fill = X, expand = False)
            tasks_frame_1 = LabelFrame(tasks_window)
            tasks_frame_1.pack(fill = BOTH, expand = True)
            tasks_frame_2 = Frame(tasks_window)
            tasks_frame_2.pack(fill = X, expand = False)

            tasks_frame_3 = LabelFrame(tasks_window)
            tasks_frame_3.pack(fill = X, expand = False)
            tasks_lbl_green = Label(tasks_frame_label, width = 2, bg = 'lightgreen')
            tasks_lbl_red = Label(tasks_frame_label, width = 2, bg = 'pink')
            tasks_lbl_grey = Label(tasks_frame_label, width = 2, bg = 'lightgrey')

            tasks_green_radio_btn = ttk.Checkbutton(tasks_frame_label)
            tasks_red_radio_btn = ttk.Checkbutton(tasks_frame_label)
            tasks_grey_radio_btn = ttk.Checkbutton(tasks_frame_label)

            tasks_lbl_green.pack(side = LEFT, expand = False)
            tasks_green_radio_btn.pack(side = LEFT, expand = False)
            tasks_lbl_red.pack(side = LEFT, expand = False)
            tasks_red_radio_btn.pack(side = LEFT, expand = False)
            tasks_lbl_grey.pack(side = LEFT, expand = False)
            tasks_grey_radio_btn.pack(side = LEFT, expand = False)

            tasks_green_radio_btn.bind("<ButtonRelease-1>", tasksview_event)
            tasks_red_radio_btn.bind("<ButtonRelease-1>", tasksview_event)
            tasks_grey_radio_btn.bind("<ButtonRelease-1>", tasksview_event)

            tasks_AZ_filter = ttk.Combobox(tasks_frame_label, values = ["А-Я", "Я-А"], state = 'readonly', width = 4)
            tasks_AZ_filter.pack(side = LEFT, expand = False)
            tasks_AZ_filter.current(0)
            tasks_AZ_filter.bind("<<ComboboxSelected>>", tasksview_event)
            
            tasks_list = ttk.Treeview(tasks_frame_1, show = "headings")
            tasks_list.tag_configure('green', background = 'lightgreen')
            tasks_list.tag_configure('red', background = 'pink')
            tasks_list.tag_configure('grey', background = 'lightgrey')
            tasks_list.bind("<Double-Button-1>", finish_tasks_event)
            tasks_list.bind("<Button-3>", tasks_popup)
            tasks_list.bind("<FocusIn>", tasks_popupFocusOut)
            tasks_list.bind("<Return>", finish_tasks_event)
            tasks_list.bind("<Delete>", delete_tasks_event)

            tasks_list['columns']=["Срок завершения", "Описание задачи", "Отметка о выполнении"]
            for header in ["Срок завершения", "Описание задачи", "Отметка о выполнении"]:
                tasks_list.heading(header, text = header, anchor = 'w')
                tasks_list.column('{}'.format(header))

            tasks_scroll_y = ttk.Scrollbar(tasks_frame_1, command = tasks_list.yview)#Создаем вертикальную полосу прокрутки для дерева сделок во фрейме frame3_in_file_cabinet
            tasks_list.configure(yscrollcommand = tasks_scroll_y.set)#Конфигурируем дерево контактов на зависимость от вертикальной полосы прокрутки
            tasks_scroll_y.pack(side = LEFT, fill = Y)#Упаковываем вертикальную полосу прокрутки в левой стороне фрейма, растягиваем вертикально по фрейму
            tasks_list.pack(side = LEFT, fill = BOTH, expand = True)#Упаковываем дерево контакта рядом с полосой прокрутки, растягиваем на всю оставшуюся область фрейма
            tasks_scroll_x = ttk.Scrollbar (tasks_frame_2, orient="horizontal", command = tasks_list.xview)#Создаем горизонтальную полосу прокрутки, устанавливаем горизонтальную ориентацию, привязываем к дереву контактов
            tasks_list.configure(xscrollcommand = tasks_scroll_x.set)#Конфигурируем дерево контактов на зависимость от горизонтальной полосы прокрутки
            tasks_scroll_x.pack(fill = X)#Упаковываем горизонтальную полосу, растягиваем по оси X

            tasks_exit_btn = Button(tasks_frame_3, text = "Выход",
                                    command = tasks_exit)
            tasks_exit_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_exit_btn.bind("<Return>", tasks_exit_event)
            tasks_exit_btn.focus()
            tasks_edit_btn = Button(tasks_frame_3, text = "Редактировать",
                                    command = finish_tasks)
            tasks_edit_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_edit_btn.bind("<Return>", finish_tasks_event)
            tasks_delete_in_btn = Button(tasks_frame_3, text = "Удалить",
                                    command = delete_tasks)
            tasks_delete_in_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_delete_in_btn.bind("<Return>", delete_tasks_event)
            tasks_newtasks_btn = Button(tasks_frame_3, text = "Новая",
                                    command = new_tasks)
            tasks_newtasks_btn.pack(side = RIGHT, fill = X, expand = True)
            tasks_newtasks_btn.bind("<Return>", new_tasks_event)
            tasksview()
        else:
            msg.showerror("Внимание", "Выберите сделку для отображения списка задач")
    except TclError:
        msg.showerror("Внимание", "Множественное редактирование не поддерживается")

#Создание функции вызова "О программе"
def about_programm():
    about_programm_window = Toplevel()
    about_programm_window.title("О программе")
    about_programm_window.resizable(True, True)
    about_programm_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
    about_programm_window.minsize(500, 300)

    text_board = Text(about_programm_window)
    text_board.pack(side = LEFT, fill = BOTH, expand = True)

    scroll_y = ttk.Scrollbar(about_programm_window, command = text_board.yview)
    text_board.configure(yscrollcommand = scroll_y.set)
    scroll_y.pack(side = LEFT, fill = Y)
    
    with open("info/info.txt", "r", encoding = "utf-8") as file:
        text_file = file.readlines()
    for line in text_file:
        text_board.insert(END, line)
    text_board.configure(state = "disabled")

def custom():
    custom_window = Toplevel()
    custom_window.grab_set()
    custom_window.title("Настройки")
    custom_window.resizable(False, False)
    custom_window.geometry("+{}+{}".format(str(20+int(size()[0])), str(20+int(size()[1]))))
    custom_window.attributes("-topmost", True)#Установка положения окна "поверх всех окон"

    def custom_quit():
        custom_window.destroy()

    #Функции городов
    def town_add_func():
        town_name = town_entry.get()
        custom_window.attributes("-topmost", False)
        town_delete.configure(state = "disable")
        town_add.configure(state = "disable")
        save_town_format.configure(state = "disable")
        custom_exit.configure(state = "disable")
        global town_lst
        if town_name != "":
            if town_name not in town_lst:
                time_zone_name = time_zone.get()
                tz_hour = int(tz.get())
                if time_zone_name  == "UTC":
                    tz_hour -= 3
                elif time_zone_name == "YEKT":
                    tz_hour += 2
                if tz_hour >= 0:
                    tz_hour = "+"+str(tz_hour)
                if msg.askyesno("Внимание", "Добавить город {} в базу?".format(town_name)):
                    with open("db/town.txt", "r", encoding = "utf-8") as file:
                        A = file.readlines()
                    A.append("{}".format(town_name)+", "+"{}".format(tz_hour)+"\n")
                    with open("db/town.txt", "w", encoding = "utf-8") as file:
                        file.writelines(sorted(A))
                    read_tz_format()
                    read_town_lst()
            else:
                msg.showinfo("Внимание", "Город с таким названием уже есть в базе")
        else:
            msg.showinfo("Внимание", "Введите название города")
        custom_window.attributes("-topmost", True)
        town_delete.configure(state = "normal")
        town_add.configure(state = "normal")
        save_town_format.configure(state = "normal")
        custom_exit.configure(state = "normal")
    def town_add_func_event(event):
        town_name = town_entry.get()
        custom_window.attributes("-topmost", False)
        town_delete.configure(state = "disable")
        town_add.configure(state = "disable")
        save_town_format.configure(state = "disable")
        custom_exit.configure(state = "disable")
        global town_lst
        if town_name != "":
            if town_name not in town_lst:
                time_zone_name = time_zone.get()
                tz_hour = int(tz.get())
                if time_zone_name  == "UTC":
                    tz_hour -= 3
                elif time_zone_name == "YEKT":
                    tz_hour += 2
                if tz_hour >= 0:
                    tz_hour = "+"+str(tz_hour)
                if msg.askyesno("Внимание", "Добавить город {} в базу?".format(town_name)):
                    with open("db/town.txt", "r", encoding = "utf-8") as file:
                        A = file.readlines()
                    A.append("{}".format(town_name)+", "+"{}".format(tz_hour)+"\n")
                    with open("db/town.txt", "w", encoding = "utf-8") as file:
                        file.writelines(sorted(A))
                    read_tz_format()
                    read_town_lst()
            else:
                msg.showinfo("Внимание", "Город с таким названием уже есть в базе")
        else:
            msg.showinfo("Внимание", "Введите название города")
        custom_window.attributes("-topmost", True)
        town_delete.configure(state = "normal")
        town_add.configure(state = "normal")
        save_town_format.configure(state = "normal")
        custom_exit.configure(state = "normal")

    def change_town_format():
        time_zone_name = time_zone_format.get()
        with open("db/town_format.txt", "w", encoding = "utf-8") as file:
                file.write(time_zone_name)
        read_tz_format()
        time_zone.current(["UTC", "MSK", "YEKT"].index(town_lst_format))

    def post_town_lst():
        lst_town['values'] = town_lst

    def delete_town():
        town_name = lst_town.get()
        custom_window.attributes("-topmost", False)
        town_delete.configure(state = "disable")
        town_add.configure(state = "disable")
        save_town_format.configure(state = "disable")
        custom_exit.configure(state = "disable")
        if town_name != "":
            with open("db/town.txt", "r", encoding = "utf-8") as file:
                A = file.readlines()
            A.remove(A[[x.split(", ")[0] for x in A].index(town_name)])
            if town_name in [x.split(", ")[0] for x in A]:
                A.remove(A[[x.split(", ")[0] for x in A].index(town_name)])
            if msg.askyesno("Внимание", "Удалить {} из списка городов?".format(town_name)):
                with open("db/town.txt", "w", encoding = "utf-8") as file:
                    file.writelines(A)
                read_town_lst()
                lst_town.set("")
        else:
            msg.showinfo("Внимание", "Выберите город для удаления")
        custom_window.attributes("-topmost", True)
        town_delete.configure(state = "normal")
        town_add.configure(state = "normal")
        save_town_format.configure(state = "normal")
        custom_exit.configure(state = "normal")

    #Создание функций вызова контекстного меню
    def custom_popup(event):
        global x, y
        x = event.x
        y = event.y
        custom_menu.post(event.x_root, event.y_root)
        #custom_menu.grab_set()

    def custom_popupFocusOut(event):
        custom_menu.unpost()
            
    def custom_copy_selection():
        try:
            custom_window.clipboard_clear()
            custom_window.clipboard_append(custom_window.focus_get().selection_get())
        except :
            return
                
    def custom_paste_cl():
        try:
            custom_window.focus_get().insert(INSERT, custom_window.clipboard_get())
        except :
            return
        
    custom_menu = Menu(tearoff = False)
    custom_menu.add_command(label = "Копировать", command = custom_copy_selection)
    custom_menu.add_command(label = "Вставить", command = custom_paste_cl)


    custom_book = ttk.Notebook(custom_window)
    custom_book.pack(fill=BOTH, expand = True, padx = 1, pady = 1)

    frame_town = ttk.Frame(custom_book)
    #Добавление фреймов на вкладки меню
    custom_book.add(frame_town, text = "Города")
    #Упаковка главного меню
    custom_book.pack(fill=BOTH, expand = True, padx = 1, pady = 1)
    #Создание и упаковка дополнительного фрейма для кнопок внизу окна настроек
    frame_all = LabelFrame(custom_window)
    frame_all.pack(fill=BOTH, expand = False, padx = 1, pady = 1)

    #Настройка городов
    frame_town_1 = LabelFrame(frame_town)
    frame_town_1.pack(fill = X, expand = True)
    lst_town = ttk.Combobox(frame_town_1, values = town_lst,
                            postcommand = post_town_lst,
                            state = 'readonly')
    lst_town.pack(side = LEFT, fill = BOTH, expand = True)
    town_delete = Button(frame_town_1, text = "Удалить", width = 20,
                         command = delete_town)
    town_delete.pack(side = LEFT, fill = BOTH, expand = False)
    
    
    frame_town_2 = LabelFrame(frame_town)
    frame_town_2.pack(fill = X, expand = True)
    town_lbl = Label(frame_town_2, text = "Добавить город:", width = 20)
    town_lbl.pack(side = LEFT, fill = BOTH, expand = False)
    town_entry = Entry(frame_town_2, width = 30)
    town_entry.pack(side = LEFT, fill = BOTH, expand = True)
    town_entry.bind("<Return>", town_add_func_event)
    time_zone = ttk.Combobox(frame_town_2,
                             values = ["UTC", "MSK", "YEKT"],
                             state = 'readonly', width = 5)
    time_zone.pack(side = LEFT, fill = BOTH, expand = False)
    time_zone.current(["UTC", "MSK", "YEKT"].index(town_lst_format))
    tz = ttk.Spinbox(frame_town_2, values = (-24, -23, -22, -21, -20,
                                                    -19, -18, -17, -16, -15,
                                                    -14, -13, -12, -11, -10,
                                                    -9, -8, -7, -6, -5, -4,
                                                    -3, -2, -1, 0, +1, +2,
                                                    +3, +4, +5, +6, +7, +8,
                                                    +9, +10, +11, +12, +13,
                                                    +14, +15, +16, +17, +18,
                                                    +19, +20, +21, +22, +23, +24),
                            width = 5, state = 'readonly')
    tz.pack(side = LEFT, fill = BOTH, expand = False)
    tz.set("0")
    town_add = Button(frame_town_2, text = "Добавить", width = 20, command = town_add_func)
    town_add.pack(side = LEFT, fill = BOTH, expand = False)

    frame_town_3 = LabelFrame(frame_town)
    frame_town_3.pack(fill = X, expand = True)
    view_lbl = Label(frame_town_3, text = "Формат отображения:",
                     width = 20)
    view_lbl.pack(side = LEFT, fill = BOTH, expand = False)
    time_zone_format = ttk.Combobox(frame_town_3,
                             values = ["UTC", "MSK", "YEKT"],
                             state = 'readonly', width = 5)
    time_zone_format.pack(side = LEFT, fill = BOTH, expand = False)
    time_zone_format.current(["UTC", "MSK", "YEKT"].index(town_lst_format))
    save_town_format = Button(frame_town_3, text = "Сохранить",
                              width = 20, command = change_town_format)
    save_town_format.pack(side = RIGHT, fill = BOTH, expand = False)

    #Настройка кнопок
    custom_exit = Button(frame_all, text = "Закрыть", width = 20, command = custom_quit)
    custom_exit.pack(side = RIGHT, expand = False, padx = 1, pady = 1)

    custom_window.bind("<Button-3>", custom_popup)
    custom_window.bind("<FocusIn>", custom_popupFocusOut)
    
    custom_window.bind("<Control-C>", custom_copy_selection)
    custom_window.bind("<Control-V>", custom_paste_cl)
    def custom_key_callback(event):
        if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
            if chr(event.keycode) == "C":
                custom_copy_selection()
            elif chr(event.keycode) == "V":
                custom_paste_cl()
    custom_window.bind("<Key>", custom_key_callback)

#Создание главного окна программы
root = Tk()

#Название главного окна программы
root.title('Cusima')

#Иконка главного окна программы
root.iconbitmap("logo.ico")

#Вывод главного окна размером с 3/4 экрана в левом верхнем углу (100+100)
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
w = int(w//1.3)
h = int(h//1.3)
root.geometry("{}x{}+100+100".format(w, h))
root.minsize(w, h)#Установка минимально возможного размера окна программы

tasks_menu = Menu(tearoff = False)
#Создание функции вызова контекстного меню для строки поиска Картотеки
def popup(event):
    global x, y
    x = event.x
    y = event.y
    con_menu.post(event.x_root, event.y_root)
    root.focus()

def popupFocusOut(event):
    con_menu.unpost()
def copy_selection():
    try:
        root.clipboard_clear()
        root.clipboard_append(find_str.selection_get())
    except :
        return
def paste_cl():
    try:
        find_str.insert(INSERT, root.clipboard_get())
        tree_shower()
    except :
        return
    
con_menu = Menu(tearoff = False)
con_menu.add_command(label = "Копировать", command = copy_selection)
con_menu.add_command(label = "Вставить", command = paste_cl)

#Создание функции вызова контекстного меню для строки поиска Картотеки
def find_trans_popup(event):
    global x, y
    x = event.x
    y = event.y
    find_trans_con_menu.post(event.x_root, event.y_root)
    root.focus()

def find_trans_popupFocusOut(event):
    find_trans_con_menu.unpost()
def find_trans_copy_selection():
    try:
        root.clipboard_clear()
        root.clipboard_append(trans_find_str.selection_get())
    except :
        return
def find_trans_paste_cl():
    try:
        trans_find_str.insert(INSERT, root.clipboard_get())
        trans_tree_shower()
    except :
        return
    
find_trans_con_menu = Menu(tearoff = False)
find_trans_con_menu.add_command(label = "Копировать", command = find_trans_copy_selection)
find_trans_con_menu.add_command(label = "Вставить", command = find_trans_paste_cl)

#Создание функции вызова контекстного меню для строки поиска Картотеки
def trans_name_popup(event):
    global x, y
    x = event.x
    y = event.y
    trans_name_con_menu.post(event.x_root, event.y_root)
    root.focus()

def trans_name_popupFocusOut(event):
    trans_name_con_menu.unpost()
def trans_name_copy_selection():
    try:
        root.clipboard_clear()
        root.clipboard_append(trans_name.selection_get())
    except :
        return
def trans_name_paste_cl():
    try:
        trans_name.insert(INSERT, root.clipboard_get())
    except :
        return
    
trans_name_con_menu = Menu(tearoff = False)
trans_name_con_menu.add_command(label = "Копировать", command = trans_name_copy_selection)
trans_name_con_menu.add_command(label = "Вставить", command = trans_name_paste_cl)

#Создание функции вызова контекстного меню для строки поиска Картотеки
def company_name_popup(event):
    global x, y
    x = event.x
    y = event.y
    company_name_con_menu.post(event.x_root, event.y_root)
    root.focus()

def company_name_popupFocusOut(event):
    company_name_con_menu.unpost()
def company_name_copy_selection():
    try:
        root.clipboard_clear()
        root.clipboard_append(company_name.selection_get())
    except :
        return
def company_name_paste_cl():
    try:
        company_name.insert(INSERT, root.clipboard_get())
    except :
        return
    
company_name_con_menu = Menu(tearoff = False)
company_name_con_menu.add_command(label = "Копировать", command = company_name_copy_selection)
company_name_con_menu.add_command(label = "Вставить", command = company_name_paste_cl)

#Создание функции вызова контекстного меню для строки поиска Картотеки
def commitments_name_popup(event):
    global x, y
    x = event.x
    y = event.y
    commitments_name_con_menu.post(event.x_root, event.y_root)
    root.focus()

def commitments_name_popupFocusOut(event):
    commitments_name_con_menu.unpost()
def commitments_name_copy_selection():
    try:
        root.clipboard_clear()
        root.clipboard_append(commitments_name.selection_get())
    except :
        return
def commitments_name_paste_cl():
    try:
        commitments_name.insert(INSERT, root.clipboard_get())
    except :
        return
    
commitments_name_con_menu = Menu(tearoff = False)
commitments_name_con_menu.add_command(label = "Копировать", command = commitments_name_copy_selection)
commitments_name_con_menu.add_command(label = "Вставить", command = commitments_name_paste_cl)

#Создание функции вызова контекстного меню для поля контактов
tree_menu = Menu(tearoff = False)
def tree_popup(event):
    global x, y, tree_menu
    x = event.x
    y = event.y
    valueses_tree_menu = [file_cabinet.item(x, option="values") for x in file_cabinet.selection()]
    if len(valueses_tree_menu) == 0:
        tree_menu = Menu(tearoff = False)
        tree_menu.add_command(label = "Просмотреть/Изменить", command = ch_db_not_event, state = 'disabled')
        tree_menu.add_command(label = "Создать копию", command = copy_db_not_event, state = 'disabled')
        tree_menu.add_command(label = "Удалить", command = delete_contact, state = 'disabled')
    elif len(valueses_tree_menu) == 1:
        tree_menu = Menu(tearoff = False)
        tree_menu.add_command(label = "Просмотреть/Изменить", command = ch_db_not_event)
        tree_menu.add_command(label = "Создать копию", command = copy_db_not_event)
        tree_menu.add_command(label = "Удалить", command = delete_contact)
    else:
        tree_menu = Menu(tearoff = False)
        tree_menu.add_command(label = "Просмотреть/Изменить", command = ch_db_not_event, state = 'disabled')
        tree_menu.add_command(label = "Создать копию", command = copy_db_not_event, state = 'disabled')
        tree_menu.add_command(label = "Удалить", command = delete_contact)        
    tree_menu.post(event.x_root, event.y_root)
    root.focus()

def tree_popupFocusOut(event):
    global tree_menu
    tree_menu.unpost()
        
def finish_all_tasks():
    valueses = [transactions.item(x, option="values") for x in transactions.selection()]
    for values in valueses:
        for i in trans_data:
            if i[0] == values[0] and i[1] == values[1] and i[2] == values[2] and i[3] == values[3]:
                save_tasks_str = i[4]
        save_tasks = [x[1:-1].split("], [") for x in [x for x in save_tasks_str[1:-1].split("), (")]]
        if save_tasks != [['']]:
            for item in save_tasks:
                if item[2].replace(" ", "") == '':
                    item[2] = '+'
        else:
            save_tasks = ""
        save_tasks_replace_str = ""
        for i in save_tasks:
            i_str = ""
            for element in i:
                i_str += "["+str(element)+"], "
            save_tasks_replace_str += "("+str(i_str[:-2]).replace("\'", "")+"), "
        try:
            sqlite_connections = sqlite3.connect(r'db\db.db')
            cursor = sqlite_connections.cursor()
            print_log("DB OPEN")
            cursor.execute("""Update trans set Задачи = "{}" WHERE Сделка = '{}'
                            AND Компания = '{}'
                            AND Дата = '{}'
                            AND Обязательства = '{}'""".format(save_tasks_replace_str[:-2],
                                                               values[0],
                                                               values[1],
                                                               values[2],
                                                               values[3]))
            sqlite_connections.commit()
            cursor.close()
        except sqlite3.Error as error:
            print_log("DB ERROR")
            print_log(error)
            msg.showerror("Внимание", "Произошла ошибка при чтении базы данных. Код ошибки: {}. Сохраните данные, закройте посторонние программы и перезапустите MemoryCall".format(error))
        finally:
            if (sqlite_connections):
                sqlite_connections.close()
                print_log("DB CLOSE")
    show()
    trans_tree_shower()
    
#Создание функции вызова контекстного меню для поля сделок
trans_menu = Menu(tearoff = False)
def trans_popup(event):
    global x, y, trans_menu
    x = event.x
    y = event.y
    valueses = [transactions.item(x, option="values") for x in transactions.selection()]
    if len(valueses) == 0:
        trans_menu = Menu(tearoff = False)
        trans_menu.add_command(label = "Открыть окно задач",
                               command = tasks_show,
                               state = 'disabled')
        trans_menu.add_command(label = "Завершить все задачи",
                               command = finish_all_tasks,
                               state = 'disabled')
        trans_menu.add_separator()
        trans_menu.add_command(label = "Удалить сделку",
                               command = trans_delete_contact,
                               state = 'disabled')
        trans_menu.add_command(label = "Документы",
                               command = file_show,
                               state = 'disabled')
    elif len(valueses) == 1:
        trans_menu = Menu(tearoff = False)
        trans_menu.add_command(label = "Открыть окно задач",
                               command = tasks_show)
        trans_menu.add_command(label = "Завершить все задачи",
                               command = finish_all_tasks)
        trans_menu.add_separator()
        trans_menu.add_command(label = "Удалить сделку",
                               command = trans_delete_contact)
        trans_menu.add_command(label = "Документы",
                               command = file_show)
    else:
        trans_menu = Menu(tearoff = False)
        trans_menu.add_command(label = "Открыть окно задач",
                               command = tasks_show,
                               state = 'disabled')
        trans_menu.add_command(label = "Завершить все задачи",
                               command = finish_all_tasks)
        trans_menu.add_separator()
        trans_menu.add_command(label = "Удалить сделки",
                               command = trans_delete_contact)
        trans_menu.add_command(label = "Документы",
                               command = file_show,
                               state = 'disabled')
    trans_menu.post(event.x_root, event.y_root)
    root.focus()

def trans_popupFocusOut(event):
    global trans_menu
    trans_menu.unpost()

trans_menu = Menu(tearoff = False)
trans_menu.add_command(label = "Открыть окно задач",
                               command = tasks_show)
trans_menu.add_command(label = "Завершить все задачи",
                              command = finish_all_tasks)
trans_menu.add_separator()
trans_menu.add_command(label = "Удалить сделку",
                              command = trans_delete_contact)
trans_menu.add_command(label = "Документы",
                              command = file_show)

#Создание общего меню в главном окне, добавление в общее меню двух разделов (filemenu, helpmenu), а также кнопок и разделителей
mainmenu = Menu(root)
root.config (menu = mainmenu)
filemenu = Menu (mainmenu, tearoff = 0)
filemenu.add_command (label = "Создать новый контакт", command = add_db)
filemenu.add_command (label = "Просмотреть/изменить контакт", command = ch_db_not_event)
filemenu.add_command (label = "Создать копию карточки контакта", command = copy_db_not_event)
filemenu.add_command (label = "Удалить контакты", command = delete_contact)
filemenu.add_separator()
filemenu.add_command (label = "Открыть окно задач", command = tasks_show)
filemenu.add_command (label = "Завершить все задачи", command = finish_all_tasks)
filemenu.add_command (label = "Удалить выбранные сделки", command = trans_delete_contact)
filemenu.add_command (label = "Сохранить изменения в сделке", command = trans_ch_db_not_event)
filemenu.add_command (label = "Добавить новую сделку", command = add_trans_click)
filemenu.add_command (label = "Открыть документы для сделки", command = file_show)
filemenu.add_separator()
filemenu.add_command(label = "Настройки", command = custom)
filemenu.add_separator()
filemenu.add_command (label = "Выход", command = root_quit)
helpmenu = Menu (mainmenu, tearoff = 0)
helpmenu.add_command (label = "О программе", command = about_programm)
mainmenu.add_cascade(label = "   Файл   ", menu = filemenu)
mainmenu.add_cascade(label = "Справка", menu = helpmenu)

#Создание меню вкладок в главном окне
nb = ttk.Notebook(root)
nb.pack(fill=BOTH, expand = True, padx = 1, pady = 1)
#Создание главного фрейма frame_file_cabinet в первой вкладке меню вкладок
frame_file_cabinet = ttk.Frame(nb)
#Создание главного фрейма frame_transactions во второй вкладке меню вкладок
frame_transactions = ttk.Frame(nb)
#Добавление фреймов на вкладки меню
nb.add(frame_file_cabinet, text = " Картотека ")
nb.add(frame_transactions, text = "    Сделки    ")
#Упаковка главного меню
nb.pack(fill=BOTH, expand = True, padx = 1, pady = 1)
#Создание и упаковка дополнительного фрейма для кнопок внизу главного окна программы
frame_btn = LabelFrame(root)
frame_btn.pack(fill=BOTH, expand = False, padx = 1, pady = 1)

#ОТОБРАЖЕНИЕ ВКЛАДКИ КАРТОТЕКА
#Создание и упаковка областей (фреймов) во вкладке "Картотека"
frame1_in_file_cabinet = LabelFrame(frame_file_cabinet)#Фрейм для поиска
frame2_in_file_cabinet = LabelFrame(frame_file_cabinet)#Фрейм для управляющих кнопок
frame3_in_file_cabinet = LabelFrame(frame_file_cabinet)#Фрейм для дерева контактов и левой вертикальной полосы прокрутки
frame4_in_file_cabinet = LabelFrame(frame_file_cabinet)#Фрейм для нижней горизонтальной полосы прокрутки
frame1_in_file_cabinet.pack(fill=BOTH, expand = False, padx = 1, pady = 1)
frame2_in_file_cabinet.pack(fill=BOTH, expand = False, padx = 1, pady = 1)
frame3_in_file_cabinet.pack(fill=BOTH, expand = True)
frame4_in_file_cabinet.pack(fill=BOTH, expand = False)

#Добавление и упаковка во фрейм frame1_in_file_cabinet строки поиска и кнопки поиска
find_str = Entry(frame1_in_file_cabinet)
clear_btn = Button(frame1_in_file_cabinet, text = 'Сброс', width = 20)
clear_btn.bind("<Button-1>", clear_find_str)
clear_btn.bind("<ButtonRelease-1>", tree_show)
find_str.pack(side=LEFT, fill=BOTH, expand = True)
clear_btn.pack(side=LEFT, expand = False)
find_str.bind('<KeyRelease>', tree_show)
find_str.bind('<FocusIn>', tree_show)
find_str.bind("<Button-3>", popup)
find_str.bind("<FocusIn>", popupFocusOut)  
find_str.bind("<Control-C>", copy_selection)
find_str.bind("<Control-V>", paste_cl)
def find_str_key_callback(event):
    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
        if chr(event.keycode) == "C":
            copy_selection()
        elif chr(event.keycode) == "V":
            paste_cl()
find_str.bind("<Key>", find_str_key_callback)

#Добавление и упаковка во фрейм frame2_in_file_cabinet выпадающего фильтра-списка и кнопок редактирования Картотеки
combo_filter = ttk.Combobox(frame2_in_file_cabinet,
                            values = contact_parameters,
                            postcommand = callback_combo_filter, state = 'readonly')#Создание выпадающего фильтр-списка, привязка его значений к верхней строке базы данных
combo_filter.pack(side = LEFT, expand = False)#Упаковка фильтра-списка
combo_filter.bind("<<ComboboxSelected>>", tree_show)#Привязка функции к обработчику события (выбор значения комбо-бокс)
combo_filter.current(0)
combo_combo_filter = ttk.Combobox(frame2_in_file_cabinet,
                                  values = [], postcommand = post_double_file_cabinet,
                                  state = 'readonly')#Создание выпадающего фильтр-фильтр-списка, привязка его значений к верхней строке базы данных
combo_combo_filter.pack(side = LEFT, expand = False)#Упаковка фильтра-фильтра-списка
combo_combo_filter.bind("<<ComboboxSelected>>", tree_show)

AZ_filter = ttk.Combobox(frame2_in_file_cabinet,
                         values = ["А-Я", "Я-А"],
                         state = 'readonly', width = 4)
AZ_filter.pack(side = LEFT, expand = False)
AZ_filter.current(0)
AZ_filter.bind("<<ComboboxSelected>>", tree_show)

add_btn = Button(frame2_in_file_cabinet, text = 'Добавить', width = 20,
                 command = add_db)
change_btn = Button(frame2_in_file_cabinet, text = 'Изменить', width = 20)
change_btn.bind("<ButtonRelease-1>", ch_db)
delete_btn = Button(frame2_in_file_cabinet, text = 'Удалить', width = 20,
                    command = delete_contact)
add_btn.pack(side = RIGHT, expand = False)
change_btn.pack(side = RIGHT, expand = False)
delete_btn.pack(side = RIGHT, expand = False)

#Добавление во фреймы frame3_in_file_cabinet и frame4_in_file_cabinet дерева контактов и полос прокрутки
file_cabinet = ttk.Treeview(frame3_in_file_cabinet, show = "headings")
file_cabinet.tag_configure('0', background = 'lightcyan')
file_cabinet.tag_configure('1', background = 'lightgrey')

file_cabinet.bind("<Double-Button-1>", ch_db)
file_cabinet.bind("<Button-3>", tree_popup)
file_cabinet.bind("<FocusIn>", tree_popupFocusOut)
file_cabinet.bind("<Return>", ch_db)
file_cabinet.bind("<Delete>", delete_contact_event)

scroll_y = ttk.Scrollbar(frame3_in_file_cabinet, command = file_cabinet.yview)#Создаем вертикальную полосу прокрутки для дерева контактов во фрейме frame3_in_file_cabinet
file_cabinet.configure(yscrollcommand = scroll_y.set)#Конфигурируем дерево контактов на зависимость от вертикальной полосы прокрутки
scroll_y.pack(side = LEFT, fill = Y)#Упаковываем вертикальную полосу прокрутки в левой стороне фрейма, растягиваем вертикально по фрейму
file_cabinet.pack(side = LEFT, fill = BOTH, expand = True)#Упаковываем дерево контакта рядом с полосой прокрутки, растягиваем на всю оставшуюся область фреймма
scroll_x = ttk.Scrollbar (frame4_in_file_cabinet, orient="horizontal", command = file_cabinet.xview)#Создаем горизонтальную полосу прокрутки, устанавливаем горизонтальную ориентацию, привязываем к дереву контактов
file_cabinet.configure(xscrollcommand = scroll_x.set)#Конфигурируем дерево контактов на зависимость от горизонтальной полосы прокрутки
scroll_x.pack(fill = X)#Упаковываем горизонтальную полосу, растягиваем по оси X

#ОТОБРАЖЕНИЕ ВКЛАДКИ СДЕЛКИ
#Создание и упаковка областей (фреймов) во вкладке "Сделки"
frame1_in_transactions = LabelFrame(frame_transactions)#Фрейм для поиска
frame1_in_transactions.pack(fill=BOTH, expand = False, padx = 1, pady = 1)
trans_find_str = Entry(frame1_in_transactions)
trans_find_str.pack(side=LEFT, fill=BOTH, expand = True)
trans_find_btn = Button(frame1_in_transactions, text = 'Сброс', width = 20)
trans_find_btn.bind("<Button-1>", trans_clear_find_str)
trans_find_btn.bind("<ButtonRelease-1>", trans_tree_show)
trans_find_str.bind("<Button-3>", find_trans_popup)
trans_find_str.bind("<FocusIn>", find_trans_popupFocusOut)  
trans_find_str.bind("<Control-C>", find_trans_copy_selection)
trans_find_str.bind("<Control-V>", find_trans_paste_cl)
def find_trans_key_callback(event):
    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
        if chr(event.keycode) == "C":
            find_trans_copy_selection()
        elif chr(event.keycode) == "V":
            find_trans_paste_cl()
trans_find_str.bind("<Key>", find_trans_key_callback)

trans_find_btn.pack(side=LEFT, expand = False)
trans_find_str.bind('<KeyRelease>', trans_tree_show)
trans_find_str.bind('<FocusIn>', trans_tree_show)

frame2_in_transactions = LabelFrame(frame_transactions)#Фрейм для управляющих кнопок
frame2_in_transactions.pack(fill=BOTH, expand = False, padx = 1, pady = 1)
trans_combo_filter = ttk.Combobox(frame2_in_transactions,
                                  values = ["Название сделки",
                                            "Компания",
                                            "Дата создания",
                                            "Обязательства по сделке"],
                                  postcommand = trans_callback_combo_filter,
                                  state = 'readonly')
trans_combo_filter.pack(side = LEFT, expand = False)
trans_combo_filter.bind("<<ComboboxSelected>>", trans_tree_show)#Привязка функции к обработчику события (выбор значения комбо-бокс)
trans_combo_filter.current(0)

trans_combo_combo_filter = ttk.Combobox(frame2_in_transactions,
                                        values = [],
                                        postcommand = trans_post_double_file_cabinet,
                                        state = 'readonly')
trans_combo_combo_filter.pack(side = LEFT, expand = False)
trans_combo_combo_filter.bind("<<ComboboxSelected>>", trans_tree_show)

lbl_green = Label(frame2_in_transactions, width = 2, bg = 'lightgreen')
lbl_red = Label(frame2_in_transactions, width = 2, bg = 'pink')
lbl_grey = Label(frame2_in_transactions, width = 2, bg = 'lightgrey')

green_radio_btn = ttk.Checkbutton(frame2_in_transactions)
red_radio_btn = ttk.Checkbutton(frame2_in_transactions)
grey_radio_btn = ttk.Checkbutton(frame2_in_transactions)

lbl_green.pack(side = LEFT, expand = False)
green_radio_btn.pack(side = LEFT, expand = False)
lbl_red.pack(side = LEFT, expand = False)
red_radio_btn.pack(side = LEFT, expand = False)
lbl_grey.pack(side = LEFT, expand = False)
grey_radio_btn.pack(side = LEFT, expand = False)
green_radio_btn.bind("<ButtonRelease-1>", trans_tree_show)
red_radio_btn.bind("<ButtonRelease-1>", trans_tree_show)
grey_radio_btn.bind("<ButtonRelease-1>", trans_tree_show)
        
trans_AZ_filter = ttk.Combobox(frame2_in_transactions, values = ["А-Я", "Я-А"], state = 'readonly', width = 4)
trans_AZ_filter.pack(side = LEFT, expand = False)
trans_AZ_filter.current(0)
trans_AZ_filter.bind("<<ComboboxSelected>>", trans_tree_show)

frame3_in_transactions = LabelFrame(frame_transactions)#Фрейм для дерева сделок и левой вертикальной полосы прокрутки
frame4_in_transactions = LabelFrame(frame_transactions)#Фрейм для нижней горизонтальной полосы прокрутки
frame3_in_transactions.pack(fill=BOTH, expand = True, padx = 1, pady = 1)
frame4_in_transactions.pack(fill=X, expand = False, padx = 1, pady = 1)

#Добавление во фреймы frame3_in_transactions и frame4_in_transactions дерева сделок и полос прокрутки
transactions = ttk.Treeview(frame3_in_transactions, show = "headings", height = 5)
transactions.tag_configure('green', background = 'lightgreen')
transactions.tag_configure('red', background = 'pink')
transactions.tag_configure('grey', background = 'lightgrey')
transactions.bind("<<TreeviewSelect>>", trans_view)
transactions.bind("<Double-Button-1>", tasks_show_event)
transactions.bind("<Button-3>", trans_popup)
transactions.bind("<FocusIn>", trans_popupFocusOut)
transactions.bind("<Return>", tasks_show_event)
transactions.bind("<Delete>", trans_delete_contact_event)

trans_scroll_y = ttk.Scrollbar(frame3_in_transactions, command = transactions.yview)#Создаем вертикальную полосу прокрутки для дерева сделок во фрейме frame3_in_file_cabinet
transactions.configure(yscrollcommand = trans_scroll_y.set)#Конфигурируем дерево контактов на зависимость от вертикальной полосы прокрутки
trans_scroll_y.pack(side = LEFT, fill = Y)#Упаковываем вертикальную полосу прокрутки в левой стороне фрейма, растягиваем вертикально по фрейму
transactions.pack(side = LEFT, fill = BOTH, expand = True)#Упаковываем дерево контакта рядом с полосой прокрутки, растягиваем на всю оставшуюся область фрейма
trans_scroll_x = ttk.Scrollbar (frame4_in_transactions, orient="horizontal", command = transactions.xview)#Создаем горизонтальную полосу прокрутки, устанавливаем горизонтальную ориентацию, привязываем к дереву контактов
transactions.configure(xscrollcommand = trans_scroll_x.set)#Конфигурируем дерево контактов на зависимость от горизонтальной полосы прокрутки
trans_scroll_x.pack(fill = X)#Упаковываем горизонтальную полосу, растягиваем по оси X

frame5_in_transactions = Frame(frame_transactions)#Фрейм для первого блока сделок (название, компания, описание, документы)
frame5_in_transactions.pack(fill=BOTH, expand = False, padx = 1, pady = 1)

#Добавление дополнительных фреймов в 1, 2, 3 блоки сделок
frame51_in_transactions = Frame(frame5_in_transactions)
frame51_in_transactions.pack(side = LEFT, fill=BOTH, expand = True)
frame52_in_transactions = Frame(frame5_in_transactions)
frame52_in_transactions.pack(side = LEFT, fill=BOTH, expand = False)
frame511_in_transactions = Frame(frame51_in_transactions)
frame511_in_transactions.pack(fill = BOTH, expand = True)
frame512_in_transactions = LabelFrame(frame51_in_transactions, text = 'Обязательства по сделке')
frame512_in_transactions.pack(fill = BOTH, expand = False)
frame5111_in_transactions = LabelFrame(frame511_in_transactions, text = 'Название сделки')
frame5112_in_transactions = LabelFrame(frame511_in_transactions, text = 'Компания заказчика')
frame5113_in_transactions = LabelFrame(frame511_in_transactions, text = 'Дата создания')
frame5111_in_transactions.pack(side = LEFT, fill = X, expand = True)
frame5112_in_transactions.pack(side = LEFT, fill = X, expand = True)
frame5113_in_transactions.pack(side = LEFT, fill = X, expand = True)

#Добавление объектов в дополнительные фреймы 1, 2, 3 блоков сделок
trans_name = ttk.Combobox(frame5111_in_transactions, postcommand = post_trans_name)
trans_name.pack(fill = BOTH, expand = True, padx = 1, pady = 1)
trans_name.bind("<Button-3>", trans_name_popup)
trans_name.bind("<FocusIn>", trans_name_popupFocusOut)  
trans_name.bind("<Control-C>", trans_name_copy_selection)
trans_name.bind("<Control-V>", trans_name_paste_cl)
def trans_name_key_callback(event):
    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
        if chr(event.keycode) == "C":
            trans_name_copy_selection()
        elif chr(event.keycode) == "V":
            trans_name_paste_cl()
trans_name.bind("<Key>", trans_name_key_callback)

company_name = ttk.Combobox(frame5112_in_transactions, postcommand = post_company_name)
company_name.pack(fill = BOTH, expand = True, padx = 1, pady = 1)
company_name.bind("<Button-3>", company_name_popup)
company_name.bind("<FocusIn>", company_name_popupFocusOut)  
company_name.bind("<Control-C>", company_name_copy_selection)
company_name.bind("<Control-V>", company_name_paste_cl)
def company_name_key_callback(event):
    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
        if chr(event.keycode) == "C":
            company_name_copy_selection()
        elif chr(event.keycode) == "V":
            company_name_paste_cl()
company_name.bind("<Key>", company_name_key_callback)

data_name = ttk.Combobox(frame5113_in_transactions, postcommand = post_date_name, state = 'readonly')
data_name.set("{}".format(time_str()))
data_name.pack(fill = BOTH, expand = True, padx = 1, pady = 1)
commitments_name = Text(frame512_in_transactions, height = 6)
commitments_name.pack(side = LEFT, fill = BOTH, expand = True)
commitments_name.bind("<Button-3>", commitments_name_popup)
commitments_name.bind("<FocusIn>", commitments_name_popupFocusOut)  
commitments_name.bind("<Control-C>", commitments_name_copy_selection)
commitments_name.bind("<Control-V>", commitments_name_paste_cl)
def commitments_name_key_callback(event):
    if (event.state & 4 > 0) and (event.keysym_num == 1089 or event.keysym_num == 1084):
        if chr(event.keycode) == "C":
            commitments_name_copy_selection()
        elif chr(event.keycode) == "V":
            commitments_name_paste_cl()
commitments_name.bind("<Key>", commitments_name_key_callback)

trans_delete_btn = Button(frame52_in_transactions, text = 'Удалить',
                       width = 20, command = trans_delete_contact)
trans_delete_btn.pack(fill = Y, expand = True, padx = 1, pady = 1)
trans_change_btn = Button(frame52_in_transactions, text = 'Сохранить',
                          width = 20, command = trans_ch_db_not_event)
trans_change_btn.pack(fill = Y, expand = True, padx = 1, pady = 1)
trans_add_btn = Button(frame52_in_transactions, text = 'Добавить',
                       width = 20, command = add_trans_click)
trans_add_btn.pack(fill = Y, expand = True, padx = 1, pady = 1)
trans_documents_btn = Button(frame52_in_transactions,
                             text = 'Документы', width = 20,
                             command = file_show)
trans_documents_btn.pack(fill = Y, expand = True, padx = 1, pady = 1)
trans_tasks_btn = Button(frame52_in_transactions, text = 'Задачи',
                         width = 20, command = tasks_show)
trans_tasks_btn.pack(fill = Y, expand = True, padx = 1, pady = 1)

#Создание и упаковка кнопок во фрейме frame_btn
counter_lbl = Label(frame_btn, text = "Контакты: ", width = 20)
trans_lbl = Label(frame_btn, text = "Сделки: ", width = 20)
tasks_lbl = Label(frame_btn, text = "Задачи: ", width = 20)

exit_btn = Button(frame_btn, text = "Выход", width = 20, command = root_quit)#Кнопка выхода из программы
counter_lbl.pack(side = LEFT, expand = False, padx = 1, pady = 1)
trans_lbl.pack(side = LEFT, expand = False, padx = 1, pady = 1)
tasks_lbl.pack(side = LEFT, expand = False, padx = 1, pady = 1)
exit_btn.pack(side = RIGHT, expand = False, padx = 1, pady = 1)

exit_btn.bind("<Return>", root_quit_event)
root.protocol("WM_DELETE_WINDOW", root_quit)

find_str.focus()
root.bind("<FocusIn>", popupFocusOut)
tree_shower()
trans_tree_shower()

root.mainloop()
