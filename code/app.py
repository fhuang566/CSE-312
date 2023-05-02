import bcrypt
import pymongo
import secrets
import hashlib
import funtions
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, flash, make_response, url_for
from flask_socketio import SocketIO, send, emit, join_room
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
        return render_template('courses.html', username = escape(auth) )

    return "403	Forbidden", 403

@app.route('/allCourses')
def allCourses():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        cur = coursesCollection.find({})
        cur = list(cur)
        for x in cur:
            del x['_id']
            x["coursename"] = escape(x["coursename"])
            x["instructor"] = escape(x["instructor"])
        return json.dumps(cur)
    
@app.route('/myCourses')
def myCourses():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        cur = coursesCollection.find({'$or': [{"instructor": auth}, {"students": auth}]})
        cur = list(cur)
        for x in cur:
            del x['_id']
            x["coursename"] = escape(x["coursename"])
            x["instructor"] = escape(x["instructor"])
        return json.dumps(cur)
    
@app.route('/myQuestions')
def myQuestions():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        cur = coursesCollection.find_one({"courseId": request.args.get("courseId")})
        if cur:
            return json.dumps(cur["questions"])


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
            course = {"courseId": courseId, "coursename": coursename, "instructor": auth, "students": [], "questions": []}
            coursesCollection.insert_one(course)
            return redirect("/course?courseId=" + courseId )
    return "403	Forbidden", 403
        

@app.route('/course')
def course():
    courseid = request.args.get("courseId")
    if not courseid:
        return redirect("/courses")
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    course = coursesCollection.find_one({"courseId": courseid})
    if auth and course:
        if course["instructor"] == auth:
            cur = coursesCollection.aggregate([{"$match": {"courseId": courseid}}, {"$limit": 1}, {"$project": {"coursename": 1, "numberOfQuestions": {"$size": "$questions"}}}])
            
            y = {}
            for x in cur:
                y.update(x)
            
            numberOfQuestions = y["numberOfQuestions"]
            print(numberOfQuestions)
            return render_template("instructorview.html", coursename  = escape(y["coursename"]), questionId = numberOfQuestions+1)
        elif auth in course["students"]:
            return render_template("studentview.html")
        else:
            return render_template("enroll.html", coursename = course["coursename"], courseId = courseid)
            
@app.route('/enroll', methods=["GET", "POST"])
def enroll():
    auth = funtions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        coursesCollection.update_one({"courseId": request.args["courseId"]}, {"$push": {"students": auth}})
        return redirect("/course?courseId=" + request.args["courseId"])
    
@socketio.on('message')
def handel_message(data):
    print(data)
    data = json.loads(data)
    course = data["courseId"]
    messageType = data["type"]
    del data["courseId"]
    del data["type"]
    for x in data.keys():
        data[x] = escape(data[x])
    if messageType == "question-create":
        coursesCollection.update_one({"courseId": course}, {"$push": {"questions": data}})
        send(data, room=course)
    
    
@socketio.on('join')
def join(data):
    join_room(data['room'])
    print("join room")

if __name__ == '__main__':
    socketio.run(app, debug = True, host='0.0.0.0', port = 8000, allow_unsafe_werkzeug=True)