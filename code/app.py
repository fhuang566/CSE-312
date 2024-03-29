import bcrypt
import pymongo
import secrets
import hashlib
import functions
import json
import random
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, flash, make_response, url_for
from flask_socketio import SocketIO, send, emit, join_room
from markupsafe import escape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

mongo_client = pymongo.MongoClient('mongo')
db = mongo_client["cse312"]
userCollection = db["users"]
contentCollection = db["content"]
auth_tokenCollection = db["auth_token"]
xsrf_tokenCollection = db["xsrf_token"]
coursesCollection = db['courses']
instructors = {}

@app.route('/')
def index():
    token = request.cookies.get("auth_token")
    if token:
        auth = functions.authenticate(token, auth_tokenCollection)
        if auth:
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
            expiredate = expire.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            auth_token = secrets.token_urlsafe(16)
            auth_tokenCollection.update_one({"username": username}, {"$set":{"username": username, "auth_token": hashlib.sha256(auth_token.encode()).digest()}}, upsert=True)
            response = make_response(redirect('/courses'))
            response.set_cookie("auth_token",  auth_token, path="/", expires=expiredate, httponly=True, secure=True)
            return response

    
    flash("Incorrect username or password. Try again!", "error")
    return redirect("/")

@app.route('/courses', methods=["GET", "POST"])
def courses():
    auth = functions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    print(auth)
    if auth:
    # if token:
    #     hashed = hashlib.sha256(token.encode())
    #     user = auth_tokenCollection.find_one({"auth_token": hashed.digest()})
    #     if user:
        return render_template('courses.html', username = escape(auth) )

    return "403	Forbidden", 403

@app.route('/allCourses')
def allCourses():
    auth = functions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
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
    auth = functions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
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
    auth = functions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        cur = coursesCollection.find_one({"courseId": request.args.get("courseId")})

        if cur:
            ret = cur['questions']
            if cur['instructor'] != auth:
                for x in ret:
                    del x['correct-answer']
            return json.dumps(ret)


@app.route('/createCourse', methods=["POST"])
def create():
    auth = functions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        coursename = request.form["coursename"]
        if len(coursename) == 0 and coursename.isspace():
            flash("Invalid input. Try again!", "error")
            return redirect("/courses")
        else:
            courseId = secrets.token_urlsafe(8)
            course = {"courseId": courseId, "coursename": coursename, "instructor": auth, "students": [], "questions": []}
            coursesCollection.insert_one(course)
            userCollection.update_one({'username': auth}, {"$set": {courseId:{}}}, upsert=True)
            return redirect("/course?courseId=" + courseId )
    return "403	Forbidden", 403
        

@app.route('/course')
def course():
    courseid = request.args.get("courseId")
    if not courseid:
        return redirect("/courses")
    auth = functions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    course = coursesCollection.find_one({"courseId": courseid})
    if auth and course:
        token = secrets.token_urlsafe(16)
        xsrf_tokenCollection.update_one({"username": auth}, {"$set":{"username": auth, "xsrf_token": token}}, upsert=True)
        if course["instructor"] == auth:
            cur = coursesCollection.aggregate([{"$match": {"courseId": courseid}}, {"$limit": 1}, {"$project": {"coursename": 1, "numberOfQuestions": {"$size": "$questions"}}}])
            
            y = {}
            for x in cur:
                y.update(x)
            
            # numberOfQuestions = y["numberOfQuestions"]
            # print(numberOfQuestions)
            return render_template("instructorview.html", coursename  = escape(y["coursename"]), xsrf_token = token)
        elif auth in course["students"]:
            return render_template("studentview.html", coursename  = escape(course["coursename"]), xsrf_token = token)
        else:
            return render_template("enroll.html", coursename = course["coursename"], courseId = courseid)
            
@app.route('/enroll', methods=["GET", "POST"])
def enroll():
    auth = functions.authenticate(request.cookies.get("auth_token"), auth_tokenCollection)
    if auth:
        coursesCollection.update_one({"courseId": request.args["courseId"]}, {"$push": {"students": auth}})
        userCollection.update_one({'username': auth}, {"$set": {request.args["courseId"]:{}}}, upsert=True)
        return redirect("/course?courseId=" + request.args["courseId"])
        


@socketio.on('connect')
def connect_handler():
    auth = functions.xsrf_auth(request.args.get("token"), xsrf_tokenCollection)
    if auth == False:
        raise ConnectionRefusedError("unauthorized")
        
    

