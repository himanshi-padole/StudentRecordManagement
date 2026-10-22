
const API_URL = "/api/students";
const ANALYTICS_URL = "/api/analytics";
const TABLE_SIZE = 10;

let students = [];
let editingRoll = null;

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function hashFunction(roll) {
    let total = 0;
    for (const char of String(roll)) {
        total += char.charCodeAt(0);
    }
    return total % TABLE_SIZE;
}

function showMessage(message) {
    alert(message);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || data.message || "Request failed.");
    }

    return data;
}

async function loadStudents() {
    try {
        const data = await apiRequest(API_URL);
        students = Array.isArray(data) ? data : (data.students || []);
        renderStudents();
        await loadAnalytics();
    } catch (error) {
        console.error("Could not load students:", error);
        showMessage(
            "Could not load student records. Make sure Flask is running and open the website using its localhost address."
        );
    }
}

async function loadAnalytics() {
    try {
        const data = await apiRequest(ANALYTICS_URL);

        if ($("totalStudents")) {
            $("totalStudents").textContent = data.total ?? students.length;
        }

        if ($("averageMarks")) {
            $("averageMarks").textContent = Number(data.average ?? getAverage()).toFixed(2);
        }

        if ($("topperName")) {
            $("topperName").textContent = data.topper?.name || getTopper()?.name || "—";
        }

        if ($("topperMarks")) {
            $("topperMarks").textContent =
                data.topper?.marks ?? getTopper()?.marks ?? "—";
        }
    } catch (error) {
        console.warn("Analytics endpoint unavailable; using loaded records.", error);
        updateDashboardFromStudents();
    }
}

function getAverage() {
    if (!students.length) return 0;

    return students.reduce(
        (sum, student) => sum + Number(student.marks || 0), 0
    ) / students.length;
}

function getTopper() {
    if (!students.length) return null;

    return students.reduce((best, student) =>
        Number(student.marks) > Number(best.marks) ? student : best
    );
}

function updateDashboardFromStudents() {
    if ($("totalStudents")) {
        $("totalStudents").textContent = students.length;
    }

    if ($("averageMarks")) {
        $("averageMarks").textContent = getAverage().toFixed(2);
    }

    const topper = getTopper();

    if ($("topperName")) {
        $("topperName").textContent = topper?.name || "—";
    }

    if ($("topperMarks")) {
        $("topperMarks").textContent = topper?.marks ?? "—";
    }
}

function renderStudents() {
    const tableBody = $("studentRows");
    if (!tableBody) return;

    const searchText = $("searchInput")?.value.trim().toLowerCase() || "";

    const filteredStudents = students.filter((student) =>
        String(student.name || "").toLowerCase().includes(searchText) ||
        String(student.roll_no || "").toLowerCase().includes(searchText)
    );

    tableBody.innerHTML = filteredStudents.map((student) => `
        <tr>
            <td>${escapeHtml(student.roll_no)}</td>
            <td>${escapeHtml(student.name)}</td>
            <td>${escapeHtml(student.department)}</td>
            <td>${escapeHtml(student.year)}</td>
            <td>${Number(student.marks || 0).toFixed(2)}</td>
            <td>${Number(student.attendance || 0)}%</td>
            <td>
                <button type="button" data-edit="${escapeHtml(student.roll_no)}">Edit</button>
                <button type="button" data-delete="${escapeHtml(student.roll_no)}">Delete</button>
            </td>
        </tr>
    `).join("");

    updateDashboardFromStudents();
    renderHashing();
}

function renderHashing() {
    const hashBox = $("hashResults");
    if (!hashBox) return;

    hashBox.innerHTML = students.map((student) => `
        <p>
            Roll no. ${escapeHtml(student.roll_no)}
            → Hash value: ${hashFunction(student.roll_no)}
        </p>
    `).join("");
}

function clearForm() {
    $("studentForm")?.reset();
    editingRoll = null;

    const submitButton = $("studentForm")?.querySelector('[type="submit"]');
    if (submitButton) submitButton.textContent = "Add Student";

    if ($("roll")) $("roll").disabled = false;
}

function openEditForm(student) {
    editingRoll = student.roll_no;

    $("roll").value = student.roll_no;
    $("name").value = student.name;
    $("department").value = student.department;
    $("year").value = student.year;
    $("marks").value = student.marks;

    $("roll").disabled = true;

    const submitButton = $("studentForm")?.querySelector('[type="submit"]');
    if (submitButton) submitButton.textContent = "Update Student";

    $("studentForm")?.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}

async function saveStudent(event) {
    event.preventDefault();

    const roll_no = $("roll").value.trim();
    const name = $("name").value.trim();
    const department = $("department").value;
    const year = Number($("year").value);
    const marks = Number($("marks").value);
    const attendance = Number($("attendance").value);

    if (!roll_no || !name || !department) {
        showMessage("Please fill in all student details.");
        return;
    }

    if (!Number.isInteger(year) || year < 1 || year > 4) {
        showMessage("Year must be between 1 and 4.");
        return;
    }

    if (!Number.isFinite(marks) || marks < 0 || marks > 100) {
        showMessage("Marks must be between 0 and 100.");
        return;
    }

    const studentData = { roll_no, name, department, year, marks,attendance };

    try {
        if (editingRoll !== null) {
            await apiRequest(
                `${API_URL}/${encodeURIComponent(editingRoll)}`,
                {
                    method: "PUT",
                    body: JSON.stringify(studentData)
                }
            );

            showMessage("Student record updated successfully.");
        } else {
            await apiRequest(API_URL, {
                method: "POST",
                body: JSON.stringify(studentData)
            });

            showMessage("Student added successfully.");
        }

        clearForm();
        await loadStudents();
    } catch (error) {
        console.error("Save failed:", error);
        showMessage(error.message || "Could not save the student.");
    }
}

async function deleteStudent(roll_no) {
    const student = students.find(
        (item) => String(item.roll_no) === String(roll_no)
    );

    if (!student) return;

    if (!confirm(`Delete student ${student.name} (${student.roll_no})?`)) {
        return;
    }

    try {
        await apiRequest(
            `${API_URL}/${encodeURIComponent(roll_no)}`,
            { method: "DELETE" }
        );

        showMessage("Student deleted successfully.");
        await loadStudents();
    } catch (error) {
        console.error("Delete failed:", error);
        showMessage(error.message || "Could not delete the student.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    $("studentForm")?.addEventListener("submit", saveStudent);

    $("searchInput")?.addEventListener("input", renderStudents);

    $("studentRows")?.addEventListener("click", (event) => {
        const editButton = event.target.closest("[data-edit]");
        const deleteButton = event.target.closest("[data-delete]");

        if (editButton) {
            const student = students.find(
                (item) => String(item.roll_no) === editButton.dataset.edit
            );

            if (student) openEditForm(student);
        }

        if (deleteButton) {
            deleteStudent(deleteButton.dataset.delete);
        }
    });

    $("cancelEdit")?.addEventListener("click", clearForm);
    $("refreshBtn")?.addEventListener("click", loadStudents);

    loadStudents();
});
