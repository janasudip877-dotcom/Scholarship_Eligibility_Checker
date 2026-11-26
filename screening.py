import math
from datetime import datetime


# Form theke asha student-er value-gulo thik ache kina age dekhi.
def validate_student(student):
    required_text = ("student_id", "name", "programme", "category")
    for field in required_text:
        if not str(student.get(field, "")).strip():
            return False, "{} cannot be blank.".format(field.replace("_", " ").title())

    try:
        semester = int(student["semester"])
        cgpa = float(student["cgpa"])
        attendance = float(student["attendance"])
        family_income = float(student["family_income"])
        backlogs = int(student["backlogs"])
    except (KeyError, TypeError, ValueError, OverflowError):
        return False, "Enter valid numeric values for semester, CGPA, attendance, income, and backlogs."

    if not 1 <= semester <= 8:
        return False, "Semester must be between 1 and 8."
    if not math.isfinite(cgpa) or not 0 <= cgpa <= 10:
        return False, "CGPA must be between 0 and 10."
    if not math.isfinite(attendance) or not 0 <= attendance <= 100:
        return False, "Attendance must be between 0 and 100."
    if not math.isfinite(family_income) or family_income < 0:
        return False, "Income cannot be negative."
    if backlogs < 0:
        return False, "Backlogs cannot be negative."

    if student["category"] not in ("General", "OBC", "SC", "ST", "EWS", "Other"):
        return False, "Select a valid category."

    for field in ("extracurricular", "first_gen", "disability", "previous_scholarship"):
        if student.get(field) not in ("Yes", "No"):
            return False, "Select Yes or No for {}.".format(field.replace("_", " "))

    if student.get("enrollment") not in ("Active", "Inactive"):
        return False, "Select a valid enrollment status."
    return True, "Valid data."


# Prottekta scholarship rule alada rakhlam, bujhte ar explain korte subidha hobe.
def check_academic_eligibility(student):
    return float(student["cgpa"]) >= 7.00


def check_attendance_eligibility(student):
    return float(student["attendance"]) >= 75


def check_income_eligibility(student):
    return float(student["family_income"]) <= 500000


def check_backlog_eligibility(student):
    return int(student["backlogs"]) <= 1


def check_enrollment(student):
    return str(student["enrollment"]).strip().casefold() == "active"


def calculate_eligibility(student):
    academic = check_academic_eligibility(student)
    attendance = check_attendance_eligibility(student)
    income = check_income_eligibility(student)
    backlogs = check_backlog_eligibility(student)
    enrollment = check_enrollment(student)
    all_mandatory_rules_pass = academic and attendance and income and backlogs and enrollment

    if all_mandatory_rules_pass and student["cgpa"] >= 8.50 and student["attendance"] >= 85:
        return "Highly Eligible"
    if all_mandatory_rules_pass:
        return "Eligible"
    if (
        6.75 <= student["cgpa"] < 7.00
        and attendance and income and backlogs and enrollment
    ):
        return "Conditionally Eligible"
    return "Not Eligible"


# Score-e CGPA-r 60% ar attendance-r 40% dhora hoyeche.
def calculate_score(student):
    return round(float(student["cgpa"]) * 6 + float(student["attendance"]) * 0.4, 2)


def generate_explanation(student):
    checks = (
        ("Academic Requirement (CGPA >= 7.00)", check_academic_eligibility(student)),
        ("Attendance Requirement (>= 75%)", check_attendance_eligibility(student)),
        ("Income Requirement (<= Rs. 5,00,000)", check_income_eligibility(student)),
        ("Backlog Requirement (<= 1)", check_backlog_eligibility(student)),
        ("Enrollment Status (Active)", check_enrollment(student)),
    )
    explanation = [
        "{}: {}".format(label, "PASS" if passed else "FAIL")
        for label, passed in checks
    ]
    status = calculate_eligibility(student)

    if status == "Conditionally Eligible":
        explanation.append(
            "Reason: CGPA is between 6.75 and 7.00; all other mandatory conditions are satisfied."
        )
    elif status == "Not Eligible":
        failed_rules = [label for label, passed in checks if not passed]
        explanation.append("Reason: Mandatory conditions not met: {}.".format(", ".join(failed_rules)))
    else:
        explanation.append("Reason: All mandatory eligibility conditions are satisfied.")

    extra_points = []
    if student["cgpa"] >= 8.50:
        extra_points.append("Merit condition (CGPA >= 8.50)")
    if student["attendance"] >= 90:
        extra_points.append("High attendance (>= 90%)")
    if student["extracurricular"] == "Yes":
        extra_points.append("Extracurricular achievement")
    if student["first_gen"] == "Yes" or student["disability"] == "Yes":
        extra_points.append("Special consideration (first-generation learner or disability)")
    explanation.append(
        "Additional considerations: {}.".format(", ".join(extra_points) if extra_points else "None recorded")
    )
    explanation.append(
        "Category: {} | Previous scholarship: {}. These details are recorded but do not change "
        "eligibility because no exclusion rule is specified.".format(
            student["category"], student["previous_scholarship"].casefold()
        )
    )
    return explanation


def evaluate_student(student):
    result = student.copy()
    result["status"] = calculate_eligibility(student)
    result["score"] = calculate_score(student)
    result["explanation"] = generate_explanation(student)
    return result


# Ei report-e shob applicant-er result ar report-er shomoy dekhano hoy.
def generate_report(students):
    screened_students = [evaluate_student(student) for student in students]
    lines = [
        "SCHOLARSHIP ELIGIBILITY SCREENING REPORT",
        "Generated: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "=" * 72,
        "Applications screened: {}".format(len(screened_students)),
        "",
        "SUMMARY",
    ]
    for status in ("Highly Eligible", "Eligible", "Conditionally Eligible", "Not Eligible"):
        count = sum(1 for student in screened_students if student["status"] == status)
        lines.append("{}: {}".format(status, count))

    lines.extend(["", "APPLICATION DETAILS", "=" * 72])
    if not screened_students:
        lines.append("No applications are available.")

    for student in screened_students:
        lines.extend(
            [
                "",
                "{} | {}".format(student["student_id"], student["name"]),
                "Programme: {} | Semester: {} | Category: {}".format(
                    student["programme"], student["semester"], student["category"]
                ),
                "CGPA: {} | Attendance: {}% | Family income: Rs. {:,.0f}".format(
                    student["cgpa"], student["attendance"], student["family_income"]
                ),
                "Backlogs: {} | Enrollment: {} | Previous scholarship: {}".format(
                    student["backlogs"], student["enrollment"], student["previous_scholarship"]
                ),
                "Score: {} / 100 | Classification: {}".format(student["score"], student["status"]),
                "Decision explanation:",
            ]
        )
        lines.extend("  - {}".format(item) for item in student["explanation"])
        lines.append("-" * 72)
    return "\n".join(lines)
