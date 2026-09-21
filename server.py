import sqlite3
import os
from flask import Flask,render_template,request,redirect,make_response, session
from werkzeug.security import generate_password_hash, check_password_hash
app=Flask(__name__)
app.secret_key = "mysecretkey"
database = os.path.join(os.path.dirname(__file__), "navya.db")

def Create_database():
    #connect to database
    connection=sqlite3.connect(database)
    print("Database location:", database)
    # store database in some object
    cursor=connection.cursor()
    # write query using that object
    # cursor.execute("""create table if not exists users(
    # id integer primary key autoincrement,
    # fullname text not null,
    # username text unique not null,
    # password text not null)""")
    cursor.execute("""create table if not exists users( 
    id integer primary key autoincrement, 
    fullname text not null, 
    username text unique not null, 
    password text not null,
    email text,
    phone text,
    dob text,
    gender text,
    address text,
    city text,
    state text,
    country text,
    pincode text,
    hobbies text)""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees_new(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employeename TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER NOT NULL,
            address TEXT,
            joining TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")

    old_employees = cursor.fetchone()

    if old_employees:
        cursor.execute("DROP TABLE employees")

    cursor.execute("""
        ALTER TABLE employees_new RENAME TO employees
    """)

    # commit query
    connection.commit()
    # close connection 
    connection.close() 

#----login check----#
def login_required():
    return "user_id" in session

#------Theme-----#
@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in["light","dark"]:
        theme="light"
    previous_page = request.referrer or"/"
    response = make_response(
        redirect(previous_page)
    )
    response.set_cookie(
        "theme",theme,max_age=60*60*24*365
    )
    return response

#----Home Page---#
@app.route("/")
def home():
     if not login_required():
         return redirect("/login")
     theme=request.cookies.get(
             "theme",
             "light"
         )
     username=session.get("username")
     fullname=session.get("fullname")
     return render_template("nav.html",theme=theme,username=username,fullname=fullname)

#----Register Page:Get----#
@app.route("/register", methods=["GET"])
def register_page():
    theme = request.cookies.get(
        "theme",
        "light"
    )
    return render_template("reg.html",theme=theme) 

#-----Register Page:Post---#
@app.route("/register", methods=["POST"])
def register():
    fullname= request.form.get("fullname"," ").strip()
    username= request.form.get("username"," ").strip()
    password= request.form.get("password"," ").strip()
    email = request.form.get("email"," ").strip()
    phone = request.form.get("phone"," ").strip()
    dob = request.form.get("dob"," ").strip()
    gender = request.form.get("gender"," ").strip()
    address = request.form.get("address"," ").strip()
    city = request.form.get("city"," ").strip()
    state = request.form.get("state"," ").strip()
    country = request.form.get("country"," ").strip()
    pincode = request.form.get("pincode"," ").strip()
    hobbies = ", ".join(request.form.getlist("hobbies"))
    #----validation----#
    if not fullname:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="fullname is required")
    if not username:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="username is required")
    if not password:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="password is required")
    if not email:
         return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="email is required")
    if not phone:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="phone is required")
    if not dob:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="dob is required")
    if not gender:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="gender is required")
    if not address:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="address is required")
    if not city:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="city is required")
    if not state:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="state is required")
    if not country:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="country is required")
    if not pincode:
        return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="pincode is required")
    if not hobbies:
         return render_template("reg.html",
            theme=request.cookies.get("theme","light"),
            error="hobbies is required")
    
#------Hash Password-----#
    hashed_password = generate_password_hash(password)

#--------insert Useer--------#
    connection=sqlite3.connect(database)
    cursor=connection.cursor()
    try: 
        cursor.execute("""
            INSERT INTO users(fullname,username,password,email,phone,dob,gender,address,city,state,country,pincode,hobbies)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,(fullname,username,hashed_password,email,phone,dob,gender,address,city,state,country,pincode,hobbies)
            )      
        connection.commit()
        connection.close()
        return redirect("/login")
    except sqlite3.IntegrityError:
        connection.close()
        return render_template("reg.html",
                theme=request.cookies.get("theme","light"),
                error="username already exists.")

#------Login Page:GET------#
@app.route("/login", methods=["GET"])  
def login_page():
    if "user_id" in session:
        return redirect("/")
    theme=request.cookies.get("theme","light")
    return render_template("login.html",theme=theme)

