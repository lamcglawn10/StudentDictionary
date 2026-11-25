import { useEffect, useState, type FormEvent } from "react";

// These fields match the JSON returned by the existing Flask API.
type Student = { id: number; name: string; age: number; email: string };
type StudentInput = Omit<Student, "id">;
const apiUrl = "/api/v1/students";

async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, options);
  if (!response.ok) {
    const message = `HTTP ${response.status}: request failed`;
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

const jsonRequest = (method: "POST" | "PUT", data: StudentInput): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});

export default function App() {
  const [students, setStudents] = useState<Student[]>([]);
  const [name, setName] = useState("");
  const [age, setAge] = useState("18");
  const [email, setEmail] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function loadStudents() {
    setStudents(await apiRequest<Student[]>(apiUrl));
  }

  useEffect(() => {
    let active = true;
    // Stop updating the component if the learner navigates away while loading.
    apiRequest<Student[]>(apiUrl)
      .then(data => { if (active) setStudents(data); })
      .catch(err => { if (active) setError(err instanceof Error ? err.message : "Could not load students"); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  function resetForm() {
    setName("");
    setAge("18");
    setEmail("");
    setEditingId(null);
  }

  function editStudent(student: Student) {
    setEditingId(student.id);
    setName(student.name);
    setAge(String(student.age));
    setEmail(student.email);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function submitStudent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedAge = Number(age);
    if (!name.trim() || !age.trim() || !Number.isInteger(normalizedAge) || normalizedAge < 0 || normalizedAge > 150) {
      setError("Enter a name and a whole-number age between 0 and 150.");
      return;
    }
    setBusy(true);
    setError("");
    const student: StudentInput = { name: name.trim(), age: normalizedAge, email: email.trim() };
    try {
      if (editingId === null) {
        await apiRequest<Student>(apiUrl, jsonRequest("POST", student));
      } else {
        await apiRequest<Student>(`${apiUrl}/${editingId}`, jsonRequest("PUT", student));
      }
      await loadStudents();
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save the student");
    } finally {
      setBusy(false);
    }
  }

  async function removeStudent(student: Student) {
    if (!window.confirm(`Delete ${student.name}? This cannot be undone.`)) return;
    setBusy(true);
    setError("");
    try {
      await apiRequest<{ message: string }>(`${apiUrl}/${student.id}`, { method: "DELETE" });
      await loadStudents();
      if (editingId === student.id) resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete the student");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <header className="page-header">
        <p className="eyebrow">AWS DEPLOYMENT COURSE · HOUR 4</p>
        <h1>Student Dictionary</h1>
        <p>Manage student records through our React frontend and Flask API.</p>
      </header>

      <section aria-labelledby="student-form-heading">
        <h2 id="student-form-heading">{editingId === null ? "Add a student" : "Edit student"}</h2>
        <form onSubmit={submitStudent}>
          <div className="form-grid">
            <label>Full name <input required maxLength={120} value={name} onChange={event => setName(event.target.value)} placeholder="e.g. Aaron" /></label>
            <label>Age <input required type="number" min={0} max={150} step={1} value={age} onChange={event => setAge(event.target.value)} /></label>
            <label>Email (optional) <input type="email" maxLength={254} value={email} onChange={event => setEmail(event.target.value)} placeholder="student@example.com" /></label>
          </div>
          <div className="actions">
            <button disabled={busy} type="submit">{busy ? "Saving…" : editingId === null ? "Add student" : "Save changes"}</button>
            {editingId !== null && <button disabled={busy} className="secondary" type="button" onClick={resetForm}>Cancel</button>}
          </div>
        </form>
      </section>

      {error && <p role="alert" className="error">Error: {error}. Check that Flask is running on port 5000.</p>}
      <section aria-labelledby="student-list-heading">
        <div className="section-heading">
          <h2 id="student-list-heading">Saved students</h2>
          <button className="secondary" type="button" disabled={busy || loading} onClick={() => { setError(""); void loadStudents().catch(err => setError(String(err))); }}>Refresh</button>
        </div>
        {loading ? <p role="status">Loading students…</p> : students.length === 0 ? <p>No students yet. Add your first student above.</p> : (
          <ul className="student-list">
            {students.map(student => (
              <li key={student.id} className="student">
                <div><strong>{student.name}</strong><span>Age {student.age}{student.email ? ` · ${student.email}` : ""}</span></div>
                <div className="actions"><button className="secondary" type="button" disabled={busy} onClick={() => editStudent(student)}>Edit</button><button className="danger" type="button" disabled={busy} onClick={() => void removeStudent(student)}>Delete</button></div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
