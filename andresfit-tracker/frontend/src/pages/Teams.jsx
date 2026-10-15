import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function Teams() {
  const [teams, setTeams] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [form, setForm] = useState({ name: '', description: '', member_ids: [] })

  const load = () => {
    setLoading(true)
    Promise.all([api.getTeams(), api.getUsers()])
      .then(([t, u]) => { setTeams(t); setUsers(u) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError(null)
    api.createTeam({ ...form, member_ids: form.member_ids.map(Number) })
      .then(() => { setForm({ name: '', description: '', member_ids: [] }); load() })
      .catch((err) => setError(err.message))
  }

  const toggleMember = (id) => {
    setForm((prev) => ({
      ...prev,
      member_ids: prev.member_ids.includes(id)
        ? prev.member_ids.filter((m) => m !== id)
        : [...prev.member_ids, id],
    }))
  }

  const handleDelete = (id) => {
    api.deleteTeam(id).then(load).catch((err) => setError(err.message))
  }

  if (loading) return <p>Loading teams...</p>

  return (
    <div>
      <h2>Teams</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit} className="row g-2 mb-3 align-items-end">
        <div className="col-auto">
          <input className="form-control" placeholder="Team Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        </div>
        <div className="col-auto">
          <input className="form-control" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <div className="col-auto">
          <div className="dropdown">
            <button className="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
              Members ({form.member_ids.length})
            </button>
            <ul className="dropdown-menu p-2">
              {users.map((u) => (
                <li key={u.id}>
                  <label className="dropdown-item">
                    <input type="checkbox" className="me-2" checked={form.member_ids.includes(u.id)} onChange={() => toggleMember(u.id)} />
                    {u.username}
                  </label>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="col-auto">
          <button className="btn btn-primary" type="submit">Create Team</button>
        </div>
      </form>
      <div className="row g-3">
        {teams.map((t) => (
          <div className="col-md-4" key={t.id}>
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">{t.name}</h5>
                <p className="card-text">{t.description}</p>
                <p className="mb-1"><strong>Members:</strong></p>
                <ul className="list-unstyled ms-2">
                  {t.members.map((m) => <li key={m.id}>{m.full_name}</li>)}
                </ul>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(t.id)}>Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