@socketio.on('message')
def handel_message(data):
    print(data)
    data = json.loads(data)
    user = functions.xsrf_auth(data.get('xsrf_token'), xsrf_tokenCollection)
    if user == False:
        return None
    
    messageType = data["type"]
    course = data["courseId"]
    print(data)
    
    if messageType == "question-create":
        cur = coursesCollection.find_one({"instructor": user})
        if cur == None:
            return None
        del data["courseId"]
        del data["type"]
        if len(data["correct-answer"]) > 1:
            data["mutiple-ans"] = True
        else:
            data["mutiple-ans"] = False
        for x in data.keys():
            if x != "correct-answer":
                data[x] = escape(data[x])
        cur = coursesCollection.aggregate([{"$match": {"courseId": course}}, {"$limit": 1}, {"$project": {"coursename": 1, "numberOfQuestions": {"$size": "$questions"}}}])
            
        y = {}
        for x in cur:
            y.update(x)
            
        numberOfQuestions = y["numberOfQuestions"]
        data['questionId'] = str(numberOfQuestions+1)
        coursesCollection.update_one({"courseId": course}, {"$push": {"questions": data}})
        send(data, to=course+"ins")
        del data["correct-answer"]
        send(data, to=course)
    elif messageType == "st":
        if coursesCollection.find_one({'courseId': data['courseId']})['instructor'] != user:
            print('unauth')
            return None
        if data['st'] == 'Started':
            coursesCollection.update_one({"courseId": data["courseId"], "questions.questionId": data['id']}, {"$set":{"questions.$.active": "Started"}})
            
        elif data['st'] == 'Stopped':
            coursesCollection.update_one({"courseId": data["courseId"], "questions.questionId": data['id']}, {"$set":{"questions.$.active": "Stopped"}})
            score = userCollection.find_one({'username': user})
            # print(score)
            # grade=score[data["courseId"]].get(data["id"], 0)
            # ret = {"type": "score", "id": data["id"], "grade": grade}
            # print(ret)
            # send(ret, to=course)
        send(data, to=course+"ins")
        send(data, to=course)
    elif messageType == 'question-submit':
        print(data)
        cur = coursesCollection.find_one({'courseId': data["courseId"]}, {"_id":0, 'questions': {"$elemMatch": {'questionId': data['id']}}})
        if cur:
            print(cur)
            if cur['questions'][0]['active'] == "Started":
                correct_ans = cur['questions'][0]['correct-answer']
                numMatch = 0
                for x in data['ans']:
                    if x in correct_ans:
                        numMatch += 1
                grade = numMatch / len(correct_ans)
                print(data)
                print(grade)
                userCollection.update_one({'username': user}, {"$set": {data['courseId'] + "." + data["id"]: grade}}, upsert=True)
                # ret = {"type": "score", "id": data["id"], "grade": grade}
                # send(ret, to=course)
    elif messageType == 'score':
        score = userCollection.find_one({'username': user})
        print(score)
        grade=score[data["courseId"]].get(data["id"], 0)
        ret = {"type": "score", "id": data["id"], "grade": grade}
        print(ret)
        send(ret)
    elif messageType == 'stAll':
        if coursesCollection.find_one({'courseId': data['courseId']})['instructor'] != user:
            return None
        if data['st'] == 'Started':
            coursesCollection.update_many({"courseId": data["courseId"]}, {"$set":{"questions.$[].active": "Started"}})
            
        elif data['st'] == 'Stopped':
            coursesCollection.update_many({"courseId": data["courseId"]}, {"$set":{"questions.$[].active": "Stopped"}})
            # print(score)
            # grade=score[data["courseId"]].get(data["id"], 0)
            # ret = {"type": "score", "id": data["id"], "grade": grade}
            # print(ret)
            # send(ret, to=course)
        ret = {'type': 'stAll', 'st': data['st']}
        questions = coursesCollection.find_one({'courseId': data['courseId']})['questions']
        print(questions)
        idlist = []
        for x in questions:
            idlist.append(x['questionId'])
        print(idlist)
        ret['id'] = idlist
        send(ret, to=course+"ins")
        send(ret, to=course)


        
    
    
@socketio.on('join')
def join(data):
    cur = xsrf_tokenCollection.find_one({"xsrf_token": data["xsrf_token"]})
    course = coursesCollection.find_one({"courseId": data["courseId"]})
    if course["instructor"] == cur["username"]:
        join_room(data["courseId"] + "ins")
        print("join room")
    else:
        join_room(data["courseId"])

if __name__ == '__main__':
    socketio.run(app, debug = True, host='0.0.0.0', port = 8000)
    