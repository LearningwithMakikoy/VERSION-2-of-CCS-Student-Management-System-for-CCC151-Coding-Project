import tkinter as Tk
from tkinter import Frame, ttk
from tkinter import messagebox
import re
import mysql.connector

#Global functions

current_page_student=0
items_per_page=17

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="hello1234",
        database="student_management"
    )

def update_program_combobox():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT program_code FROM program")
    programs = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    programno_ent['values'] = programs  

    if program_var.get() not in programs:
        program_var.set('N/A')

def update_college_combobox():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT college_code FROM college")
    colleges = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    college_ent['values'] = colleges  

    if college_var.get() not in colleges:
        college_var.set('N/A')

def delete_program_or_college(table_name, code_column, code_to_delete):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        if table_name == "program":
            # Check if this program is assigned to any student
            cursor.execute("UPDATE student SET program_code = NULL WHERE program_code = %s", (code_to_delete,))
            
        elif table_name == "college":
            cursor.execute("SELECT * FROM program WHERE college_code = %s", (code_to_delete,))
            if cursor.fetchone():
                messagebox.showerror("Error", f"Cannot delete {code_to_delete} as it is assigned to a program.")
                return

        # Safe to delete
        query = f"DELETE FROM {table_name} WHERE {code_column} = %s"
        cursor.execute(query, (code_to_delete,))
        conn.commit()
        messagebox.showinfo("Success", f"{code_to_delete} has been deleted.")
        
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        
    finally:
        cursor.close()
        conn.close()

