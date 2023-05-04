import hashlib
import json



#authenticate auth_token, if token is valid return username else return false
def authenticate(token, collection):
    if token:
        hashed = hashlib.sha256(token.encode())
        user = collection.find_one({"auth_token": hashed.digest()})
        if user:
            return user["username"]
    return False

def xsrf_auth(token, collection):
    if token:
        user = collection.find_one({"xsrf_token": token})
        if user:
            return user["username"]
    return False

def question_create(courseId, xsrfdb, coursedb):
    return None

def startall(courseId, xsrfdb, coursedb):
    return None

def stopall(courseId, xsrfdb, coursedb):
    return None

def start(courseId, xsrfdb, coursedb, questionId):
    return None

def stop(courseId, xsrfdb, coursedb, questionId):
    return None

def ans_submit(courseId, xsrfdb, coursedb, questionId):
    return None

def message_handeler(data, xsrfdb, coursedb):
    json.load(data)
    type = data["type"]
    courseId = data["courseId"]
    match type:
        case "question-create":
            question_create(courseId, xsrfdb, coursedb)
        case "startall":
            startall(courseId, xsrfdb, coursedb)
        case "stopall":
            stopall(courseId, xsrfdb, coursedb)
        case "start":
            start(courseId, xsrfdb, coursedb, data["questionId"])
        case "stop":
            stop(courseId, xsrfdb, coursedb, data["questionId"])
        case "ans_submit":
            ans_submit(courseId, xsrfdb, coursedb, data["questionId"])

