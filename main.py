import certifi as certifi
import pymongo
from pymongo import MongoClient
import connect_string
from pprint import pprint
from menu_definitions import menu_main
from menu_definitions import add_menu
from menu_definitions import delete_menu
from menu_definitions import list_menu
from datetime import datetime, time
from datetime import date
import random
from bson import ObjectId
from pymongo.errors import DuplicateKeyError


def add(db):
    """
    Present the add menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    add_action: str = ''
    while add_action != add_menu.last_action():
        add_action = add_menu.menu_prompt()
        exec(add_action)


def delete(db):
    """
    Present the delete menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    delete_action: str = ''
    while delete_action != delete_menu.last_action():
        delete_action = delete_menu.menu_prompt()
        exec(delete_action)


def list_objects(db):
    """
    Present the list menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    list_action: str = ''
    while list_action != list_menu.last_action():
        list_action = list_menu.menu_prompt()
        exec(list_action)


def count_departments(db):
    '''
    Check the document for any department objects present
    param db:   The connection to the current database
    return:     0 if there are no departments, 1 otherwise
    '''
    collection = db["departments"]
    if collection.count_documents({}) == 0:
        print("There are currently no departments.")
        return 0
    return 1


def count_courses(db):
    '''
    Check the document for any course objects present
    param db:   The connection to the current database
    return:     0 if there are no departments, 1 otherwise
    '''
    collection = db["courses"]
    if collection.count_documents({}) == 0:
        print("There are currently no courses.")
        return 0
    return 1


def count_sections(db):
    '''
    Check the document for any course objects present
    param db:   The connection to the current database
    return:     0 if there are no departments, 1 otherwise
    '''
    collection = db["sections"]
    if collection.count_documents({}) == 0:
        print("There are currently no sections.")
        return 0
    return 1


def count_students(db):
    '''
    Check the document for any student objects present
    param db:   The connection to the current database
    return:     0 if there are no students, 1 otherwise
    '''
    collection = db["students"]
    if collection.count_documents({}) == 0:
        print("There are currently no students.")
        return 0
    return 1


def count_enrollments(db):
    '''
    Check the document for any enrollment objects present
    param db:   The connection to the current database
    return:     0 if there are no enrollments, 1 otherwise
    '''
    collection = db["enrollments"]
    if collection.count_documents({}) == 0:
        print("There are currently no enrollments.")
        return 0
    return 1


def count_majors(db):
    '''
    Check the document for any major objects present
    param db:   The connection to the current database
    return:     0 if there are no majors, 1 otherwise
    '''
    collection = db["majors"]
    if collection.count_documents({}) == 0:
        print("There are currently no majors.")
        return 0
    return 1


def count_student_major(db):
    '''
    Check the document for any student_major objects present
    param db:   The connection to the current database
    return:     0 if there are no student_major, 1 otherwise
    '''
    collection = db["student_major"]
    if collection.count_documents({}) == 0:
        print("There are currently no student_major records.")
        return 0
    return 1


def validate_department(department_document):
    try:
        # Validate name
        if not isinstance(department_document['name'], str) or len(department_document['name']) > 50:
            return False, "A name must be unique, 10-50 letters long"

        # Validate abbreviation
        if not isinstance(department_document['abbreviation'], str) or len(department_document['abbreviation']) > 6:
            return False, "An abbreviation must be unique, no more than 6 letters long"

        # Validate chair name
        if not isinstance(department_document['chair name'], str) or len(department_document['chair name']) > 80:
            return False, "A chair name must be unique, no more than 80 letters long"

        # Validate building
        valid_buildings = ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC']
        if department_document['building'] not in valid_buildings:
            shorten_len = "'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', or 'VEC'"
            return False, "A building can only be: 'ANAC', 'CDC', 'DC', 'ECS','EN2'," + shorten_len

        # Validate office
        if not isinstance(department_document['office'], int):
            return False, 'A building-office combination must be unique'

        # Validate description
        if not isinstance(department_document['description'], str) or len(department_document['description']) > 80:
            return False, 'A description must be 10-80 letters long'

        return True, ''
    except Exception as e:
        print()
        print("Department violated constraints:")
        print("\tA name must be unique, 10-50 letters long")
        print("\tAn abbreviation must be unique, no more than 6 letters long")
        print("\tA chair name must be unique, no more than 80 letters long")
        print("\tA building can only be: 'ANAC', 'CDC', 'DC', 'ECS', 'EN2', "
              "'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', or 'VEC'")
        print("\tA building-office combination must be unique")
        print("\tA description must be 10-80 letters long")
        pprint(e)
        print()
        add_department(department_document)


def add_department(db):
    departments = db["departments"]

    # Prompt the user for department details
    name = input("Enter the department name: ")
    abbreviation = input("Enter the department abbreviation: ")
    chair_name = input("Enter the chair name: ")
    building = input("Enter the building (ANAC, CDC, DC, ECS, EN2, EN3, EN4, EN5, ET, HSCI, NUR, VEC): ")
    office = int(input("Enter the office number: "))
    description = input("Enter the department description: ")

    department_document = {
        "name": name,
        "abbreviation": abbreviation,
        "chair name": chair_name,
        "building": building,
        "office": office,
        "description": description,
        "courses": [],
        "majors": []
    }

    # Check if the department exists
    existing_department = departments.find_one({"abbreviation": abbreviation})
    if existing_department:
        print(f"Department with abbreviation {abbreviation} already exists.")
        return

    # Validate the department document
    is_valid, error_message = validate_department(department_document)
    if not is_valid:
        print("Validation error:", error_message)
        return

    # Insert the department document into the departments collection
    try:
        result = departments.insert_one(department_document)
        print(f"Added department {name} with abbreviation {abbreviation}")
    except Exception as e:
        print("Error adding department:")
        print(e)


def add_course(db):
    courses = db["courses"]
    departments = db["departments"]

    # Prompt the user for course details
    course_number = int(input("Enter course number: "))
    name = input("Enter course name: ")
    description = input("Enter course Description: ")
    units = int(input("Enter course units: "))
    department_abbr = input("Enter Department Abbreviation: ")

    # Check if the department exists
    department = departments.find_one({"abbreviation": department_abbr})
    if department is None:
        print(f"No department found with abbreviation {department_abbr}")
        return

    if not validate_courses(course_number, description, units):
        return

    # Create course document
    course_document = {
        "courseNumber": course_number,
        "name": name,
        "description": description,
        "units": units,
        "department": department["_id"]
    }

    # Insert course document into courses collection
    try:
        courses.insert_one(course_document)
        print(f"Added course {course_number} to department {department_abbr}")
    except pymongo.errors.DuplicateKeyError as e:
        print("Course already exists")
        pprint(e)
        return

    # Add course to department courses array
    courses_array = department.get("courses", [])
    if isinstance(course_number, int):
        courses_array.append(course_number)
        departments.update_one({"_id": department["_id"]}, {"$set": {"courses": courses_array}})
    else:
        print("Invalid course number, must be an integer.")


def validate_courses(course_number, description, units):
    # Check course number constraint
    if course_number < 100 or course_number > 700:
        print("Course number must be between 100 and 700")
        return False

    # Check description length constraint
    if len(description) > 80:
        print("Description must not exceed 80 characters")
        return False

    # Check units constraint
    if units < 1 or units >= 5:
        print("Units must be between 1 and 5")
        return False

    return True


def add_section(db):
    # Selecting departments and sections since we want to check for courses inside departments' table
    sections = db["sections"]
    valid_buildings = ('ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC')

    while True:
        # Getting the information from the user
        course_number = int(input("Enter the course number: "))
        section_number = int(input("Enter the section number: "))
        semester = input("Enter the semester (e.g., 'Spring'): ")
        section_year = int(input("Enter the section year (e.g., 2022): "))
        building = input("Enter the building: ")
        room = int(input("Enter the room number: "))
        schedule = input("Enter the schedule (e.g., 'MW'): ")
        start_time = input("Enter the start time (eg. '8:00am'): ")
        instructor = input("Enter the instructor's name: ")

        # Checking constraints
        if not validate_sections(schedule, semester, room, building, start_time):
            return
        valid_schedule = schedule in ('MW', 'TuTh', 'MWF', 'F', 'S')
        valid_semester = semester in ('Fall', 'Spring', 'Summer I', 'Summer II', 'Summer III', 'Winter')
        valid_room = 0 < room < 1000
        valid_building = building in valid_buildings
        valid_start_time = ('AM' in start_time.upper() and 8 <= int(
            start_time.split(':')[0]) <= 11 or 'PM' in start_time.upper() and 1 <= int(
            start_time.split(':')[0]) <= 7) or ('PM' in start_time.upper() and int(start_time.split(':')[0]) == 12) or (
                                   int(start_time.split(':')[0]) == 7 and start_time.split(':')[1] == '30')

        if valid_schedule and valid_semester and valid_room and valid_building and valid_start_time:
            # Searching course in the course collection
            course = courses.find_one({"courseNumber": course_number})

            if course:
                # If the course number exists then insert section table
                new_section = {
                    "section number": section_number,
                    "semester": semester,
                    "section year": section_year,
                    "building": building,
                    "room": room,
                    "schedule": schedule,
                    "startTime": start_time,
                    "instructor": instructor,
                    "course": course_number
                }

                try:
                    sections.insert_one(new_section)
                    print(f"section was added to course number: {course_number}")
                    break
                except DuplicateKeyError:
                    print("Duplicate section found. Section not added.")
            else:
                print("Course not found. Please add the course first.")
        else:
            print("Invalid input. Please check the constraints.")
            print()
            print("""
            Constrints for Section:
            i.	schedule is IN ('MW', 'TuTh', 'MWF', 'F', 'S')
            ii.	semester is IN ('Fall', 'Spring', 'Summer I', 'Summer II', 'Summer III', 'Winter')
            iii.	room > 0 and room < 1000 (assume no ten story buildings on campus)
            iv.	building is IN – the same list as the one for the department office.
            v.	startTime >= 8:00 AM and <= 7:30 PM.
            """)


def validate_sections(schedule, semester, room, building, start_time):
    valid_schedule = schedule in ('MW', 'TuTh', 'MWF', 'F', 'S')
    if not valid_schedule:
        print("Invalid schedule. Valid schedules are: MW, TuTh, MWF, F, S")
        return False

    valid_semester = semester in ('Fall', 'Spring', 'Summer I', 'Summer II', 'Summer III', 'Winter')
    if not valid_semester:
        print("Invalid semester. Valid semesters are: Fall, Spring, Summer I, Summer II, Summer III, Winter")
        return False

    if room < 1 or room > 1000:
        print("Invalid room number. Room number must be between 1 and 1000")
        return False

    valid_buildings = ('ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC')
    if building not in valid_buildings:
        print("Invalid building. Valid buildings are:", valid_buildings)
        return False
    valid_start_time = ('AM' in start_time.upper() and 8 <= int(
        start_time.split(':')[0]) <= 11 or 'PM' in start_time.upper() and 1 <= int(start_time.split(':')[0]) <= 7) or (
                               'PM' in start_time.upper() and int(start_time.split(':')[0]) == 12) or (
                               int(start_time.split(':')[0]) == 7 and start_time.split(':')[1] == '30')

    return True


def quick_add_department(db):
    collection = db["departments"]
    names = ["Engineering", "Liberal Arts", "Business", "Education", "Science", "Social Sciences"]
    abbreviations = ["CECS", "LAS", "BUS", "EDU", "SCI", "SSC"]
    descriptions = ["This department offers programs in engineering and technology.",
                    "This department offers programs in humanities and social sciences.",
                    "This department offers programs in business and management.",
                    "This department offers programs in teaching and education.",
                    "This department offers programs in natural sciences.",
                    "This department offers programs in social sciences."]
    index = random.randint(0, len(names) - 1)
    department = {
        "name": names[index],
        "abbreviation": abbreviations[index],
        "chair name": "John Doe",
        "building": random.choice(['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC']),
        "office": 101,
        "description": descriptions[index],
        "courses": []
    }
    try:
        results = collection.insert_one(department)
        print(f"Added department: {department}")
    except Exception as e:
        print(f"Error adding department: {e}")


def add_student(db):
    # We only add the student without the need to reference a major since the add_student_major will add the major to the student
    students = db["students"]
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")

    student = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        # In this array we will store objects with attribute "major_name" and "declaration_date"
        "StudentMajor": []
    }
    try:
        students.insert_one(student)
        print(f"Added student {first_name} {last_name}")
    except Exception as e:
        print("Failed to add student")
        print(e)


def validate_student_major(declaration_date):
    if declaration_date > datetime.today():
        print("Invalid declaration date. Declaration date can not be in the future.")
        return False
    return True


def add_student_major(db):
    # Here we are essentially adding the major to the student
    # Therefore, we need to select both "students" and "majors" table
    students = db["students"]
    majors = db["departments"]

    # The professor want us to use a system where the user cant give the students id and instead the name of the student
    # In this case we are going to ask only for the first name of the student that the user is changing

    student_first_name = input("Enter student first name: ")

    # Now we are going to list all students found with the provided first name from the user
    studentsFound = list(students.find({"first_name": student_first_name}))

    if studentsFound:
        # If we found students with that firs name provided then...
        print("Select the correct student:")

        # Loop through all found students with first name and showing to the user
        for idx, student in enumerate(studentsFound, start=1):
            print(
                f"Index Number: {idx} | student: {student['first_name']} {student['last_name']} | email: {student['email']}")

        # Get the users selection of the correct student
        student_selection = int(
            input("Enter the corresponding 'Index Number' of the student that you want to select: "))

        # Now we are going to adjust the selected index by substracting 1 to account for the python's 0-based indexing
        student_selection -= 1

        # Now we are retrieving the right student from the list that we used the adjusted index
        selected_student = studentsFound[student_selection]

        # Now that we finally got the correct student, then we can ask for the major to be added to this student
        major_name = input("What Major you want to add to the selected student?(Enter Major name): ")
        declaration_date_user = input("enter the declaration date (yyyy-mm-dd): ")

        # Check if the date was correctly formatted
        try:
            declaration_date_user = datetime.strptime(declaration_date_user, "%Y-%m-%d")

        except ValueError:
            print("Invalid date format. Major to Student not added")

        if not validate_student_major(declaration_date_user):
            return

        # Finding if the major that is going to be added to the student exists
        major = majors.find_one({"majors.name": major_name})

        if major:
            # Initialize an empty list to store majors of the student that match the major given by the user
            student_majors = []

            # Looping through each array "StudentMajor" attribute from the student that we selected
            # We are tryihng to find if the student already has this major already added
            for student_major in selected_student["StudentMajor"]:
                # checking if the major name given matches with any existing major that the student already has
                if student_major["major_name"] == major_name:
                    # If the student already has the major, then we are adding it into the list so we can later tell the user that this student already declared in this major
                    student_majors.append(student_major)

            if not student_majors:
                # if the array is empty(the user havent enrolled to the major yet) then we will add it to the student
                student_major = {
                    "major_name": major_name,
                    "declaration_date": declaration_date_user
                }
                try:
                    # Adding the major to the student using id of the student
                    students.update_one({"_id": selected_student["_id"]}, {"$push": {"StudentMajor": student_major}})
                    print(
                        f"Added major: name={major_name} to student with first and last name as {selected_student['first_name']} {selected_student['last_name']} with email {selected_student['email']} ")
                except Exception as e:
                    print("Failed adding Major to Student")
                    print(e)
            else:
                # if the array contains the major that we trying to add then..
                print(
                    f"Student {selected_student['first_name']} {selected_student['last_name']} already declared the major named '{major_name}'")
        else:
            print(f"Major with name {major_name} does not exist, sorry")
    else:
        print(f"No student with first name {student_first_name} was found, sorry")


def add_major(db):
    # Adding Major to Department table so that then it can be referenced to student
    departments = db["departments"]

    # asking user which department we want the major to be
    department_abreviation = input("Enter department abreviation: ")

    # Check if department given by user exists so we can add the major
    department = departments.find_one({"abbreviation": department_abreviation})

    if department:
        # if the department given by the user is found on the department's table then...
        major_name = input("Enter Major name: ")
        description = input("Enter Major description: ")

        # checking that the major is unique by searching if there is a major with the name given by the user
        existing_major = [major for major in department["majors"] if major["name"] == major_name]

        if not existing_major:
            # If this major is indeed unique inside departments array of majors then we can add the major
            major = {
                "name": major_name,
                "description": description
            }

            try:
                # then we go inside departments table(specificallly to the department abbreviation procvided by the user)
                # after finding the department provided by the user, to the majors array of that department
                # we add the major that the user gave data about
                departments.update_one({"abbreviation": department_abreviation}, {"$push": {"majors": major}})
                print(
                    f"We succesfully added the Major named  {major_name} into the department abreviation {department_abreviation}!")
                # Add uniqueness constraint for the "name" field inside the "majors" array
                departments.update_one({"abbreviation": department_abreviation, "majors.name": major_name},
                                       {"$set": {"majors.$.name": major_name}}, upsert=True)
            except Exception as e:
                print(
                    f"Failed to add Major with major name {major_name} into the department with abbreviation of {department_abreviation}")
                pprint(e)
        else:
            print(f"Major with name {major_name} already exists, sorry add another major")
    else:
        print(
            f"Department with abreviation name {department_abreviation} was not found, use another department abreviation")


def add_enrollment(db):
    from datetime import datetime
    # In order to add an enrollment we would need the students and enrollments table
    students = db["students"]
    enrollments = db["enrollments"]

    # Adding enrollment by student name
    student_first_name = input("Enter student first name: ")

    # Find the students with the student first name given
    matched_students = list(students.find({"first_name": student_first_name}))

    if matched_students:
        # if we found student with that first name then..
        print("Select the correct student:")

        # Loop through all found students with first name and showing to the user
        for idx, student in enumerate(matched_students, start=1):
            print(
                f"Index Number: {idx} | student: {student['first_name']} {student['last_name']} | email: {student['email']}")

        # Get the user's selection of the correct student
        student_selection = int(
            input("Enter the corresponding 'Index Number' of the student that you want to select: "))

        # Now we are going to adjust the selected index by subtracting 1 to account for the python's 0-based indexing
        student_selection -= 1

        # Now we are retrieving the right student from the list that we used the adjusted index
        selected_student = matched_students[student_selection]

        # Ask user for identifying information about the course being enrolled in
        semester = input("Enter the semester (e.g., 'Spring'): ")
        section_year = int(input("Enter the section year (e.g., 2022): "))
        department_abbreviation = input("Enter the department's abbreviation: ")
        course_number = int(input("Enter the course number: "))
        section_number = input("Enter the section number: ")

        # Check if the enrollment already exists
        existing_enrollment = enrollments.find_one({
            "semester": semester,
            "section_year": section_year,
            "department_abbreviation": department_abbreviation,
            "course_number": course_number,
            "section_number": section_number,
            "studentID": selected_student["_id"]
        })

        if existing_enrollment:
            print("This enrollment already exists.")
            return

        # Check if student is already enrolled in another section of the same course during the same semester
        existing_enrollment = enrollments.find_one({
            "semester": semester,
            "course_number": course_number,
            "section_number": {"$ne": section_number},
            "studentID": selected_student["_id"]
        })

        if existing_enrollment:
            print(
                f"This student is already enrolled in section {existing_enrollment['section_year']}, section {existing_enrollment['section_number']} of course {existing_enrollment['course_number']} during {existing_enrollment['semester']}.")
            return

        # Check if the student is already enrolled in the same course in the same section during the same semester
        existing_enrollment = enrollments.find_one({
            "semester": semester,
            "section_year": section_year,
            "section_number": section_number,
            "department_abbreviation": department_abbreviation,
            "course_number": course_number,
            "studentID": selected_student["_id"]
        })

        if existing_enrollment:
            print(
                f"This student is already enrolled in section {existing_enrollment['section_year']}, section {existing_enrollment['section_number']} of course {existing_enrollment['course_number']} during {existing_enrollment['semester']}.")
            return

        # Check for Pass/Fail or letter grade and validate acordingly
        verified_date = input("If the course was a Pass/Fail please enter the date\n"
                              "If it was a Letter Grade course hit enter for next prompt(yyyy-mm-dd): ")

        # If the User does an enter for verified time, then it will be for Letter Grade
        pass_fail = input("Enter Letter Grade. eg 'A','B','C' (Only enter if you didnt input date): ")

        if verified_date:
            # Check if the date was correctly formatted
            try:
                verified_date = datetime.strptime(verified_date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Enrollment not added")
                return

        if pass_fail:
            while pass_fail not in ["A", "B", "C"]:
                pass_fail = input("Enter Letter Grade. eg 'A','B','C' (Only enter if you didnt input date): ")

        # Inserting the enrollment into the database
        enrollment = {
            "studentID": selected_student["_id"],
            "semester": semester,
            "section_year": section_year,
            "department_abbreviation": department_abbreviation,
            "course_number": course_number,
            "section_number": section_number,
            "pass_fail": pass_fail.lower(),
            "verified_date": verified_date
        }

        try:
            enrollment_result = enrollments.insert_one(enrollment)
            print(f"Enrollment added with ID: {enrollment_result.inserted_id}")

        except Exception as e:
            print("Error Adding Enrollments")
            print(e)

    else:
        print(f"There is no student with first name: {student_first_name}")


def delete_enrollment(db):
    students = db["students"]
    enrollments_collection = db["enrollments"]

    student_first_name = input("Enter student first name: ")

    matched_students = list(students.find({"first_name": student_first_name}))

    if matched_students:
        print("Select the correct student:")

        for idx, student in enumerate(matched_students, start=1):
            print(
                f"Index Number: {idx} | student: {student['first_name']} {student['last_name']} | email: {student['email']}")

        student_selection = int(
            input("Enter the corresponding 'Index Number' of the student that you want to select: ")) - 1

        selected_student = matched_students[student_selection]

        student_enrollments = list(enrollments_collection.find({"studentID": selected_student["_id"]}))

        if not student_enrollments:
            print("Student " + selected_student['first_name'] + " has no enrollments.")
            return

        print("Enrollments for student: " + selected_student['first_name'] + " " + selected_student['last_name'])
        for i, enrollment in enumerate(student_enrollments):
            print(
                f"{i + 1}. Semester: {enrollment['semester']}, Year: {enrollment['section_year']}, Department: {enrollment['department_abbreviation']}, Course Number: {enrollment['course_number']}")

        enrollment_choice = int(input("Enter the number of the enrollment you want to delete: ")) - 1

        if enrollment_choice < 0 or enrollment_choice >= len(student_enrollments):
            print("Invalid enrollment number.")
            return

        deleted_enrollment = student_enrollments[enrollment_choice]
        enrollments_collection.delete_one({"_id": deleted_enrollment["_id"]})
        print("Enrollment deleted successfully.")
    else:
        print(f"No student with first name {student_first_name} was found, sorry.")



def delete_major(db):
    departments = db["departments"]
    department_abreviation = input("Enter department abreviation: ")

    # check if department exists
    department = departments.find_one({"abbreviation": department_abreviation})

    if department:
        major_name = input("Enter major name: ")

        # check if major to be deleted exists
        # Iterating through all departments inside the departments collection and going specifically to the array of majors
        # and find the major with the major name given by the user
        existing_major = [major for major in department["majors"] if major["name"] == major_name]

        if existing_major:
            # if major in the array of a the department exists, then we can delete it
            try:
                departments.update_one({"abbreviation": department_abreviation},
                                       {"$pull": {"majors": {"name": major_name}}})
                print(f"We just deleted the major: {major_name}.")

            except Exception as e:
                print(f"Failed deleting major named {major_name}")
                pprint(e)
        else:
            print(
                f"Major with major name {major_name} was not found in department with abreviation {department_abreviation}, sorry")
    else:
        print(f"Department abreviation with name '{department_abreviation}' was not found, sorry")


def delete_student_majors(db):
    students = db["students"]

    # We are going to use the first name to find the major that is going to be deleted from the student
    student_first_name = input("Enter student first name: ")

    # Displaying all students with the fisrt name provided
    matched_students = list(students.find({"first_name": student_first_name}))

    if matched_students:
        print("Select the correct student:")

        # Loop through all found students with first name and showing to the user
        for idx, student in enumerate(matched_students, start=1):
            print(
                f"Index Number: {idx} | student: {student['first_name']} {student['first_name']} | email: {student['email']}")

        # Get the users selection of the correct student
        student_selection = int(
            input("Enter the corresponding 'Index Number' of the student that you want to select: "))

        # Now we are going to adjust the selected index by substracting 1 to account for the python's 0-based indexing
        student_selection -= 1

        # Now we are retrieving the right student from the list that we used the adjusted index
        selected_student = matched_students[student_selection]

        # Asking for the major name to be deleted from the student selected
        major_name = input("What is the major name to be deleted from the selected student? ")

        # Check if the major exists inside the student
        student_majors = []
        for student_major in selected_student["StudentMajor"]:
            if student_major["major_name"] == major_name:
                student_majors.append(student_major)

        if student_majors:
            try:
                # if there is a mjor with that name inside the student, then we can delete it
                students.update_one({"_id": selected_student["_id"]},
                                    {"$pull": {"StudentMajor": {"major_name": major_name}}})
                print(
                    f"You just removed the Major named '{major_name}' from the student '{selected_student['first_name']} {selected_student['last_name']}' with email {selected_student['email']}")

            except Exception as e:
                print("Failed to remove majors inside the student")
                print(e)
        else:
            print(
                f"Student '{selected_student['first_name']} {selected_student['last_name']}' has not declared to major named '{major_name}'")
    else:
        print(f"No student with first name {student_first_name} was foubnd, sorry")


def select_department(db):
    if count_departments(db) == 0:
        return
    collection = db["departments"]
    found: bool = False
    abbreviation: str = ''
    while not found:
        abbreviation = input("Enter department abbreviation: ")
        abrv_count: int = collection.count_documents({"abbreviation": abbreviation})
        found = abrv_count == 1
        if not found:
            print("No department found by that abbreviation. Try again.")
    found_department = collection.find_one({"abbreviation": abbreviation})
    return found_department


def select_course(db):
    if count_courses(db) == 0:
        return
    collection = db["courses"]
    found: bool = False
    course_number: int = 0
    while not found:
        course_number = int(input("Enter course number: "))
        course_count: int = collection.count_documents({"course number": course_number})
        found = course_count == 1
        if not found:
            print("No course found with that course number. Try again.")
    found_course = collection.find_one({"course number": course_number})
    return found_course


def select_major(db):
    if count_majors(db) == 0:
        return
    collection = db["majors"]
    found: bool = False
    while not found:
        major_name = input("Enter major name: ")
        major_count = collection.count_documents({"name": major_name})
        found = major_count == 1
        if not found:
            print("No major found by that name. Try again.")
    found_major = collection.find_one({"name": major_name})
    return found_major


def select_student(db):
    students = db["students"]

    while True:
        student_id = input("Enter student ID: ")
        try:
            student = students.find_one({"_id": ObjectId(student_id)})
            if student:
                return student
            else:
                print("No student found by that ID. Try again.")
        except Exception as e:
            print("Invalid ID format. Try again.")
            pprint(e)


def list_department(db):
    if count_departments(db) == 0:
        return
    departments = db["departments"].find({}).sort([("abbreviation", pymongo.ASCENDING)])
    for department in departments:
        pprint(department)


def list_course(db):
    if count_courses(db) == 0:
        return
    courses = db["courses"].find({}).sort([("course_number", pymongo.ASCENDING)])
    for course in courses:
        pprint(course)


def list_section(db):
    if count_sections(db) == 0:
        return
    sections = db["sections"].find({}).sort([("section_number", pymongo.ASCENDING)])
    for section in sections:
        pprint(section)


def list_student(db):
    if count_students(db) == 0:
        return
    students = db["students"].find({}).sort([("last name", pymongo.ASCENDING), ("first name", pymongo.ASCENDING)])
    for student in students:
        pprint(student)


def list_major(db):
    # List all departments
    departments = list(db["departments"].find({}).sort([("name", pymongo.ASCENDING)]))

    # If no departments found, print a message and return
    if not departments:
        print("No departments found.")
        return

    # Print the list of departments
    print("List of Departments:")
    for department in departments:
        print(department["name"])

    # Ask the user to select a department
    selected_department = input("Enter the name of the department you'd like to see the majors for: ")

    # Find the selected department in the database
    department = db["departments"].find_one({"name": selected_department})

    # If the department is not found, print a message and return
    if not department:
        print("Department not found.")
        return

    # If the department has no majors, print a message and return
    if not department.get("majors"):
        print("No majors found for the selected department.")
        return

    # Print the majors associated with the selected department
    print(f"Majors for the {selected_department} department:")
    for major in department["majors"]:
        pprint(major)


def list_enrollments(db):
    if count_enrollments(db) == 0:
        return
    enrollments = db["enrollments"].find({}).sort([
        ("semester", pymongo.ASCENDING),
        ("section_year", pymongo.ASCENDING),
        ("department_abbreviation", pymongo.ASCENDING),
        ("course_number", pymongo.ASCENDING)
    ])
    for enrollment in enrollments:
        student = db["students"].find_one({"enrollment_id": enrollment["_id"]})


        pprint({
            "semester": enrollment["semester"],
            "year": enrollment["section_year"],
            "department": enrollment["department_abbreviation"],
            "course": enrollment["course_number"],
            # "student_name": student['first_name'] + " " + ['last_name'],
        })


def delete_department(db):
    department = select_department(db)
    if department is None:
        print("Department does not exist")
        return
    departments = db["departments"]
    deleted = departments.delete_one({"_id": department["_id"]})

    # Delete associated majors
    majors = department["majors"]
    major_names = [major["name"] for major in majors]

    # Update students by removing the major that belongs to the deleted department
    students = db["students"]
    students.update_many(
        {"StudentMajor.major_name": {"$in": major_names}},
        {"$pull": {"StudentMajor": {"major_name": {"$in": major_names}}}}
    )

    # Find associated courses
    courses = db["courses"]
    associated_courses = courses.find({"courseNumber": {"$in": department["courses"]}})

    # For each associated course, delete the sections associated with the course
    # and then delete the course itself
    sections = db["sections"]
    for course in associated_courses:
        sections.delete_many({"course": course["courseNumber"]})
        courses.delete_one({"_id": course["_id"]})

    print(f"We just deleted: {deleted.deleted_count} departments.")
    return deleted.deleted_count


def delete_course(db):
    courses = db["courses"]
    departments = db["departments"]
    sections = db["sections"]

    # Prompt the user for department abbreviation and course number
    department_abbr = input("Enter Department Abbreviation: ")
    course_number = int(input("Enter course number: "))

    # Check if the department exists
    department = departments.find_one({"abbreviation": department_abbr})
    if department is None:
        print(f"No department found with abbreviation {department_abbr}")
        return

    # Check if the course exists
    course = courses.find_one({"courseNumber": course_number, "department": department["_id"]})
    if course is None:
        print(f"No course found with course number {course_number} in department {department_abbr}")
        return

    # Delete the course from courses collection
    courses.delete_one({"_id": course["_id"]})
    print(f"Deleted course {course_number} from department {department_abbr}")

    # Remove the course number from the department's courses array
    courses_array = department.get("courses", [])
    if course_number in courses_array:
        courses_array.remove(course_number)
        departments.update_one({"_id": department["_id"]}, {"$set": {"courses": courses_array}})
    else:
        print("Course number not found in department's courses array.")

    # Find all sections with the deleted course number and delete them
    sections_to_delete = sections.find({"course": course_number})
    sections.delete_many({"course": course_number})
    print(f"Deleted {db.sections.count_documents({'course': course_number})} sections with course number {course_number}")




def delete_section(db):
    # To delete the section we must select first both tables "sections" and "courses"
    sections = db["sections"]
    courses = db["courses"]

    # Prompt the user to get the section and course information
    section_number = int(input("Enter section number to delete: "))
    course_number = int(input("Enter course number: "))
    department_abbr = input("Enter department abbreviation: ")

    # Find the corresponding section by section number and course number in the table "sections"
    # This is in order to ensure that we are not deleting a section from another course
    section = sections.find_one({"section number": section_number, "course": course_number})

    if section is not None:
        # If we were able to find the section provided by the user then...

        # Remove the section from the sections collection
        result = sections.delete_one({"section number": section_number})
        print(f"Deleted {result.deleted_count} section(s) with section number {section_number}")

        # Update the corresponding course to remove the reference to the deleted section
        course_id = section["course"]
        courses.update_one({"_id": course_id}, {"$pull": {"sections": section["_id"]}})
        print(f"Updated course with ID {course_id} by removing the deleted section")

    else:
        print(
            f"No section found with that section number {section_number} and course number {course_number} in department {department_abbr}")


def delete_student(db):
    students = db["students"]
    email = input("Enter student email: ")
    student = students.find_one({"email": email})
    if student:
        try:
            students.delete_one({"email": email})
            # delete the student major records
            db["StudentMajor"].delete_many({"email": email})

            print(f"Deleted student with email {email}")
        except Exception as e:
            print(f"Failed deleting student with email {email}")
            pprint(e)
    else:
        print(f"Student with email {email} was not found, sorry")

def drop_all_collections(db):
    print()
    print("""
    DELETING TABLES... (Staring from 0 tables) 
    """)

    collections = ['departments', 'courses', 'sections', 'students', 'enrollment']
    for collection in collections:
        db[collection].drop()

if __name__ == '__main__':
    uri = connect_string.myConnectString
    # Create a new client and connect to the server
    client = MongoClient(uri, tlsCAFile=certifi.where())

    # As a test that the connection worked, print out the database names.
    print(client.list_database_names())

    # db will be the way that we refer to the database from here on out.
    db = client["CECS323Spring2023"]

    # Call the function to drop all collections everytime we run the code, so we can start clean
    drop_all_collections(db)

    # Print off the collections that we have available to us, again more of a test than anything.
    print(db.list_collection_names())

    # Departments collection will have the following attributes:
    # i.	name – String length 50.  This is the primary key for this table.
    # ii.	abbreviation – String length 6 – mandatory
    # iii.	chair_name – String length 80 – mandatory
    # iv.	building – IN ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4',
    #                       'EN5', 'ET', 'HSCI', 'NUR', 'VEC'] – mandatory
    # v.	office – Integer – mandatory
    # vi.	description – String length 80 – mandatory

    # CREATING DEPARTMENT VALIDATOR
    department_validator = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "description": "a division of a large organization dealing with a specific subject",
                "required": ["name", "abbreviation", "chair name", "building", "office", "description"],
                "properties": {
                    "name": {
                        "bsonType": "string",
                        "maxLength": 50,
                        "$expr": {
                            "$lte": [{"$strLenBytes": "$name"}, 50]
                        }
                    },
                    "abbreviation": {
                        "bsonType": "string",
                        "maxLength": 6,
                        "$expr": {
                            "$lte": [{"$strLenBytes": "$abbreviation"}, 6]
                        }
                    },
                    "chair name": {
                        "bsonType": "string",
                        "maxLength": 80,
                        "$expr": {
                            "$lte": [{"$strLenBytes": "$chair name"}, 80]
                        }
                    },
                    "building": {
                        "bsonType": "string",
                        "enum": ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC']
                    },
                    "office": {
                        "bsonType": "int"
                    },
                    "description": {
                        "bsonType": "string",
                        "maxLength": 80,
                        "$expr": {
                            "$lte": [{"$strLenBytes": "$description"}, 80]
                        }
                    },
                    "courses": {
                        "bsonType": "array",
                        "items": {
                            "bsontype": "int"
                        }
                    },
                    "majors": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["name", "description"],
                            "properties": {
                                "name": {
                                    "bsonType": "string"
                                },
                                "description": {
                                    "bsonType": "string"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    try:
        db.create_collection('departments', **department_validator)
    except Exception:
        print("Department collection already exists")

    # CREATING COURSE VALIDATOR
    course_validator = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "description": "classes offered by a specific learning curriculum",
                "required": ["courseNumber", "name", "description", "units"],
                "properties": {
                    "courseNumber": {
                        "bsonType": "int",
                        "minimum": 100,
                        "maximum": 699
                    },
                    "name": {
                        "bsonType": "string",
                        "maxLength": 50
                    },
                    "description": {
                        "bsonType": "string",
                        "maxLength": 80
                    },
                    "units": {
                        "bsonType": "int",
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                "allOf": [
                    {
                        "$expr": {
                            "$lte": [{"$strLenBytes": "$name"}, 50]
                        }
                    },
                    {
                        "$expr": {
                            "$lte": [{"$strLenBytes": "$description"}, 80]
                        }
                    }
                ]
            }
        }
    }

    try:
        db.create_collection('courses', **course_validator)
    except Exception:
        print("Course collection already exists")

    # CREATING SECTION VALIDATOR
    section_validator = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "description": "a section of a course",
                "required": ["section number", "semester", "section year", "building", "room", "schedule", "startTime",
                             "instructor"],
                "properties": {
                    "section number": {
                        "bsonType": "int",
                        "min": 1
                    },
                    "semester": {
                        "bsonType": "string",
                        "enum": ['Fall', 'Spring', 'Summer I', 'Summer II', 'Summer III', 'Winter']
                    },
                    "section year": {
                        "bsonType": "int"
                    },
                    "building": {
                        "bsonType": "string",
                        "enum": ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC']
                    },
                    "room": {
                        "bsonType": "int",
                        "minimum": 1,
                        "maximum": 999
                    },
                    "schedule": {
                        "bsonType": "string",
                        "enum": ['MW', 'TuTh', 'MWF', 'F', 'S']
                    },
                    "startTime": {
                        "bsonType": "string",
                        "pattern": "^(0[89]|1[0-9]|2[0-2]):[0-5][0-9](AM|PM)$",
                        "description": "start time must be between 8:00 AM and 10:00 PM"
                    },
                    "instructor": {
                        "bsonType": "string",
                        "maxLength": 80
                    },
                    "course": {
                        "bsonType": "int"
                    }
                },
                "allOf": [
                    {"$expr": {"$lte": [{"$strLenBytes": "$instructor"}, 80]}},
                    {"$expr": {"$lte": [{"$strLenBytes": "$semester"}, 12]}},
                    {"$expr": {"$lte": [{"$strLenBytes": "$building"}, 4]}}
                ]
            }
        }
    }

    try:
        db.create_collection('sections', **section_validator)
    except Exception:
        print("Section collection already exists")

    # CREATING STUDENT VALIDATOR
    student_validator = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "description": "a student",
                "required": ["first_name", "last_name", "email"],
                "properties": {
                    "first_name": {
                        "bsonType": "string"
                    },
                    "last_name": {
                        "bsonType": "string"
                    },
                    "email": {
                        "bsonType": "string"
                    },
                    "StudentMajor": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["major_name", "declaration_date"],
                            "properties": {
                                "major_name": {
                                    "bsonType": "string"
                                },
                                "declaration_date": {
                                    "bsonType": "date",
                                    "maximum": {"$date": "2023-05-07T00:00:00.000Z"}
                                }
                            }
                        }
                    },
                    "Enrollment": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["id"],
                            "properties": {
                                "id": {
                                    "bsonType": "int"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    try:
        db.create_collection('students', **student_validator)
    except Exception:
        print("Student collection already exists")

    currentDate = datetime.today().strftime('%Y-%m-%d');

    # Creating enrollment validator
    enrollment_validator = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "description": "The enrollment status of a current student.",
                "required": ["semester", "section_year", "department_abbreviation", "course_number", "section_number"],

                "properties": {
                    "semester": {
                        "bsonType": "string",
                    },
                    "section_year": {
                        "bsonType": "string",
                    },
                    "department_abbreviation": {
                        "bsonType": "string",
                    },
                    "course_number": {
                        "bsonType": "string",
                    },
                    "section_number": {
                        "bsonType": "int",
                    },
                    "pass_fail": {
                        "bsonType": "date",
                        "max": currentDate
                    },
                    "letter_grade": {
                        "bsonType": "string",
                        "enum": ["A", "B", "C"]
                    }
                },
                # Use the oneOf sub schema validator to make sure ONLY one of the
                # subschemas is present, either Pass/Fail or Letter Grade
                "oneOf": [{"required": ["pass_fail"]},
                          {"required": ["letter_grade"]}]
            }
        },
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "description": "The enrollment status of a current student.",
                "required": ["semester", "section_year", "department_abbreviation", "course_number", "section_number"],

                "properties": {
                    "pass_fail": {
                        "bsonType": "object",
                        "description": "Pass/fail status of a student's enrollment",
                        "required": ["application_date"],
                        "properties": {
                            "application_date": {
                                "bsonType": "date",
                                "maximum": currentDate
                            }
                        }
                    },
                    "letter_grade": {
                        "bsonType": "object",
                        "description": "Letter grade for a student's enrollment",
                        "required": ["min_satisfactory"],
                        "properties": {
                            "min_satisfactory": {
                                "bsonType": "string",
                                "enum": ["A", "B", "C"]
                            }
                        }
                    }
                },
                # Use the oneOf sub schema validator to make sure ONLY one of the
                # subschemas is present, either Pass/Fail or Letter Grade
                "oneOf": [{"required": ["pass_fail"]},
                          {"required": ["letter_grade"]}]
            }
        }
    }

    try:
        db.create_collection('enrollment', **enrollment_validator)
    except Exception:
        print("Enrollment collection already exists")

    # Create a departments collection in MongoDB.
    departments = db["departments"]

    # Create a courses collection in MongoDB.
    courses = db["courses"]

    # Create a sections collection in MongoDB.
    sections = db["sections"]

    # Create a student collection in MongoDB.
    students = db["students"]

    # Create an enrollment
    enrollment = db["enrollments"]

    # Create the new unique index on the "name" field
    departments.create_index("name", unique=True)
    departments.create_index("abbreviation", unique=True)
    departments.create_index([("building", 1), ("office", 1)], unique=True)
    departments.create_index("chairName", unique=True)

    # Add uniqueness constraints for the courses collection
    courses.create_index([("departmentAbbreviation", 1), ("courseNumber", 1)], unique=True)
    courses.create_index([("departmentAbbreviation", 1), ("courseName", 1)], unique=True)

    # Add uniqueness constraints for the sections collection
    sections.create_index([("course", 1), ("section number", 1), ("semester", 1), ("section year", 1)], unique=True)
    sections.create_index(
        [("semester", 1), ("section year", 1), ("building", 1), ("room", 1), ("schedule", 1), ("startTime", 1)],
        unique=True)
    sections.create_index([("semester", 1), ("section year", 1), ("schedule", 1), ("startTime", 1), ("instructor", 1)],
                          unique=True)
    sections.create_index(
        [("semester", 1), ("section year", 1), ("departmentAbbreviation", 1), ("courseNumber", 1), ("studentID", 1)],
        unique=True)

    # Add uniqueness constraints for the students collection
    students.create_index([("lastName", 1), ("firstName", 1)], unique=True)
    students.create_index([("eMail", 1)], unique=True)

    # Uniqueness constraints for Student Major. An student can have only one major, and a major can only have one student
    db.students.create_index(
        [("StudentMajor.student", pymongo.ASCENDING), ("StudentMajor.majorName", pymongo.ASCENDING)],
        unique=True
    )

    # No student can be enrolled in more than one section of the same course in the same semester
    enrollment.create_index([
        ("semester", pymongo.ASCENDING),
        ("section_year", pymongo.ASCENDING),
        ("section_number", pymongo.ASCENDING),  # added field
        ("department_abbreviation", pymongo.ASCENDING),
        ("course_number", pymongo.ASCENDING),
        ("studentID", pymongo.ASCENDING)],
        unique=True)

    main_action: str = ''
    while main_action != menu_main.last_action():
        main_action = menu_main.menu_prompt()
        print('next action: ', main_action)
        exec(main_action)
