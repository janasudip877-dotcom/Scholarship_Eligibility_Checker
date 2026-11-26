import json
import mimetypes
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from data import delete_student_by_id, students_db
from screening import evaluate_student, generate_report, validate_student


PROJECT_ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "index.html"
STATIC_ROOT = PROJECT_ROOT / "static"
last_result = None
last_notice = ""


# Browser-er form-er text value-gulo number-e bodle validate kori.
def student_from_form(values):
    try:
        student = {
            "student_id": values.get("student_id", "").strip(),
            "name": values.get("name", "").strip(),
            "programme": values.get("programme", "").strip(),
            "semester": int(values.get("semester", "")),
            "cgpa": float(values.get("cgpa", "")),
            "attendance": float(values.get("attendance", "")),
            "family_income": float(values.get("family_income", "")),
            "backlogs": int(values.get("backlogs", "")),
            "category": values.get("category", ""),
            "extracurricular": values.get("extracurricular", ""),
            "first_gen": values.get("first_gen", ""),
            "disability": values.get("disability", ""),
            "previous_scholarship": values.get("previous_scholarship", ""),
            "enrollment": values.get("enrollment", ""),
        }
    except (TypeError, ValueError, OverflowError):
        return None, "Enter valid numeric values for all required academic and financial fields."

    is_valid, message = validate_student(student)
    if not is_valid:
        return None, message
    return student, ""


def render_page(workspace_open):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    page_data = {
        "students": [evaluate_student(student) for student in students_db],
        "last_result": last_result,
        "notice": last_notice,
    }
    encoded_data = json.dumps(page_data, ensure_ascii=False).replace("<", "\\u003c")
    template = template.replace("__SCREENING_DATA__", encoded_data)
    template = template.replace("__WORKSPACE_OPEN__", "true" if workspace_open else "false")
    return template.encode("utf-8")


class ScholarshipRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global last_notice
        request = urlparse(self.path)

        if request.path == "/":
            query = parse_qs(request.query)
            self.send_content(
                200,
                render_page(query.get("workspace", [""])[0] == "1"),
                "text/html; charset=utf-8",
            )
            last_notice = ""
        elif request.path == "/report":
            report_text = generate_report(students_db).encode("utf-8")
            self.send_content(
                200,
                report_text,
                "text/plain; charset=utf-8",
                "attachment; filename=scholarship-screening-report.txt",
            )
        elif request.path.startswith("/static/"):
            self.send_static_file(request.path)
        else:
            self.send_content(404, b"Page not found.", "text/plain; charset=utf-8")

    def do_POST(self):
        global last_result, last_notice
        request_path = urlparse(self.path).path
        if request_path not in ("/", "/delete"):
            self.send_content(404, b"Page not found.", "text/plain; charset=utf-8")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_content(400, b"Invalid request length.", "text/plain; charset=utf-8")
            return
        if content_length <= 0 or content_length > 65536:
            self.send_content(400, b"Invalid form submission.", "text/plain; charset=utf-8")
            return

        form_data = self.rfile.read(content_length).decode("utf-8")
        values = {
            key: items[0] if items else ""
            for key, items in parse_qs(form_data, keep_blank_values=True).items()
        }
        if request_path == "/delete":
            student_id = values.get("student_id", "").strip()
            removed_student = delete_student_by_id(student_id)
            if removed_student is None:
                last_notice = "No student found with ID {}.".format(student_id or "(blank)")
            else:
                if last_result and last_result["student"]["student_id"].casefold() == student_id.casefold():
                    last_result = None
                last_notice = "{} ({}) was removed from the current session.".format(
                    removed_student["name"], removed_student["student_id"]
                )
            self.redirect_to_workspace()
            return

        student, message = student_from_form(values)
        duplicate_id = student is not None and any(
            saved["student_id"].casefold() == student["student_id"].casefold()
            for saved in students_db
        )

        if student is None or duplicate_id:
            last_result = None
            last_notice = "Student ID already exists." if duplicate_id else message
        else:
            students_db.append(student)
            last_result = {
                "student": evaluate_student(student),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            last_notice = "Screening completed for {}.".format(student["name"])

        self.redirect_to_workspace()

    def redirect_to_workspace(self):
        self.send_response(303)
        self.send_header("Location", "/?workspace=1")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # Browser-ke CSS/JS ar onnanno static file pathai.
    def send_static_file(self, request_path):
        file_path = (STATIC_ROOT / request_path[len("/static/"):]).resolve()
        try:
            file_path.relative_to(STATIC_ROOT.resolve())
        except ValueError:
            self.send_content(404, b"File not found.", "text/plain; charset=utf-8")
            return
        if not file_path.is_file():
            self.send_content(404, b"File not found.", "text/plain; charset=utf-8")
            return

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_content(200, file_path.read_bytes(), content_type)

    def send_content(self, status, body, content_type, disposition=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if disposition:
            self.send_header("Content-Disposition", disposition)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        print("[{}] {}".format(self.log_date_time_string(), format_string % args))


def run_server(port=8000):
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")

    server = HTTPServer(("127.0.0.1", port), ScholarshipRequestHandler)
    print("Scholarship Eligibility System running at http://127.0.0.1:{}/".format(port))
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
