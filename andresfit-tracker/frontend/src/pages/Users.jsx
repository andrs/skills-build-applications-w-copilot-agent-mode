import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [form, setForm] = useState({ username: '', email: '', full_name: '' })

  const load = () => {
    setLoading(true)
    api.getUsers()
      .then(setUsers)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError(null)
    api.createUser(form)
      .then(() => { setForm({ username: '', email: '', full_name: '' }); load() })
      .catch((err) => setError(err.message))
  }

  const handleDelete = (id) => {
    api.deleteUser(id).then(load).catch((err) => setError(err.message))
  }

  if (loading) return <p>Loading users...</p>

  return (
    <div>
      <h2>Users</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit} className="row g-2 mb-3">
        <div className="col-auto">
          <input className="form-control" placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
        </div>
        <div className="col-auto">
          <input className="form-control" placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        </div>
        <div className="col-auto">
          <input className="form-control" placeholder="Full Name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
        </div>
        <div className="col-auto">
          <button className="btn btn-primary" type="submit">Add User</button>
        </div>
      </form>
      <table className="table table-striped">
        <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Full Name</th><th></th></tr></thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.email}</td>
              <td>{u.full_name}</td>
              <td><button className="btn btn-sm btn-danger" onClick={() => handleDelete(u.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
