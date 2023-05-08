# University Database Management System
<img src="https://i.imgur.com/kwWjdS6.jpeg" alt="CSULB" width="100%" height="500">

This project is a University Database Management System implemented using Python and MongoDB, designed to simulate an interactive user interface for adding, deleting, and listing records related to departments, courses, sections, students, and enrollments.

## Database Design

The database consists of the following collections:

1. **departments**: Stores information about each department, including an array of majors and a list of course numbers associated with the specific department.
2. **courses**: Stores information about each course separately.
3. **sections**: Stores information about each course section separately and includes a reference to the associated course number.
4. **students**: Stores information about each student, including an array called "StudentMajor" that acts as a junction table for the many-to-many association between majors and students.
5. **enrollments**: Acts as a junction table for the many-to-many association between students and sections. Stores the associated student and course, as well as either a "PassFail" application date or a "LetterGrade" (A, B, or C) to simulate the complete, disjoint constraint.

## Features

- Add, delete, and list records for departments, courses, sections, students, and enrollments.
- Interactive user interface for managing university data.
- Many-to-many associations between students and majors, as well as students and sections, using junction tables.
- Enforce complete, disjoint constraints for enrollment grading options (PassFail or LetterGrade).

## Getting Started

1. Clone the repository.
2. Install the required dependencies.
3. Run the main.py script to start the interactive user interface.
4. Follow the on-screen prompts to manage university data.


## Video Demonstration
Link: https://www.youtube.com/watch?v=DjgNDK6aW8Y
