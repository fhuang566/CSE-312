const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const courseId = urlParams.get('courseId');
var ret = Object();


document.addEventListener('DOMContentLoaded', () => {
    // create websocket connection
    var socket = io.connect({query:{"token": document.getElementById("xsrf_token").value}});

    //upon connecting, join room, room name = courseid
    socket.on('connect', function() {
        socket.emit('join', {'room': courseId});
    });

    socket.on('message', data => {
        console.log(`Message received: ${data}`);
        if(data["type"] == "question-st"){
            questionST(data);
        }
        else{
            addQuestion(data);
        }
        
        
    });

    const forms = document.querySelectorAll('form');
    //catch form submition, extract form entries into json object
    forms.forEach(function (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const data = new FormData(form);
            const JSONdata = Object.fromEntries(data.entries());
            if (JSONdata["type"] == "question-create"){
                JSONdata["correct-answer"] = data.getAll("correct-answer");
            }
            else{
                JSONdata["ans"] = data.getAll("ans");
            }

            JSONdata["courseId"] = courseId;
            console.log(JSONdata);
            socket.emit('message', JSON.stringify(JSONdata));
            form.reset();
        });
    });

})

function addQuestion(data) {
    const choices = ['a', 'b', 'c', 'd', 'e'];
    var template = "<form><fieldset id="+ data["questionId"] +" disabled><div><input id='quetionId' name='questionId' value="+ data["questionId"] +  
    " hidden><input id='type' name='type' value='question-submit' hidden><br><b type='text' id='question' name='questions'>"+ data["question"] +
    "</b><br><input id='a' name='ans' type='checkbox' value='a'>a: "+ data["choice-a"] + 
    "</input><br><input id='b' name='ans' type='checkbox' value='b'>b: "+ data["choice-b"] + 
    "</input><br><input id='c' name='ans' type='checkbox' value='c'>c: "+ data["choice-c"] + 
    "</input><br><input id='d' name='ans' type='checkbox' value='d'>d: "+ data["choice-d"] +
    "</input><br><input id='e' name='ans' type='checkbox' value='e'>e: "+ data["choice-b"];
    

    
    if (data["mutiple-ans"] == "False"){
        template = template.replaceAll("checkbox", "radio");
    }

    if (data['correct-answer'] != undefined){
        for(let i = 0; i < data['correct-answer'].length; i++){
            x = data['correct-answer'][i];
            template = template.replace("value=\'" + x + "\'", "value=\'" + x + "\' checked");

        }
        template += '</input></fieldset></form><div><button type="submit" name="start" value="start">Start</button><button type="submit" name="stop" value="stop">Stop</button></div>';
    }
    else{
        template += "</input></div><div><button type='submit'>Submit</button></div></fieldset></form>";
    }
    document.getElementById('myQuestions').innerHTML += template

}

function questionST(data) {
    document.getElementById(data["questionId"]).disabled  = data["option"];
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