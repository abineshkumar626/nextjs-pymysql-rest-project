'use client';

import { useCallback, useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/students";
const emptyForm = { name: "", email: "", course: "" };

export default function Home() {
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadStudents = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(API);
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Unable to load students");
      setStudents(data);
    } catch (requestError) {
      setError(requestError.message || "Unable to connect to the student API");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  const filteredStudents = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return students;
    return students.filter((student) =>
      [student.name, student.email, student.course].some((value) =>
        value.toLowerCase().includes(query)
      )
    );
  }, [search, students]);

  const change = (event) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
    setMessage("");
    setError("");
  };

  const reset = () => {
    setEditingId(null);
    setForm(emptyForm);
  };

  const save = async (event) => {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    setError("");

    try {
      const endpoint = editingId ? `${API}/${editingId}` : API;
      const response = await fetch(endpoint, {
        method: editingId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Unable to save student");
      setMessage(data.message);
      reset();
      await loadStudents();
    } catch (requestError) {
      setError(requestError.message || "Unable to save student");
    } finally {
      setSaving(false);
    }
  };

  const edit = (student) => {
    setEditingId(student.id);
    setForm({ name: student.name, email: student.email, course: student.course });
    setMessage("");
    setError("");
    document.getElementById("student-form")?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  const remove = async (id) => {
    if (!window.confirm("Delete this student? This action cannot be undone.")) return;
    setError("");
    try {
      const response = await fetch(`${API}/${id}`, { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Unable to delete student");
      setMessage(data.message);
      await loadStudents();
    } catch (requestError) {
      setError(requestError.message || "Unable to delete student");
    }
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-mark">SM</div>
        <div>
          <p className="eyebrow">Academic records</p>
          <h1>Student Management</h1>
        </div>
        <div className="student-count" aria-label={`${students.length} students`}>
          <strong>{students.length}</strong>
          <span>Active students</span>
        </div>
      </header>

      <section className="dashboard-grid">
        <article className="panel form-panel" id="student-form">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">{editingId ? "Update record" : "New record"}</p>
              <h2>{editingId ? "Edit student" : "Add a student"}</h2>
            </div>
            <span className="status-dot">Live</span>
          </div>

          <form className="student-form" onSubmit={save}>
            <label>
              <span>Full name</span>
              <input
                name="name"
                value={form.name}
                onChange={change}
                placeholder="e.g. Maya Sharma"
                required
                minLength="1"
                maxLength="100"
              />
            </label>
            <label>
              <span>Email address</span>
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={change}
                placeholder="maya@example.com"
                required
                maxLength="150"
              />
            </label>
            <label className="full-width">
              <span>Course</span>
              <input
                name="course"
                value={form.course}
                onChange={change}
                placeholder="e.g. Computer Science"
                required
                maxLength="100"
              />
            </label>
            <div className="form-actions full-width">
              <button className="primary-button" type="submit" disabled={saving}>
                {saving ? "Saving..." : editingId ? "Update student" : "Add student"}
              </button>
              {editingId && (
                <button className="secondary-button" type="button" onClick={reset}>Cancel</button>
              )}
            </div>
          </form>
          {message && <p className="success-message" role="status">{message}</p>}
          {error && <p className="error-message" role="alert">{error}</p>}
        </article>

        <article className="panel records-panel">
          <div className="records-header">
            <div>
              <p className="eyebrow">Directory</p>
              <h2>Student records</h2>
            </div>
            <label className="search-box">
              <span className="sr-only">Search students</span>
              <span aria-hidden="true">⌕</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search name, email or course"
              />
            </label>
          </div>

          {loading ? (
            <div className="empty-state" role="status">Loading student records...</div>
          ) : error && students.length === 0 ? (
            <div className="empty-state error-state" role="alert">{error}</div>
          ) : filteredStudents.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">✦</span>
              <strong>No students found</strong>
              <p>{search ? "Try a different search term." : "Add your first student to begin."}</p>
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Student</th>
                    <th>Course</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((student) => (
                    <tr key={student.id}>
                      <td><span className="id-badge">#{student.id}</span></td>
                      <td>
                        <strong>{student.name}</strong>
                        <span>{student.email}</span>
                      </td>
                      <td><span className="course-pill">{student.course}</span></td>
                      <td>
                        <div className="row-actions">
                          <button className="edit-button" onClick={() => edit(student)}>Edit</button>
                          <button className="delete-button" onClick={() => remove(student.id)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </article>
      </section>
    </main>
  );
}