#Student Management Functions
def add_student (id_number ,first_name, last_name, year_level, gender, program_code):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = ("INSERT INTO student (id_number, first_name, last_name, year_level, gender, program_code) "
                 "VALUES (%s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (id_number, first_name, last_name, year_level, gender, program_code))
        conn.commit()
        messagebox.showinfo("Success", "Student added successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database error",str(err))
    finally:
        cursor.close()
        conn.close()

def load_student():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def delete_student(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM student WHERE id_number = %s", (student_id,))
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def update_student (id_number ,first_name, last_name, year_level, gender, program_code):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = ("UPDATE student SET first_name=%s, last_name=%s, year_level=%s, gender=%s, program_code=%s WHERE id_number=%s")
        cursor.execute(query, (first_name, last_name, year_level, gender, program_code, id_number))
        conn.commit()
        messagebox.showinfo("Success", "Student data updated successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def search_studentdata(table, search_entry):
    search_value = search_entry.get().strip().lower()

    # Clear current table
    for item in table.get_children():
        table.delete(item)

    conn = connect_db()
    cursor = conn.cursor()

    # Search across all student fields
    query = """SELECT * FROM student 
               WHERE LOWER(id_number) LIKE %s 
               OR LOWER(first_name) LIKE %s 
               OR LOWER(last_name) LIKE %s 
               OR LOWER(gender) LIKE %s 
               OR LOWER(year_level) LIKE %s
               OR LOWER(program_code) LIKE %s"""
    search_term = f"%{search_value}%"
    cursor.execute(query, (search_term, search_term, search_term, search_term, search_term, search_term))

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # Insert matching results into table
    for row in results:
        table.insert("", "end", values=row)

def sort_student_table(tree, sort_by, order):
    conn = connect_db()
    cursor = conn.cursor()
    
    allowed_columns = {
        "ID Number": "id_number",
        "First Name": "first_name",
        "Last Name": "last_name",
        "Gender": "gender",
        "Year Level": "year_level",
        "Program Code": "program_code"
    }

    if sort_by not in allowed_columns:
        print(f"Invalid sort column: {sort_by}")
        conn.close()
        return

    sql_column = allowed_columns[sort_by]
    # Ascending and Descending
    sql_order = "ASC" if order == "Ascending" else "DESC"

    # SQL query to fetch sorted data
    query = f"SELECT id_number, first_name, last_name, year_level, gender, program_code FROM student ORDER BY {sql_column} {sql_order};"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Clear the existing treeview
    for item in tree.get_children():
        tree.delete(item)

    # Insert new sorted rows into the treeview
    for row in rows:
        tree.insert("", "end", values=row)

    # Close the connection
    cursor.close()
    conn.close()


#Program Management Functions
def add_program(program_code, course, college_code):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = ("INSERT INTO program (program_code, course, college_code) "
                 "VALUES (%s, %s, %s)")
        cursor.execute(query, (program_code, course, college_code))
        conn.commit()
        messagebox.showinfo("Success", "Program added successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def load_program():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM program")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
def delete_program(program_code):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM program WHERE program_code = %s", (program_code,))
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()
def update_program(program_code, course, college_code):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = ("UPDATE program SET course=%s, college_code=%s WHERE program_code=%s")
        cursor.execute(query, (course, college_code, program_code))
        conn.commit()
        messagebox.showinfo("Success", "Program updated successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def sort_program_table(tree, sort_by, order):
    conn = connect_db()
    cursor = conn.cursor()
    
    allowed_columns = {
        "Program Code": "program_code",
        "Course": "course",
        "College Code": "college_code"
    }

    if sort_by not in allowed_columns:
        print(f"Invalid sort column: {sort_by}")
        conn.close()
        return

    sql_column = allowed_columns[sort_by]
    sql_order = "ASC" if order == "Ascending" else "DESC"

    query = f"SELECT program_code, course, college_code FROM program ORDER BY {sql_column} {sql_order};"
    cursor.execute(query)
    rows = cursor.fetchall()

    for item in tree.get_children():
        tree.delete(item)

    for row in rows:
        tree.insert("", "end", values=row)

    cursor.close()
    conn.close()

#College Management Functions
def add_college(college_code, college_name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = ("INSERT INTO college (college_code, college_name) "
                 "VALUES (%s, %s)")
        cursor.execute(query, (college_code, college_name))
        conn.commit()
        messagebox.showinfo("Success", "College added successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def load_colleges():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM college")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def delete_college_by_code(college_code):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM college WHERE college_code = %s", (college_code,))
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def update_college(college_code, college_name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = ("UPDATE college SET college_name=%s WHERE college_code=%s")
        cursor.execute(query, (college_name, college_code))
        conn.commit()
        messagebox.showinfo("Success", "College updated successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def sort_college_table(tree, sort_by, order):
    conn = connect_db()
    cursor = conn.cursor()
    
    allowed_columns = {
        "College Code": "college_code",
        "College Name": "college_name"
    }

    if sort_by not in allowed_columns:
        print(f"Invalid sort column: {sort_by}")
        conn.close()
        return

    sql_column = allowed_columns[sort_by]
    sql_order = "ASC" if order == "Ascending" else "DESC"

    query = f"SELECT college_code, college_name FROM college ORDER BY {sql_column} {sql_order};"
    cursor.execute(query)
    rows = cursor.fetchall()

    for item in tree.get_children():
        tree.delete(item)

    for row in rows:
        tree.insert("", "end", values=row)

    cursor.close()
    conn.close()

   
#making of Main Frame Student
win = Tk.Tk()
win.geometry("1240x700")


page1=Frame(win)
page2=Frame(win)
page3=Frame(win)

for page in(page1, page2, page3):
    page.grid(row=0,column=0,sticky="nsew")

win.rowconfigure(0,weight=1)
win.columnconfigure(0,weight=1)

win.title("Student Management System")
win.config(bg="lightgrey")

title_label = Tk.Label(page1,text="Student Management System",font=("Cambria Math",14,"bold"),border=2,bg="lightblue",foreground="yellow",relief=Tk.GROOVE,)
title_label.pack(side=Tk.TOP, fill=Tk.X,)

detail_frame = Tk.LabelFrame(page1,text="Enter Student Details",font=("Cambria Math",14,),bg=("blue"),fg=("yellow"),bd=12,relief=Tk.GROOVE,)

detail_frame.place(x=10,y=120,width=420,height=575)

data_frame = Tk.Frame(page1,bd=12,bg="lightblue",relief=Tk.GROOVE)
data_frame.place(x=440,y=120,width=800,height=575)

#Variables
id_var = Tk.StringVar()
fname_var = Tk.StringVar()
lname_var = Tk.StringVar()
year_var= Tk.StringVar()
gender_var = Tk.StringVar()
program_var = Tk.StringVar()
search_student_var =Tk.StringVar()

# Label for Student Details
idno_lbl=Tk.Label(detail_frame,text="ID Number ",font=('Arial',12),bg="lightgrey")
idno_lbl.grid(row=0,column=0,padx=2,pady=2)
idno_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=id_var)
idno_ent.grid(row=0,column=1,padx=2,pady=2)

fname_lbl=Tk.Label(detail_frame,text="First Name ",font=('Arial',12),bg="lightgrey")
fname_lbl.grid(row=1,column=0,padx=2,pady=2)
fname_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=fname_var)
fname_ent.grid(row=1,column=1,padx=2,pady=2)

lname_lbl=Tk.Label(detail_frame,text="Last Name ",font=('Arial',12),bg="lightgrey")
lname_lbl.grid(row=2,column=0,padx=2,pady=2)
lname_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=lname_var)
lname_ent.grid(row=2,column=1,padx=2,pady=2)

level_lbl=Tk.Label(detail_frame,text="Year Level ",font=('Arial',12),bg="lightgrey")
level_lbl.grid(row=3,column=0,padx=2,pady=2)
level_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=year_var)
level_ent.grid(row=3,column=1,padx=2,pady=2)

gender_lbl=Tk.Label(detail_frame,text="Gender ",font=('Arial',12),bg="lightgrey")
gender_lbl.grid(row=4,column=0,padx=2,pady=2)
gender_ent=ttk.Combobox(detail_frame,font=('Arial',12),state="readonly",textvariable=gender_var)
gender_ent['values']=("Male","Female","Others")
gender_ent.grid(row=4,column=1,padx=2,pady=2)

programno_lbl=Tk.Label(detail_frame,text="Program Code ",font=('Arial',12),bg="lightgrey")
programno_lbl.grid(row=5,column=0,padx=2,pady=2)
programno_ent=ttk.Combobox(detail_frame,font=("Arial",12),state="readonly", textvariable=program_var)
programno_ent.grid(row=5,column=1,padx=2,pady=2)
update_program_combobox()
#Database Frame
main_frame = Tk.Frame(data_frame,bg="lightgrey",bd=11,relief=Tk.GROOVE)
main_frame.pack(fill=Tk.BOTH,expand=True)

student_table = ttk.Treeview(main_frame, columns=("ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program Code"))

student_table.heading("ID Number",text="ID Number")
student_table.heading("First Name",text="First Name")
student_table.heading("Last Name",text="Last Name")
student_table.heading("Year Level",text="Year Level")
student_table.heading("Gender",text="Gender")
student_table.heading("Program Code",text="Program Code")

student_table['show']='headings'

student_table.column("ID Number",width=100)
student_table.column("First Name",width=100)
student_table.column("Last Name",width=100)
student_table.column("Year Level",width=100)
student_table.column("Gender",width=100)
student_table.column("Program Code",width=100)

student_table.pack(fill=Tk.BOTH,expand=True)

#Student Functions

def refresh_student_table():
    for row in student_table.get_children():
        student_table.delete(row)
    
    offset = current_page_student * items_per_page

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM student LIMIT {items_per_page} OFFSET {offset}")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    for student in students:
        student_table.insert("", Tk.END, values=student)

def student_add():
    if not check_id():
        return

    if not check_yearlevel():
        return

    if not (id_var.get() and fname_var.get() and lname_var.get() and year_var.get() and gender_var.get() and program_var.get()):
        messagebox.showerror("Error", "All fields must be filled!")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE id_number = %s", (id_var.get(),))
    existing = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing:
        messagebox.showerror("Error", "Duplicate ID Number! Student already exists.")
        return

    confirm = messagebox.askyesno("Confirm Add", "Are you sure you want to add this student?")
    if not confirm:
        return

    add_student(id_var.get(), fname_var.get(), lname_var.get(), year_var.get(), gender_var.get(), program_var.get())

    refresh_student_table()
    clear_student_inputs()

def check_id():
    id_value = id_var.get()
    pattern = r"^\d{4}-\d{4}$"
    if not re.fullmatch(pattern, id_value):
        messagebox.showerror("Error", "Invalid ID! Use format YYYY-####.")
        return False
    return True

def check_yearlevel():
    yearlevel_value = year_var.get()
    pattern = r"^\d$"  # Only a single digit number (1-9)
    if not re.fullmatch(pattern, yearlevel_value):
        messagebox.showerror("Error", "Invalid Year Level! Use format # (single number).")
        return False
    return True


def student_edit():
    selected = student_table.selection()
    if not selected:
        messagebox.showerror("Error", "No student selected for editing.")
        return
    
    values = student_table.item(selected[0])['values']
    id_var.set(values[0])
    fname_var.set(values[1])
    lname_var.set(values[2])
    year_var.set(values[3])
    gender_var.set(values[4])
    program_var.set(values[5])
    save_btn.config(state="normal")
    
    
def student_update():
    update_student(id_var.get(), fname_var.get(), lname_var.get(), year_var.get(), gender_var.get(), program_var.get())
    refresh_student_table()
    clear_student_inputs()
    save_btn.config(state="disabled")

def student_delete():
    selected = student_table.selection()
    if selected:
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?")
        if confirm:
            student_id = student_table.item(selected[0])['values'][0]
            delete_student(student_id)   
            refresh_student_table()
            clear_student_inputs()

def student_save():
    student_id = id_var.get()

    if not student_id:
        messagebox.showerror("Error", "ID Number is required.")
        return
    if not (id_var.get() and fname_var.get() and lname_var.get() and year_var.get() and gender_var.get() and program_var.get()):
        messagebox.showerror("Error", "All fields must be filled!")
        return

    confirm = messagebox.askyesno("Confirm Save", "Are you sure you want to save changes?")
    if not confirm:
        return

    # Check if student exists
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE id_number = %s", (student_id,))
    existing_student = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing_student:
        # Student exists then Update
        update_student(
            id_var.get(),
            fname_var.get(),
            lname_var.get(),
            year_var.get(),
            gender_var.get(),
            program_var.get()
        )
    else:
        # Student does not exist then Add 
        add_student(
            id_var.get(),
            fname_var.get(),
            lname_var.get(),
            year_var.get(),
            gender_var.get(),
            program_var.get()
        )

    refresh_student_table()
    clear_student_inputs()

def clear_student_inputs():
    id_var.set("")
    fname_var.set("")
    lname_var.set("")
    year_var.set("")
    gender_var.set("")
    program_var.set("")
    search_student_var.set("")
    save_btn.config(state="disabled")

def prev_page_student():
    global current_page_student
    if current_page_student > 0:
        current_page_student -= 1
        refresh_student_table()

def next_page_student():
    global current_page_student
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM student")
    total_students = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if (current_page_student + 1) * items_per_page < total_students:
        current_page_student += 1
        refresh_student_table()


#Buttons
btn_frame=Tk.Frame(detail_frame,bg="lightgrey",bd=10,relief=Tk.GROOVE)
btn_frame.place(x=20,y=250,width=340,height=200)

#add
add_btn=Tk.Button(btn_frame,bg="lightgrey",text="Add",bd=7,font=("Arial",12),width=15, command=student_add)
add_btn.grid(row=0,column=0,padx=2,pady=2)

#update 
update_btn=Tk.Button(btn_frame,bg="lightgrey",text="Update",bd=7,font=("Arial",12),width=15, command=student_update)
update_btn.grid(row=0,column=1,padx=2,pady=2)


#delete
delete_btn=Tk.Button(btn_frame,bg="lightgrey",text="Delete",bd=7,font=("Arial",12),width=15, command=student_delete)
delete_btn.grid(row=1,column=0,padx=2,pady=2)

edit_btn = Tk.Button(btn_frame, text="Edit",bd=7, font=("Arial", 12), width=15, command=student_edit)
edit_btn.grid(row=1, column=1, padx=2, pady=2)

blank_btn = Tk.Button(btn_frame, text="b", font=("Arial", 1), width=1,height=18)
blank_btn.grid(row=2, column=0, padx=2, pady=2)

save_btn = Tk.Button(btn_frame, text="Save Changes",bd=7, font=("Arial", 12), width=15, command=student_save, state="disabled")
save_btn.grid(row=6, column=0, padx=2, pady=2)

#Search
search_frame=Tk.Frame(data_frame,bg="lightgrey",bd=10,relief=Tk.GROOVE)
search_frame.pack(side=Tk.TOP,fill=Tk.X)

search_lbl=Tk.Label(search_frame,text="Search:",font=("Arial",12),bg="lightgrey")
search_lbl.grid(row=0,column=0,padx=12,pady=2)

search_entry_student = Tk.Entry(search_frame, font=("Arial", 12))  # Student search bar
search_entry_student.grid(row=0, column=1, padx=12, pady=2)

search_btn_student = Tk.Button(search_frame, text="Search", font=("Arial", 12), bd=9, width=14, bg="lightgrey",
                               command=lambda: search_studentdata(student_table, search_entry_student))
search_btn_student.grid(row=0, column=2, padx=12, pady=2)

reset_btn_student = Tk.Button(search_frame, text="Reset", font=("Arial", 12), bd=9, width=14, bg="lightgrey",
                              command=lambda: [search_entry_student.delete(0, Tk.END), refresh_student_table()])
reset_btn_student.grid(row=0, column=3, padx=12, pady=2)                              

# Sort
sort_lbl = Tk.Label(search_frame, text="Sort by:", font=("Arial", 12), bg="lightgrey")
sort_lbl.grid(row=1,column=0,padx=12,pady=2)

sort_opts = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly")
sort_opts["values"] = ("ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program Code")
sort_opts.grid(row=1,column=1,padx=12,pady=2)

order_opts = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly")
order_opts["values"] = ("Ascending", "Descending")
order_opts.grid(row=1,column=2,padx=12,pady=2)

sort_button = Tk.Button(search_frame, text="Sort", font=("Arial", 12),bd=9,width=14,bg="lightgrey",command=lambda: sort_student_table(student_table, sort_opts.get(), order_opts.get()))
sort_button.grid(row=1,column=3,padx=12,pady=2)

pagination_frame = Tk.Frame(data_frame)
pagination_frame.pack(side=Tk.BOTTOM, pady=5)

prev_btn = Tk.Button(pagination_frame, text="<< Prev", command=prev_page_student)
prev_btn.pack(side=Tk.LEFT, padx=10)

next_btn = Tk.Button(pagination_frame, text="Next >>", command=next_page_student)
next_btn.pack(side=Tk.RIGHT, padx=10)
#Program Frame
Tk.Label(page2,text="",font=("Arial", 12))  
title2_label = Tk.Label(
    page2,
    text="Student Management System",
    font=("Cambria Math",14,"bold"),
    border=2,
    bg="lightblue",
    foreground="yellow",
    relief=Tk.GROOVE,
)
title2_label.pack(side=Tk.TOP, fill=Tk.X,)

detail_frame = Tk.LabelFrame(page2,text="Enter Program Details",font=("Cambria Math",14,),bg=("blue"),fg=("yellow"),bd=12,relief=Tk.GROOVE,)

detail_frame.place(x=10,y=120,width=420,height=575)

data_frame = Tk.Frame(page2,bd=12,bg="lightblue",relief=Tk.GROOVE)
data_frame.place(x=440,y=120,width=750,height=575)


#Enter Data For Program

#Variables

college_programno_var=Tk.StringVar()
course_var=Tk.StringVar()
college_var=Tk.StringVar()


# Label for Program Details
college_programno_lbl=Tk.Label(detail_frame,text="Program Code ",font=('Arial',12),bg="lightgrey")
college_programno_lbl.grid(row=0,column=0,padx=2,pady=2)
college_programno_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=college_programno_var)
college_programno_ent.grid(row=0,column=1,padx=2,pady=2)

course_lbl=Tk.Label(detail_frame,text="College Course ",font=('Arial',12),bg="lightgrey")
course_lbl.grid(row=1,column=0,padx=2,pady=2)
course_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=course_var)
course_ent.grid(row=1,column=1,padx=2,pady=2)

college_lbl=Tk.Label(detail_frame,text="College Code ",font=('Arial',12),bg="lightgrey")
college_lbl.grid(row=5,column=0,padx=2,pady=2)
college_ent=ttk.Combobox(detail_frame,font=("Arial",12),state="readonly", textvariable=college_var)
college_ent.grid(row=5,column=1,padx=2,pady=2)
update_college_combobox()

#Database Frame
main_frame = Tk.Frame(data_frame,bg="lightgrey",bd=11,relief=Tk.GROOVE)
main_frame.pack(fill=Tk.BOTH,expand=True)

y_scroll=Tk.Scrollbar(main_frame,orient=Tk.VERTICAL)
x_scroll=Tk.Scrollbar(main_frame,orient=Tk.HORIZONTAL)

program_table=ttk.Treeview(main_frame,columns=("Program Code","Course","College Code"),yscrollcommand=y_scroll.set,xscrollcommand=x_scroll.set)

y_scroll.config(command=program_table.yview)
x_scroll.config(command=program_table.xview)

y_scroll.pack(side=Tk.RIGHT,fill=Tk.Y)
x_scroll.pack(side=Tk.BOTTOM,fill=Tk.X)

program_table.heading("Program Code",text="Program Code")
program_table.heading("Course",text="Course")
program_table.heading("College Code",text="College Code")

program_table['show']='headings'

program_table.column("Program Code",width=100)
program_table.column("Course",width=100)
program_table.column("College Code",width=100)

program_table.pack(fill=Tk.BOTH,expand=True)

#Functions for Program
def is_valid_program_no(program_no):
    """Check if the program code contains only capital letters."""
    return bool(re.fullmatch(r'[A-Z]+', program_no.get()))

def refresh_program_table():
    for row in program_table.get_children():
        program_table.delete(row)
    for program in load_program():
        program_table.insert("", Tk.END, values=program)

def clear_program_inputs():
    college_programno_var.set("")
    course_var.set("")
    college_var.set("")
    save_btn_program.config(state="disabled")

def program_add():
    
    if not is_valid_program_no(college_programno_var):
        messagebox.showerror("Error", "Invalid Program Code! Only capital letters are allowed.")
        return 
    
    if not (college_programno_var.get() and course_var.get() and college_var.get()):
        messagebox.showerror("Error", "All fields must be filled!")
        return
    
    confirm = messagebox.askyesno("Confirm Add", "Are you sure you want to add this Program?")
    if not confirm:
        return
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Check for duplicate Program Code
        cursor.execute("SELECT * FROM program WHERE program_code = %s", (college_programno_var.get(),))
        existing_program = cursor.fetchone()
        
        if existing_program:
            messagebox.showerror("Error", "Duplicate Program Code! Program already exists.")
            return
        
        # Insert new Program
        query = "INSERT INTO program (program_code, course, college_code) VALUES (%s, %s, %s)"
        cursor.execute(query, (college_programno_var.get(), course_var.get(), college_var.get()))
        conn.commit()

        messagebox.showinfo("Success", "Program Data added successfully!")
        
        refresh_program_table()
        update_program_combobox()
        clear_program_inputs()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

    finally:
        cursor.close()
        conn.close()

def program_edit():
    selected = program_table.selection()
    if not selected:
        messagebox.showerror("Error", "No Program selected for editing.")
        return
    
    values = program_table.item(selected[0])['values']
    college_programno_var.set(values[0])
    course_var.set(values[1])
    college_var.set(values[2])
    save_btn_program.config(state="normal")

def program_update():
    confirm = messagebox.askyesno("Confirm Save", "Are you sure you want to save changes?")
    if not confirm:
        return
    
    update_program(college_programno_var.get(), course_var.get(), college_var.get())
    refresh_program_table()
    update_program_combobox()   
    clear_program_inputs()
   

def program_delete():
    selected = program_table.selection()
    if selected:
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this program?")
        if confirm:
            program_code = program_table.item(selected[0])['values'][0]
            delete_program_or_college("program", "program_code", program_code)
            refresh_program_table()
            update_program_combobox() 
            clear_program_inputs()

def search_programdata(table, search_entry):
    search_value = search_entry.get().strip().lower()
    for item in table.get_children():
        table.delete(item)

    conn = connect_db()
    cursor = conn.cursor()
    query = """SELECT * FROM program 
               WHERE LOWER(program_code) LIKE %s 
               OR LOWER(course) LIKE %s 
               OR LOWER(college_code) LIKE %s"""
    search_term = f"%{search_value}%"
    cursor.execute(query, (search_term, search_term, search_term))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    for row in results:
        table.insert("", "end", values=row)

def program_save():
    program_code = college_programno_var.get()

    if not (program_code and course_var.get() and college_var.get()):
        messagebox.showerror("Error", "All fields must be filled!")
        return

    confirm = messagebox.askyesno("Confirm Save", "Are you sure you want to save changes?")
    if not confirm:
        return

    # Check if program exists
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM program WHERE program_code = %s", (program_code,))
    existing_program = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing_program:
        update_program(program_code, course_var.get(), college_var.get())
    else:
        add_program(program_code, course_var.get(), college_var.get())

    refresh_program_table()
    update_program_combobox()
    clear_program_inputs()
    save_btn_program.config(state="disabled")

#Buttons

btn_frame=Tk.Frame(detail_frame,bg="lightgrey",bd=10,relief=Tk.GROOVE)
btn_frame.place(x=20,y=250,width=340,height=200)

#Add
add_btn=Tk.Button(btn_frame,bg="lightgrey",text="Add",bd=7,font=("Arial",12),width=15, command=program_add)
add_btn.grid(row=0,column=0,padx=2,pady=2)

#Update
update_btn=Tk.Button(btn_frame,bg="lightgrey",text="Update",bd=7,font=("Arial",12),width=15, command=program_update)
update_btn.grid(row=0,column=1,padx=2,pady=2)


#Delete
delete_btn=Tk.Button(btn_frame,bg="lightgrey",text="Delete",bd=7,font=("Arial",12),width=15, command=program_delete)
delete_btn.grid(row=1,column=0,padx=2,pady=2)

#Edit
edit_btn = Tk.Button(btn_frame, text="Edit",bd=7, font=("Arial", 12), width=15, command=program_edit)
edit_btn.grid(row=1, column=1, padx=2, pady=2)

blank_btn = Tk.Button(btn_frame, text="b", font=("Arial", 1), width=1,height=18)
blank_btn.grid(row=2, column=0, padx=2, pady=2)

#Save
save_btn_program = Tk.Button(btn_frame, text="Save Changes",bd=7, font=("Arial", 12), width=15, command=program_save, state="disabled")
save_btn_program.grid(row=6, column=0, padx=2, pady=2)


#Search
search_frame=Tk.Frame(data_frame,bg="lightgrey",bd=10,relief=Tk.GROOVE)
search_frame.pack(side=Tk.TOP,fill=Tk.X)

search_lbl=Tk.Label(search_frame,text="Search:",font=("Arial",12),bg="lightgrey")
search_lbl.grid(row=0,column=0,padx=12,pady=2)

search_entry_program = Tk.Entry(search_frame, font=("Arial", 12))  # Program search bar
search_entry_program.grid(row=0, column=1, padx=12, pady=2)

search_btn_program = Tk.Button(search_frame, text="Search", font=("Arial", 12), bd=9, width=14, bg="lightgrey",
                               command=lambda: search_programdata(program_table, search_entry_program))
search_btn_program.grid(row=0, column=2, padx=12, pady=2)

reset_btn_program = Tk.Button(search_frame, text="Reset", font=("Arial", 12), bd=9, width=14, bg="lightgrey",
                              command=lambda: [search_entry_program.delete(0, Tk.END), refresh_program_table()])
reset_btn_program.grid(row=0, column=3, padx=12, pady=2)                              

#Sort
sort_lbl2 = Tk.Label(search_frame, text="Sort by:", font=("Arial", 12), bg="lightgrey")
sort_lbl2.grid(row=1,column=0,padx=12,pady=2)

sort_opts2 = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly")
sort_opts2["values"] = ("Program Code","Course","College Code")
sort_opts2.grid(row=1,column=1,padx=12,pady=2)

order_opts2 = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly")
order_opts2["values"] = ("Ascending", "Descending")
order_opts2.grid(row=1,column=2,padx=12,pady=2)

sort_button2 = Tk.Button(search_frame, text="Sort", font=("Arial", 12),bd=9,width=14,bg="lightgrey", command=lambda: sort_program_table(program_table, sort_opts2.get(), order_opts2.get()))
sort_button2.grid(row=1,column=3,padx=12,pady=2)

#College Frame
Tk.Label(page3,text="",font=("Arial", 12)) 
title3_label = Tk.Label(
    page3,
    text="Student Management System",
    font=("Cambria Math",14,"bold"),
    border=2,
    bg="lightblue",
    foreground="yellow",
    relief=Tk.GROOVE,
)
title3_label.pack(side=Tk.TOP, fill=Tk.X,)

detail_frame = Tk.LabelFrame(page3,text="Enter College Details",font=("Cambria Math",14,),bg=("blue"),fg=("yellow"),bd=12,relief=Tk.GROOVE,)

detail_frame.place(x=10,y=120,width=420,height=575)

data_frame = Tk.Frame(page3,bd=12,bg="lightblue",relief=Tk.GROOVE)
data_frame.place(x=440,y=120,width=750,height=575)

#Enter Data For College

#Variables

college_code_var=Tk.StringVar()
college_name_var=Tk.StringVar()



# Label for College Details
college_code_lbl=Tk.Label(detail_frame,text="College Code ",font=('Arial',12),bg="lightgrey")
college_code_lbl.grid(row=0,column=0,padx=2,pady=2)
college_code_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=college_code_var)
college_code_ent.grid(row=0,column=1,padx=2,pady=2)

