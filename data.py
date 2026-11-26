# Demo dekhanor jonno kichu application list-e rekhechi.
students_db = [
    {
        "student_id": "AUBC24001",
        "name": "Rahul Sen",
        "programme": "B.C.A",
        "semester": 4,
        "cgpa": 8.24,
        "attendance": 82,
        "family_income": 380000,
        "backlogs": 0,
        "category": "General",
        "extracurricular": "Yes",
        "first_gen": "No",
        "disability": "No",
        "previous_scholarship": "No",
        "enrollment": "Active",
    },
    {
        "student_id": "AUBC24002",
        "name": "Sudip Jana",
        "programme": "B.C.A",
        "semester": 4,
        "cgpa": 9.40,
        "attendance": 92,
        "family_income": 240000,
        "backlogs": 0,
        "category": "General",
        "extracurricular": "Yes",
        "first_gen": "Yes",
        "disability": "No",
        "previous_scholarship": "No",
        "enrollment": "Active",
    },
]


# Student ID diye record-ta list theke khuje ber kore bad dei.
def delete_student_by_id(student_id):
    for index, student in enumerate(students_db):
        if student["student_id"].casefold() == student_id.strip().casefold():
            return students_db.pop(index)
    return None
