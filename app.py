import sys
from datetime import datetime

from data import delete_student_by_id, students_db
from screening import calculate_eligibility, calculate_score, evaluate_student, generate_report
from web import run_server


# Ei function-ta menu-te application ar tar result dekhay.
def display_students(students):
    if not students:
        print("No applications found.")
        return

    for student in students:
        result = evaluate_student(student)
        print(
            "{} | {} | {} | CGPA {} | Score {} | {}".format(
                student["student_id"],
                student["name"],
                student["programme"],
                student["cgpa"],
                result["score"],
                result["status"],
            )
        )


def show_summary():
    statuses = [calculate_eligibility(student) for student in students_db]
    print("\nScholarship summary")
    print("-------------------")
    print("Total applications: {}".format(len(students_db)))
    for status in ("Highly Eligible", "Eligible", "Conditionally Eligible", "Not Eligible"):
        print("{}: {}".format(status, statuses.count(status)))


# Ekhane while loop user-er menu choice niye shei kaj-ta kore.
def run_menu():
    while True:
        print(
            "\n====================================================\n"
            " SCHOLARSHIP ELIGIBILITY SCREENING SYSTEM\n"
            "====================================================\n"
            "1. Display All Applications\n"
            "2. Screen Individual Student\n"
            "3. Screen All Students\n"
            "4. Search Student\n"
            "5. Display Eligible Students\n"
            "6. Display Highly Eligible Students\n"
            "7. Rank Eligible Students\n"
            "8. Display Scholarship Summary\n"
            "9. Display Screening Date and Time\n"
            "10. Generate Screening Report\n"
            "11. Delete Student Record\n"
            "12. Exit"
        )
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_students(students_db)
        elif choice == "2":
            student_id = input("Enter student ID: ").strip().casefold()
            matches = [
                student for student in students_db
                if student["student_id"].casefold() == student_id
            ]
            display_students(matches)
            for student in matches:
                for line in evaluate_student(student)["explanation"]:
                    print("  - {}".format(line))
        elif choice == "3":
            display_students(students_db)
            for student in students_db:
                print("Decision details for {}:".format(student["student_id"]))
                for line in evaluate_student(student)["explanation"]:
                    print("  - {}".format(line))
        elif choice == "4":
            query = input("Enter a student ID or name: ").strip().casefold()
            matches = [
                student for student in students_db
                if query in student["student_id"].casefold()
                or query in student["name"].casefold()
            ]
            display_students(matches)
        elif choice == "5":
            display_students([
                student for student in students_db
                if calculate_eligibility(student) in ("Eligible", "Highly Eligible")
            ])
        elif choice == "6":
            display_students([
                student for student in students_db
                if calculate_eligibility(student) == "Highly Eligible"
            ])
        elif choice == "7":
            eligible = [
                student for student in students_db
                if calculate_eligibility(student) in ("Eligible", "Highly Eligible")
            ]
            ranked = sorted(eligible, key=lambda student: calculate_score(student), reverse=True)
            for position, student in enumerate(ranked, start=1):
                print("{}. ".format(position), end="")
                display_students([student])
        elif choice == "8":
            show_summary()
        elif choice == "9":
            print(datetime.now().strftime("Screening date and time: %Y-%m-%d %H:%M:%S"))
        elif choice == "10":
            print(generate_report(students_db))
        elif choice == "11":
            student_id = input("Enter the student ID to delete: ").strip()
            student = next(
                (
                    record for record in students_db
                    if record["student_id"].casefold() == student_id.casefold()
                ),
                None,
            )
            if student is None:
                print("No student found with that ID.")
                continue
            print("This will remove {} ({}) from the current session.".format(
                student["name"], student["student_id"]
            ))
            confirmation = input("Are you sure? (y/n): ").strip().casefold()
            if confirmation in ("y", "yes"):
                delete_student_by_id(student_id)
                print("Student record deleted.")
            else:
                print("Deletion cancelled.")
        elif choice == "12":
            print("Thank you for using the screening system.")
            break
        else:
            print("Please enter a number from 1 to 12.")


# Default-e website chole; --cli dile menu version-ta khule.
if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_menu()
    else:
        port = 8000
        if "--port" in sys.argv:
            port_index = sys.argv.index("--port") + 1
            if port_index >= len(sys.argv):
                raise SystemExit("Provide a port number after --port.")
            try:
                port = int(sys.argv[port_index])
            except ValueError:
                raise SystemExit("Port must be a number.")
        run_server(port)