college_name_lbl=Tk.Label(detail_frame,text="Name of College",font=('Arial',12),bg="lightgrey")
college_name_lbl.grid(row=1,column=0,padx=2,pady=2)
college_name_ent=Tk.Entry(detail_frame,bd=7,font=("Arial",12),textvariable=college_name_var)
college_name_ent.grid(row=1,column=1,padx=2,pady=2)

#Database Frame

main_frame = Tk.Frame(data_frame,bg="lightgrey",bd=11,relief=Tk.GROOVE)
main_frame.pack(fill=Tk.BOTH,expand=True)

y_scroll=Tk.Scrollbar(main_frame,orient=Tk.VERTICAL)
x_scroll=Tk.Scrollbar(main_frame,orient=Tk.HORIZONTAL)

college_table=ttk.Treeview(main_frame,columns=("College Code","College Name"),yscrollcommand=y_scroll.set,xscrollcommand=x_scroll.set)

y_scroll.config(command=college_table.yview)
x_scroll.config(command=college_table.xview)

y_scroll.pack(side=Tk.RIGHT,fill=Tk.Y)
x_scroll.pack(side=Tk.BOTTOM,fill=Tk.X)

college_table.heading("College Code",text="College Code")
college_table.heading("College Name",text="College Name")

college_table['show']='headings'

