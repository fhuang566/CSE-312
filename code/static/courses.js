// Renders a new courses to the page
function addCourse(course, category) {
    let courses = document.getElementById(category);
    courses.innerHTML += "<b><a href=\"course?courseId=" + course["courseId"] + "\">" + course["coursename"] +  "   " + "Instructor: " + course["instructor"] + "</a></b><br>";

}

// called when the page loads to get all courses
function get_allCourses() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const courses = JSON.parse(this.response);
            for (const course of courses) {
                addCourse(course, "allCourses");
            }
        }
    };
    request.open("GET", "/allCourses");
    request.send();
}

// called when the page loads to get all courses
function get_myCourses() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const courses = JSON.parse(this.response);
            for (const course of courses) {
                addCourse(course, "myCourses");
            }
        }
    };
    request.open("GET", "/myCourses");
    request.send();
}

function load() {
    get_allCourses();
    get_myCourses();
}