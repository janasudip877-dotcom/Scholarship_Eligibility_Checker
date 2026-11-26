document.addEventListener("DOMContentLoaded", () => {
    const dataElement = document.getElementById("screening-data");
    const pageData = JSON.parse(dataElement.textContent);
    let students = pageData.students;
    let currentFilter = "all";
    let ranked = false;

    const clockElements = [
        document.getElementById("live-clock"),
        document.getElementById("workspace-clock")
    ];
    const updateClock = () => {
        const now = new Date().toLocaleString("en-IN", {
            timeZone: "Asia/Kolkata",
            dateStyle: "medium",
            timeStyle: "medium"
        });
        clockElements.forEach((element) => {
            if (element) element.textContent = now;
        });
    };
    updateClock();
    window.setInterval(updateClock, 1000);

    if (window.openWorkspaceOnLoad) openScreeningDashboard();

    const notice = document.getElementById("log-display");
    if (pageData.last_result) {
        const { student, timestamp } = pageData.last_result;
        writeLog([
            `[+] Screening completed at ${timestamp}`,
            "======================================================",
            `FINAL CLASSIFICATION: ${student.status}`,
            `CALCULATED SCORE    : ${student.score} / 100`,
            "------------------------------------------------------",
            ...student.explanation.map((line) => `> ${line}`)
        ].join("\n"));
    } else if (pageData.notice) {
        writeLog(pageData.notice);
    }

    const tbody = document.getElementById("student-table-body");
    const filterButtons = document.querySelectorAll("[data-filter]");
    const searchInput = document.getElementById("student-search");

    function filteredStudents() {
        const query = searchInput.value.trim().toLocaleLowerCase();
        let visible = students.filter((student) => {
            const matchesQuery = !query
                || student.name.toLocaleLowerCase().includes(query)
                || student.student_id.toLocaleLowerCase().includes(query);
            const matchesFilter = currentFilter === "all"
                || student.status === currentFilter;
            return matchesQuery && matchesFilter;
        });
        if (ranked) {
            visible = visible
                .filter((student) => ["Eligible", "Highly Eligible"].includes(student.status))
                .sort((first, second) => second.score - first.score);
        }
        return visible;
    }

    function renderTable() {
        tbody.replaceChildren();
        const visible = filteredStudents();
        if (!visible.length) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 10;
            cell.className = "empty-state";
            cell.textContent = "No students match this view.";
            row.appendChild(cell);
            tbody.appendChild(row);
        }

        visible.forEach((student) => {
            const row = document.createElement("tr");
            const identityCell = document.createElement("td");
            const identity = document.createElement("span");
            identity.className = "student-cell";
            const avatar = document.createElement("span");
            avatar.className = "student-avatar";
            avatar.textContent = student.name.trim().charAt(0).toUpperCase() || "?";
            const copy = document.createElement("span");
            copy.className = "student-cell-copy";
            const name = document.createElement("b");
            name.textContent = student.name;
            const id = document.createElement("small");
            id.textContent = student.student_id;
            const detailsButton = document.createElement("button");
            detailsButton.type = "button";
            detailsButton.className = "detail-toggle";
            detailsButton.textContent = "View decision";

            const deleteForm = document.createElement("form");
            deleteForm.className = "delete-form";
            deleteForm.method = "post";
            deleteForm.action = "/delete";
            const studentIdInput = document.createElement("input");
            studentIdInput.type = "hidden";
            studentIdInput.name = "student_id";
            studentIdInput.value = student.student_id;
            const deleteButton = document.createElement("button");
            deleteButton.type = "submit";
            deleteButton.className = "delete-button";
            deleteButton.textContent = "Delete record";
            deleteForm.append(studentIdInput, deleteButton);
            deleteForm.addEventListener("submit", (event) => {
                if (!window.confirm(`Delete ${student.name} (${student.student_id})? This cannot be undone.`)) {
                    event.preventDefault();
                }
            });

            copy.append(name, id, detailsButton, deleteForm);
            identity.append(avatar, copy);
            identityCell.appendChild(identity);
            row.appendChild(identityCell);

            const values = [
                student.programme,
                student.category,
                student.cgpa,
                `${student.attendance}%`,
                `₹${Number(student.family_income).toLocaleString("en-IN")}`,
                student.backlogs,
                student.previous_scholarship
            ];
            values.forEach((value) => {
                const cell = document.createElement("td");
                cell.textContent = String(value);
                row.appendChild(cell);
            });

            const scoreCell = document.createElement("td");
            const scoreWrap = document.createElement("span");
            scoreWrap.className = "score-cell";
            const score = document.createElement("b");
            score.textContent = String(student.score);
            const track = document.createElement("span");
            track.className = "score-track";
            const fill = document.createElement("span");
            fill.style.width = `${Math.max(0, Math.min(100, Number(student.score) || 0))}%`;
            track.appendChild(fill);
            scoreWrap.append(score, track);
            scoreCell.appendChild(scoreWrap);
            row.appendChild(scoreCell);

            const statusCell = document.createElement("td");
            const badge = document.createElement("span");
            const classes = {
                "Highly Eligible": "badge-highly",
                "Eligible": "badge-eligible",
                "Conditionally Eligible": "badge-conditional"
            };
            badge.className = `badge ${classes[student.status] || "badge-not"}`;
            badge.textContent = student.status.toUpperCase();
            statusCell.appendChild(badge);
            row.appendChild(statusCell);
            tbody.appendChild(row);

            const detailRow = document.createElement("tr");
            detailRow.className = "decision-detail hidden";
            const detailCell = document.createElement("td");
            detailCell.colSpan = 10;
            const detailHeading = document.createElement("strong");
            detailHeading.textContent = `${student.status} — decision explanation`;
            const explanationList = document.createElement("ul");
            student.explanation.forEach((line) => {
                const item = document.createElement("li");
                item.textContent = line;
                explanationList.appendChild(item);
            });
            detailCell.append(detailHeading, explanationList);
            detailRow.appendChild(detailCell);
            tbody.appendChild(detailRow);

            detailsButton.addEventListener("click", () => {
                const isHidden = detailRow.classList.toggle("hidden");
                detailsButton.textContent = isHidden ? "View decision" : "Hide decision";
            });
        });
        updateMetrics(students);
        const count = document.getElementById("registry-count");
        count.textContent = `${visible.length} ${visible.length === 1 ? "record" : "records"}`;
    }

    function updateMetrics(records) {
        const countByStatus = (status) => records.filter((student) => student.status === status).length;
        document.getElementById("total-students").textContent = String(records.length).padStart(2, "0");
        document.getElementById("eligible-count").textContent = String(
            countByStatus("Eligible") + countByStatus("Highly Eligible")
        ).padStart(2, "0");
        document.getElementById("high-merit-count").textContent = String(
            countByStatus("Highly Eligible")
        ).padStart(2, "0");
        document.getElementById("summary-highly").textContent = String(countByStatus("Highly Eligible"));
        document.getElementById("summary-eligible").textContent = String(countByStatus("Eligible"));
        document.getElementById("summary-conditional").textContent = String(countByStatus("Conditionally Eligible"));
        document.getElementById("summary-not").textContent = String(countByStatus("Not Eligible"));
    }

    function writeLog(message) {
        notice.textContent = message;
        const resultPanel = notice.closest(".result-panel");
        if (resultPanel) resultPanel.classList.add("has-result");
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            currentFilter = button.dataset.filter;
            ranked = false;
            filterButtons.forEach((item) => item.classList.toggle("active", item === button));
            renderTable();
        });
    });

    searchInput.addEventListener("input", renderTable);
    document.getElementById("rank-button").addEventListener("click", () => {
        currentFilter = "all";
        ranked = true;
        filterButtons.forEach((button) => {
            button.classList.toggle("active", button.dataset.filter === "all");
        });
        renderTable();
        const eligibleCount = students.filter(
            (student) => ["Eligible", "Highly Eligible"].includes(student.status)
        ).length;
        writeLog(`Merit ranking complete. Ranked ${eligibleCount} eligible applicants by score.`);
    });

    renderTable();
});
