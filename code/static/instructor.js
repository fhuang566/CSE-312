const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const courseId = urlParams.get('courseId');


document.addEventListener('DOMContentLoaded', () => {
    // create websocket connection
    var socket = io.connect({query:{"token": document.getElementById("xsrf_token").value}});

    //upon connecting, join room, room name = courseid
    socket.on('connect', function() {
        socket.emit('join', {'room': courseId});
    });

    socket.on('message', data => {
        addQuestion(data);
        console.log(`Message received: ${data}`);
    });

    const forms = document.querySelectorAll('form');
    //catch form submition, extract form entries into json object
    forms.forEach(function (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const data = new FormData(form);
            const JSONdata = Object.fromEntries(data.entries());
            JSONdata["correct-answer"] = data.getAll("correct-answer");
            JSONdata["courseId"] = courseId;
            console.log(JSONdata);
            socket.emit('message', JSON.stringify(JSONdata));
            form.reset();
        });
    });

})

function addQuestion(data) {
    const choices = ['a', 'b', 'c', 'd', 'e'];
    var template = "<form><fieldset><div><input disabled id='quetionId' name='questionId' value=" + data["questionId"] + 
    " hidden><input disabled id='type' name='type' value='question-create' hidden><input diabled id='active' name='active' value='false' hidden><br><textarea disabled type='text' id='question' name='questions' cols='40' rows='10' placeholder=\'" + data["question"]+
    "\' required minlength='1'></textarea><br><label  for='choice-a'>Choice a: </label><input disabled type='text' id='choice-a' name='choice-a' size='50' placeholder=" + data["choice-a"] +
    " required minlength='1'><br><label  for='choice-b'>Choice b: </label><input disabled type='text' id='choice-b' name='choice-b' size='50' placeholder=" + data["choice-b"] + 
    " required minlength='1'><br><label  for='choice-c'>Choice c: </label><input disabled type='text' id='choice-c' name='choice-c' size='50' placeholder=" + data["choice-c"] +
    " required minlength='1'><br><label  for='choice-d'>Choice d: </label><input disabled type='text' id='choice-d' name='choice-d' size='50' placeholder=" + data["choice-d"] +
    " required minlength='1'><br><label  for='choice-e'>Choice e: </label><input disabled type='text' id='choice-e' name='choice-e' size='50' placeholder=" + data["choice-e"] +
    " required minlength='1'><p>Select the correct answer:</p>";
    for (const c of choices) {
        temp = "<input disabled id=" + c + " name='correct-answer' type='checkbox' value=\'" + c;
        if(data["correct-answer"].includes(c)){
           temp += "\' checked >" + c + "</input>";
        } 
        else{
            temp += "\'>" + c + "</input>";
        }
        template += temp;
    }

    template += "</div><div><button type='submit' value='start'>Start</button><button type='submit' value='stop'>Stop</button></div></fieldset></form>";
    // for (const entrie of Object.keys(data)) {
    document.getElementById('myQuestions').innerHTML += template;
    // data.forEach(function (entrie) {
    //     console.log(entrie);
    // });

}

function loadQuestions(){
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const questions = JSON.parse(this.response);
            for (const question of questions) {
                addQuestion(question);
            }
        }
    };
    request.open("GET", "/myQuestions?courseId=" + courseId);
    request.send();

}

function loadCourse(){
    loadQuestions();
}