#------Login Page:POST------#
@app.route("/login", methods=["POST"])
def login():
    #------GET FORM VALUES-----#
    username= request.form.get("username","").strip()
    password= request.form.get("password","")

    ##-------VALIDATION--------##
    if not username or not password:
        return render_template("login.html",
            theme=request.cookies.get("theme","light"),
            error="Username and password are required."
        )

    ##------Find User-----##
    connection=sqlite3.connect(database)
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username=?
        """,(username,))

    user=cursor.fetchone()

    ##------User Not Found------##
    if user is None:
        connection.close()
        return render_template("login.html",
            theme=request.cookies.get("theme","light"),
            error="Username or password is incorrect."
        )

    ##------CHECK Password------##
    try:
        password_correct=check_password_hash(user["password"],password)
    except:
        password_correct=False

    if not password_correct and user["password"] == password:
        password_correct=True

    if not password_correct:
        connection.close()
        return render_template("login.html",
            theme=request.cookies.get("theme","light"),
            error="Username or password is incorrect."
        )

    connection.close()

    ##-----Login Success-----##
    session.clear()
    session["user_id"]=user["id"]
    session["username"]=user["username"]
    session["fullname"]=user["fullname"]

    return redirect("/")

##------Logout-----##
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

##------Add Employee:GET----##
@app.route("/add", methods=["GET"])
def add_page():
    if not login_required():
        return redirect("/login")
    theme=request.cookies.get("theme","light")
    return render_template("add.html",theme=theme)

##------ADD EMPLOYEE:POST------##     
@app.route("/add", methods=["POST"])
def add():
    if not login_required():
        return redirect("/login")
    employeename= request.form.get("employeename"," ").strip()
    email = request.form.get("email"," ").strip()
    phone = request.form.get("phone"," ").strip()
    department = request.form.get("department"," ").strip()
    salary = request.form.get("salary"," ").strip()
    address = request.form.get("address"," ").strip()
    joining = request.form.get("joining"," ").strip()

##------VALIDATION-------##
    if not employeename:
        return "Employeename is required!"
    if not email:
        return "email is required!"
    if not phone:
        return "phone is required!"
    if not department:
        return "department is required!"
    if not salary:
        return "salary is required!"
    if not address:
        return "address is required!"
    if not joining:
        return "joining is required!"
    try:
        salary = int(salary)
    except ValueError:
        return "Salary must be a number!"
    
    ##-----INSERT EMPLOYEE------##
    connection=sqlite3.connect(database)
    cursor=connection.cursor() 
    cursor.execute("""
            INSERT INTO employees(employeename,email,phone,department,salary,address,joining)
            VALUES(?,?,?,?,?,?,?)
            """,(employeename,email,phone,department,salary,address,joining
                ))      
    connection.commit()
    connection.close()
    return redirect("/employees")

##-------EMPLOYEES-------##
@app.route("/employees")
def employees():
    if not login_required():
        return redirect("/login")
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, employeename, email, phone, department, salary, address, joining
        FROM employees
        ORDER BY id DESC
    """)
    employees = cursor.fetchall()
    connection.close()
    theme = request.cookies.get("theme","light")
    search_text = ""
    return render_template("employees.html", employees=employees,theme=theme,search_text=search_text)

##-----SEARCH-----##
@app.route("/search")
def search():
    if not login_required():
        return redirect("/login")
    search_text = request.args.get("q","").strip()
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    if search_text:
        search_value = f"%{search_text}%"
        cursor.execute("""
            SELECT id, employeename, email, phone, department, salary, address, joining
            FROM employees
            WHERE employeename LIKE ?
            OR email LIKE ?
            OR phone LIKE ?
            OR department LIKE ?
            ORDER BY id DESC
        """, (
            search_value,
            search_value,
            search_value,
            search_value
        ))
    else:
        cursor.execute("""
            SELECT id, employeename, email, phone, department, salary, address, joining
            FROM employees
            ORDER BY id DESC""")
    employees = cursor.fetchall()
    connection.close()
    theme=request.cookies.get("theme","light")
    return render_template("employees.html", employees=employees,theme=theme,search_text=search_text)

   ##------DELETE EMPLOYEE------##
@app.route("/delete-employee/<email>")
def delete_employee(email):
    if not login_required():
            return redirect("/login")
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM employees WHERE email = ?", (email,))
    connection.commit()
    connection.close()
    return redirect("/employees")

##-------EDIT EMPLOYEE:GET------##
@app.route("/edit-employee/<email>", methods=["GET"])
def edit_employee_page(email):
    if not login_required():
            return redirect("/login")
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, employeename, email, phone, department, salary, address, joining
        FROM employees
        WHERE email=?
    """,(email,))
    employee=cursor.fetchone()
    connection.close()
    if employee is None:
        return """ <h2>Employee not found!</h2>
        <a href="/employees">Back to Employes</a>"""
    theme=request.cookies.get("theme","light")
    return render_template("edit-employee.html",employee=employee,theme=theme)

##-------EDIT EMPLOYEE:POST-------##
@app.route("/edit-employee/<email>", methods=["POST"])
def edit_employee(email):
    if not login_required():
            return redirect("/login")
    employeename= request.form.get("employeename"," ").strip()
    new_email = request.form.get("email"," ").strip()
    phone = request.form.get("phone"," ").strip()
    department = request.form.get("department"," ").strip()
    salary = request.form.get("salary"," ").strip()
    joining = request.form.get("joining"," ").strip()
    address = request.form.get("address"," ").strip()

    ##------VALIDATION-------##
    if not employeename:
        return "Employeename is required!"
    if not new_email:
        return "new_email is required!"
    if not phone:
        return "phone is required!"
    if not department:
        return "department is required!"
    if not salary:
        return "salary is required!"
    if not address:
        return "address is required!"
    if not joining:
        return "joining is required!"
    try:
        salary = int(salary)
    except ValueError:
        return "Salary must be a number!"
    
##------UPDATE EMPLOYEE------##
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""
            UPDATE employees
            SET employeename = ?,
                email = ?,
                phone = ?,
                department = ?,
                salary = ?,
                address = ?,
                joining = ? WHERE email = ?
        """, (employeename,new_email, phone, department, salary, address, joining,email))
    connection.commit()
    connection.close()
    return redirect("/employees")

##------START APPLICATION-----##
if __name__=="__main__":
    Create_database()
    app.run(debug=True)