from flask import Flask, render_template, request, redirect, session
import mysql.connector
import random
import string

app = Flask(__name__)
app.secret_key = "pass"

my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456",
    database="cdms"
)
cursor = my_db.cursor()

global allowed_routes
allowed_routes = ["login", "static","logout"]

@app.route('/login',  methods=["GET", "POST"])
def login():
    global allowed_routes
    allowed_routes = ["login", "static"]
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        query = "select type from auth where binary userid = %s and binary password =%s"
        value = [username, password]
        cursor.execute(query, value)
        auth = cursor.fetchall()

        if auth: 
            session["authenticated"] = True
            session["username"] = username
            type = auth[0][0]
            print(username,type, " authentication successful")

            if type == "student":
                allowed_routes = ["login","static","logout", "student"]
                return redirect('/student')

            elif type == "staff":
                allowed_routes = ["login", "static","logout",
                                  "staff", "add_details_staff","error"]
                return redirect('/staff')

            elif type == "tutor":
                allowed_routes = ["login", "static","logout", "tutor"]
                return redirect('/tutor')
            
            elif type == "admin":
                allowed_routes=["login","static","logout","admin","admin_table","edit"]
                return redirect('/admin')

        else:
            error = "Invalid Username or Password. Please try again."
            return render_template("login.html", error=error)
    return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    print(session["username"],"logged out")
    session.clear()
    return redirect("/login")


@app.route('/student')
def student():
    if session.get("username"):
        userid = [session.get("username")]

        query = "select * from details where userid = %s"
        cursor.execute(query, userid)
        details = cursor.fetchall()

        query = "select * from dues where userid = %s"
        cursor.execute(query, userid)
        dues = cursor.fetchall()

        return render_template("student.html", details=details, dues=dues)
    else:
        return redirect("/login")




@app.route('/add_details_staff',  methods=["GET", "POST"])
def add_details_staff():
    try:
        userid = [session.get("username")]

        query = "select * from details where userid =%s"
        cursor.execute(query, userid)
        details = cursor.fetchall()

        name = request.args.get('name')
        amt = request.args.get('amt')
        print("Due update : ",name, amt)
        query = "update dues set "+details[0][1] + \
            " = "+details[0][1]+" + %s where userid = %s "
        value = [amt, name]
        cursor.execute(query, value)
        my_db.commit()

        return redirect("/staff")
    except:
        return redirect("/staff")
    
@app.route('/staff',  methods=["GET", "POST"])  
def staff():
    if session.get("username"):
        if request.method == "POST":
            name = request.form['username']
            amt = request.form['amount']
            return redirect(f"/add_details_staff?name={name}&amt={amt}")

        else:
            userid = [session.get("username")]

            query = "select * from details where userid =%s"
            cursor.execute(query, userid)
            details = cursor.fetchall()

            query = "select details.userid,name,dues." + \
                details[0][1] + \
                    " from details,dues where details.userid=dues.userid ORDER BY dues.updated_at DESC"
            cursor.execute(query)
            dues = cursor.fetchall()

            return render_template("staff.html", details=details, dues=dues,err="")
    else:
        return redirect("/login")
    

@app.route('/tutor')
def tutor():
    if session.get("username"):
        userid = [session.get("username")]

        query = "select * from details where userid = %s"
        cursor.execute(query, userid)
        details = cursor.fetchall()

        query = " select details.userid,details.name,dues.canteen,dues.store,dues.bus,dues.office from details,dues where details.userid=dues.userid and details.tutorid = %s"
        cursor.execute(query, userid)
        dues = cursor.fetchall()

        return render_template("tutor.html", details=details, dues=dues)
    else:
        return redirect("/login")

def generate_password(length):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/admin', methods=["GET", "POST"])
def admin():
    if session.get("username"):
        if request.method == "POST":
            if 'add_user' in request.form:
                id = request.form['userid']
                password = generate_password(7)
                type = request.form['type']
                name = request.form['name']
                dept = request.form['dept']
                year = request.form['year']
                tutor = request.form['tutor']

                query = "insert into auth values (%s,%s,%s)" 
                values = [id, password, type]
                cursor.execute(query, values)

                query = "insert into details values (%s,%s,%s,%s,%s) "
                values = [id, name, dept, year, tutor]
                cursor.execute(query, values)

                if type == "student":
                    query = "insert into dues (userid,Canteen,Store,Bus,Office) values (%s,0,0,0,0)"
                    values = [id]
                    cursor.execute(query, values)

                my_db.commit()
            
            return redirect("/admin")
        
            

        else:
            query = "select auth.userid,auth.password,auth.type,details.name,details.dept,details.year,details.tutorid from auth,details where auth.userid=details.userid order by userid"
            cursor.execute(query)
            table = cursor.fetchall()

            query = "select auth.userid,details.name from auth,details where auth.userid=details.userid and auth.type='tutor'"
            cursor.execute(query)
            tutors = cursor.fetchall()

            return render_template("admin.html", table=table,tutors=tutors)
    else:
        return redirect("/login")


@app.route('/admin_table', methods=["GET", "POST"])
def admin_table():
    if 'delete_user' in request.form:
        user_id = request.form['user_id']
        id=[user_id]


        query = "delete from dues where userid = %s"
        cursor.execute(query,id)

        query = "delete from details where userid = %s"
        cursor.execute(query,id)

        query = "delete from auth where userid = %s"
        cursor.execute(query,id)

        my_db.commit()

        return redirect('/admin')
    elif 'edit_user' in request.form:
        user_id = request.form['user_id']
        return redirect(f"/edit?id={user_id}")

        return redirect('/admin')
    else :
        return redirect('/admin')
    
@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        id = request.form['userid']
        password = request.form['password']
        type = request.form['type']

        name = request.form['name']
        dept = request.form['dept']
        year = request.form['year']
        tutor = request.form['tutor']

        query = "update auth set password=%s,type=%s where userid=%s"
        values = [password,type,id]
        cursor.execute(query,values)

        query = "update details set name=%s,dept=%s,year=%s,tutorid=%s where userid=%s"
        values = [name,dept,year,tutor,id]
        cursor.execute(query,values)

        my_db.commit()

        return redirect('/admin')        

    else :
        query = "select auth.userid,auth.password,auth.type,details.name,details.dept,details.year,details.tutorid from auth,details where auth.userid=details.userid order by userid"
        cursor.execute(query)
        table = cursor.fetchall()

        query = "select auth.userid,details.name from auth,details where auth.userid=details.userid and auth.type='tutor'"
        cursor.execute(query)
        tutors = cursor.fetchall()

        id = request.args.get('id')
        query = "select auth.userid,auth.password,auth.type,details.name,details.dept,details.year,details.tutorid from auth,details where auth.userid=details.userid and auth.userid=%s order by userid"
        values = [id]
        cursor.execute(query,values)
        edit = cursor.fetchall()

        return render_template("edit.html", table=table,tutors=tutors,edit=edit)

@app.before_request
def require_login():
    if request.endpoint not in allowed_routes :
        return redirect("/login")


@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

if __name__ == '__main__':
    app.run()