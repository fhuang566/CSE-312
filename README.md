# CSE312 Project Team
 404 Not Found

 Happy Coding!
 
![](https://github.com/AlvinlolZ/CSE331-Project/blob/main/GIF/programming.gif)

TopHat 404
requirements:

User accounts
- [ ] Users can view all of the courses they created, and for each course that they enrolled in they can see their grades. Only the user themselves and the instructor of the course can view a user's grades

User Data - Courses
- [x] All users can create courses. When a user creates a course, they are the instructor for that course
- [x] All users can view every course that has been created along with their instructor and be given an option to enroll in each course
- [ ] The instructor of a course must be able to view the roster (users who enrolled) for each of their courses

WebSockets - Questions
- [ ] Instructors can create questions and assign those questions to the class. When a question is created, the instructor must provide enough information for the question to be automatically graded (eg. a multiple choice question with the correct answer provided by the instructor)
- [ ] Instructors must have a way to start and stop a question. Answers will only be accepted while the question is active. The start and stop messages must be sent via WebSockets
- [ ] When a question is active, each user who is enrolled in the course can provide their answer for the question. These answers must be sent via WebSockets. If the question is stopped, users must be able to immediately see that the question was stopped (Via WebSockets).
- [ ] Any answers submitted after the question is stopped do not count
- [ ] When the question is stopped, the answers are graded. Each student can view their grades for each question and the instructor of the course can view all the grades in a gradebook
- [ ] Grading must be automated
- [ ] Multiple courses must be able to have questions simultaneously, though a single course can be limited to one question at a time
