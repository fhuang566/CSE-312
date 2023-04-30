import bcrypt
import pymongo
import secrets
import hashlib
import funtions
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, flash, make_response, url_for
from flask_socketio import SocketIO
from markupsafe import escape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

mongo_client = pymongo.MongoClient('mongo')
db = mongo_client["cse312"]
userCollection = db["users"]
contentCollection = db["content"]
auth_tokenCollection = db["auth_token"]
xsrf_tokenCollection = db["xsrf_token"]
coursesCollection = db['courses']


@app.route('/')
def index():
    token = request.cookies.get("auth_token")
    if token:
        return redirect("/courses")
    return render_template('index.html')

@app.route('/register', methods=["POST"])
def signup():
    username = request.form['username']
    password = request.form["password"]
    user = userCollection.find_one({"username": username})
    contents = {"username": username}
    response = make_response(redirect("/"))
    response.headers
    if user:
        flash("Username alredy in use. Please try again!", "error")
        
    else:
        salt = bcrypt.gensalt()
        contents["salt"] = salt
        contents["password"] = bcrypt.hashpw(password.encode(),salt)
        userCollection.insert_one(contents)
        flash("Register Successful! Please Login!", "success")
        
        
    return redirect("/")

@app.route('/login', methods=["POST"])
def login():
    username = request.form['username']
    password = request.form["password"]
    user = userCollection.find_one({"username": username})
    if user:
        if bcrypt.checkpw(password.encode(), user["password"]):
            print("logged in")
            expire = datetime.now(timezone.utc) + timedelta(days=30)
            expiredate = expire.strftime("%a, %d-%b-%Y %H:%M:%S GMT;")
            auth_token = secrets.token_urlsafe(16)
            auth_tokenCollection.update_one({"username": username}, {"$set":{"username": username, "auth_token": hashlib.sha256(auth_token.encode()).digest()}}, upsert=True)
            response = make_response(redirect('/courses'))
            response.set_cookie("auth_token",  auth_token, path="/", expires=expiredate, secure=True, httponly=True)
            return response

    
    flash("Incorrect username or password. Try again!", "error")
    return redirect("/")

@app.route('/courses', methods=["GET"])
def courses():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
    # if token:
    #     hashed = hashlib.sha256(token.encode())
    #     user = auth_tokenCollection.find_one({"auth_token": hashed.digest()})
    #     if user:
        return render_template('courses.html', username = auth )

    return "403	Forbidden", 403

@app.route('/allCourses')
def allCourses():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        cur = coursesCollection.find({})
        cur = list(cur)
        for x in cur:
            del x['_id']
        return json.dumps(cur)
    
@app.route('/myCourses')
def myCourses():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        cur = contentCollection.find({"instructor" : auth})
        cur = list(cur)
        cur1 = contentCollection.find({"students": auth })
        cur = cur + list(cur1)
        for x in cur:
            del x['_id']
        return json.dumps(cur)


@app.route('/createCourse', methods=["POST"])
def create():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        coursename = request.form["coursename"]
        if len(coursename) == 0 and coursename.isspace():
            flash("Invalid input. Try again!", "error")
            return redirect("/courses")
        else:
            courseId = secrets.token_urlsafe(8)
            course = {"courseId": courseId, "coursename": coursename, "instructor": auth, "students": []}
            coursesCollection.insert_one(course)
            return redirect("/course?courseId=" + courseId )
    return "403	Forbidden", 403
        

@app.route('/course')
def course():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    course = coursesCollection.find_one({"courseId": request.args["courseId"]})
    if auth and course:
        if course["instructor"] == auth:
            return render_template("instructorview.html")
        elif auth in course["student"]:
            return render_template("studenview.html")
        else:
            return render_template("enroll.html", coursename = course["coursename"], courseId = course["courseId"])
            
@app.route('/enroll')
def enroll():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    #course = coursesCollection.find_one({"courseId": request.form["courseId"]})
    if auth:
        print(request.form["courseId"])

if __name__ == '__main__':
    socketio.run(app, debug = True, host='0.0.0.0', port = 8000, allow_unsafe_werkzeug=True)