college_table.column("College Code",width=100)
college_table.column("College Name",width=100)

college_table.pack(fill=Tk.BOTH,expand=True)

#College Functions
def refresh_college_table():
    for row in college_table.get_children():
        college_table.delete(row)
    for college in load_colleges():
        college_table.insert("", Tk.END, values=college)

def clear_college_inputs():
    college_code_var.set("")
    college_name_var.set("")
    save_btn_college.config(state="disabled")

def college_add():
    confirm = messagebox.askyesno("Confirm Add", "Are you sure you want to add this College?")
    if not confirm:
        return

    if not is_valid_program_no(college_code_var):
        messagebox.showerror("Error", "Invalid College Code! Only capital letters are allowed.")
        return 

    college_no = college_code_var.get().strip()
    college_name_val = college_name_var.get().strip()

    if not (college_no and college_name_val):
        messagebox.showerror("Error", "All fields must be filled!")
        return

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM college WHERE college_code = %s", (college_no,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Duplicate College Code! Already exists.")
            return

        cursor.execute("SELECT * FROM college WHERE college_name = %s", (college_name_val,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Duplicate College Name! Already exists.")
            return
    finally:
        cursor.close()
        conn.close()

    # Add to database
    add_college(college_no, college_name_val)
    refresh_college_table()
    update_college_combobox()
    clear_college_inputs()


def college_edit():
    selected = college_table.selection()
    if not selected:
        messagebox.showerror("Error", "No college selected for editing.")
        return
    values = college_table.item(selected[0])['values']
    college_code_var.set(values[0])
    college_name_var.set(values[1])
    save_btn_college.config(state="normal")

def college_update():
    confirm = messagebox.askyesno("Confirm Save", "Are you sure you want to save changes?")
    if not confirm:
        return
    
    update_college(college_code_var.get(), college_name_var.get())
    refresh_college_table()
    update_college_combobox()
    clear_college_inputs()
    save_btn_college.config(state="disabled")

def college_delete():
    selected = college_table.selection()
    if selected:
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this college?")
        if confirm:
            college_code = college_table.item(selected[0])['values'][0]
            delete_program_or_college("college", "college_code", college_code)
            refresh_college_table()
            update_college_combobox()
            clear_college_inputs()

def search_college_data(table, search_entry):
    search_value = search_entry.get().strip().lower()
    for item in table.get_children():
        table.delete(item)

    conn = connect_db()
    cursor = conn.cursor()
    query = """SELECT * FROM college 
               WHERE LOWER(college_code) LIKE %s 
               OR LOWER(college_name) LIKE %s"""
    search_term = f"%{search_value}%"
    cursor.execute(query, (search_term, search_term))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    for row in results:
        table.insert("", "end", values=row)

def college_save():
    college_code = college_code_var.get()

    if not (college_code and college_name_var.get()):
        messagebox.showerror("Error", "All fields must be filled!")
        return

    confirm = messagebox.askyesno("Confirm Save", "Are you sure you want to save changes?")
    if not confirm:
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM college WHERE college_code = %s", (college_code,))
    existing_college = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing_college:
        update_college(college_code, college_name_var.get())
    else:
        add_college(college_code, college_name_var.get())

    refresh_college_table()
    update_college_combobox()
    clear_college_inputs()
    save_btn_college.config(state="disabled")


#Buttons

btn_frame=Tk.Frame(detail_frame,bg="lightgrey",bd=10,relief=Tk.GROOVE)
btn_frame.place(x=20,y=250,width=340,height=200)

#Add
add_btn=Tk.Button(btn_frame,bg="lightgrey",text="Add",bd=7,font=("Arial",12),width=15, command=college_add)
add_btn.grid(row=0,column=0,padx=2,pady=2)

#Update
update_btn=Tk.Button(btn_frame,bg="lightgrey",text="Update",bd=7,font=("Arial",12),width=15, command=college_update)
update_btn.grid(row=0,column=1,padx=2,pady=2)


#Delete
delete_btn=Tk.Button(btn_frame,bg="lightgrey",text="Delete",bd=7,font=("Arial",12),width=15, command=college_delete)
delete_btn.grid(row=1,column=0,padx=2,pady=2)

#Edit
edit_btn = Tk.Button(btn_frame, text="Edit",bd=7, font=("Arial", 12), width=15, command=college_edit)
edit_btn.grid(row=1, column=1, padx=2, pady=2)

blank_btn = Tk.Button(btn_frame, text="b", font=("Arial", 1), width=1,height=18)
blank_btn.grid(row=2, column=0, padx=2, pady=2)

#Save
save_btn_college = Tk.Button(btn_frame, text="Save Changes",bd=7, font=("Arial", 12), width=15, command=college_save, state="disabled")
save_btn_college.grid(row=6, column=0, padx=2, pady=2)

#Search
search_frame=Tk.Frame(data_frame,bg="lightgrey",bd=10,relief=Tk.GROOVE)
search_frame.pack(side=Tk.TOP,fill=Tk.X)

search_lbl=Tk.Label(search_frame,text="Search:",font=("Arial",12),bg="lightgrey")
search_lbl.grid(row=0,column=0,padx=12,pady=2)

search_entry_college = Tk.Entry(search_frame, font=("Arial", 12))  # College search bar
search_entry_college.grid(row=0, column=1, padx=12, pady=2)

search_btn_college = Tk.Button(search_frame, text="Search", font=("Arial", 12), bd=9, width=14, bg="lightgrey",
                               command=lambda: search_college_data(college_table, search_entry_college))
search_btn_college.grid(row=0, column=2, padx=12, pady=2)

reset_btn_college = Tk.Button(search_frame, text="Reset", font=("Arial", 12), bd=9, width=14, bg="lightgrey",
                              command=lambda: [search_entry_college.delete(0, Tk.END), refresh_college_table()])
reset_btn_college.grid(row=0, column=3, padx=12, pady=2)                              

#Sort
sort_lbl3 = Tk.Label(search_frame, text="Sort by:", font=("Arial", 12), bg="lightgrey")
sort_lbl3.grid(row=1,column=0,padx=12,pady=2)

sort_opts3 = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly")
sort_opts3["values"] = ("College Code","College Name")
sort_opts3.grid(row=1,column=1,padx=12,pady=2)

order_opts3 = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly")
order_opts3["values"] = ("Ascending", "Descending")
order_opts3.grid(row=1,column=2,padx=12,pady=2)

sort_button3 = Tk.Button(search_frame, text="Sort", font=("Arial", 12), command=lambda: sort_college_table(college_table, sort_opts3.get(), order_opts3.get()))
sort_button3.grid(row=1,column=3,padx=12,pady=2)

#Navigation Buttons
Tk.Button(page1,text="Student",command=lambda:page1.tkraise(),font=("Arial",12)).place(x=55, y=582, width=100, height=40)
Tk.Button(page1,text="Program",command=lambda:[page2.tkraise(),refresh_program_table()],font=("Arial",12)).place(x=160, y=582, width=100, height=40)
Tk.Button(page1,text="College",command=lambda:[page3.tkraise(),refresh_college_table()],font=("Arial",12)).place(x=265, y=582, width=100, height=40)
Tk.Button(page2,text="Student",command=lambda:[page1.tkraise(),refresh_student_table()],font=("Arial",12)).place(x=55, y=582, width=100, height=40)
Tk.Button(page2,text="Program",command=lambda:[page2.tkraise(),refresh_program_table()],font=("Arial",12)).place(x=160, y=582, width=100, height=40)
Tk.Button(page2,text="College",command=lambda:[page3.tkraise(),refresh_college_table()],font=("Arial",12)).place(x=265, y=582, width=100, height=40)
Tk.Button(page3,text="Student",command=lambda:[page1.tkraise(),refresh_student_table()],font=("Arial",12)).place(x=55, y=582, width=100, height=40)
Tk.Button(page3,text="Program",command=lambda:[page2.tkraise(),refresh_program_table()],font=("Arial",12)).place(x=160, y=582, width=100, height=40)
Tk.Button(page3,text="College",command=lambda:[page3.tkraise(),refresh_college_table()],font=("Arial",12)).place(x=265, y=582, width=100, height=40)

refresh_student_table()
page1.tkraise()
win.mainloop()
