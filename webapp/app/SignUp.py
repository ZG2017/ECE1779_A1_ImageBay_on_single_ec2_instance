from flask import render_template, url_for, request, redirect, session,g
from app import webapp
from app import sql
import hashlib
import base64
import os

# add salt and hash the password
def Pwd2Hash(password,salt=None):
    password = password.encode()
    if not salt:
        salt = base64.b64encode(os.urandom(32))
    hashInput = hashlib.sha256(salt+password).hexdigest()
    return hashInput,salt

# show signup page
@webapp.route("/signup", methods = ["GET","POST"])
def SignUp():
    username = None
    error = None
    email = None    
    if "username" in session:
        username = session["username"]
    if "error" in session:
        error = session["error"]
    if "email" in session:
        email = session["email"]
    return render_template("signup.html",title = "ImageBay", email = email, error = error, username = username)

# check if user info are valid and submit the info 
@webapp.route("/signup_submit",methods = ["POST"])
def SignUpSubmit():
    error = ""
    # check if name is valid
    if "username" in request.form:
        if request.form["username"] == "":
            error += "Please enter a username.\n"
        elif len(request.form["username"]) > 20:
            error += "The username is too long. Please retry.\n"
        for char in request.form["username"]:
            if char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_":
                error += "Username should only contain letters, numbers and '_'.\n"
                break
    
    # check if name already exsist
    cnx = sql.get_db()
    cursor = cnx.cursor()
    query = ''' SELECT * FROM userInfo WHERE userName = %s '''
    cursor.execute(query,(request.form["username"],))
    row = cursor.fetchone()
    if row == None:
        session["username"] = request.form["username"]
    else:
        session["error"] = "Username has been taken. Please choose another name!\n"
        return redirect(url_for("SignUp"))

    # check if email is entered or taken
    if "email" in request.form:
        if request.form["email"] == "":
            error += "Please enter the email address.\n"
    query = ''' SELECT * FROM userInfo WHERE userEmail = %s '''
    cursor.execute(query,(request.form["email"],))
    row = cursor.fetchone()
    if row == None:
        session["email"] = request.form["email"]
    else:
        session["error"] = "Email address has been taken. Please choose another!\n"
        return redirect(url_for("SignUp"))
    session["email"] = request.form["email"]
    
    # check if password are match
    if "password" in request.form and "com_password" in request.form:
        if request.form["password"] == "" or request.form["com_password"] == "":
            error += "Please enter the password or password comfirm.\n"
        elif request.form["password"] != request.form["com_password"]:
            error += "password doesn't match the comfirm password.\n"
    
    if error != "":
        session["error"] = error
        return redirect(url_for("SignUp"))
    else:
        session['authenticated'] = True
        
    # save userinfo
    pwd,salt = Pwd2Hash(request.form["password"], salt = None)
    cnx = sql.get_db()
    cursor = cnx.cursor()
    query = ''' INSERT INTO userInfo (userName, userEmail, userPwd, userSalt)
                       VALUES (%s,%s,%s,%s)
    '''
    
    cursor.execute(query,(request.form["username"],request.form["email"],pwd,salt))
    cnx.commit()
    session["error"] = None
    return redirect(url_for("HomePage"))
    
