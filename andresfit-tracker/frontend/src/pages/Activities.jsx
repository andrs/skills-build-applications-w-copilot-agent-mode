import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function Activities() {
  const [activities, setActivities] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [form, setForm] = useState({ user_id: '', activity_type: 'running', duration_minutes: '', calories_burned: '' })

  const load = () => {
    setLoading(true)
    Promise.all([api.getActivities(), api.getUsers()])
      .then(([a, u]) => { setActivities(a); setUsers(u) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError(null)
    api.createActivity({
      ...form,
      user_id: Number(form.user_id),
      duration_minutes: Number(form.duration_minutes),
      calories_burned: Number(form.calories_burned),
    })
      .then(() => { setForm({ user_id: '', activity_type: 'running', duration_minutes: '', calories_burned: '' }); load() })
      .catch((err) => setError(err.message))
  }

  const handleDelete = (id) => {
    api.deleteActivity(id).then(load).catch((err) => setError(err.message))
  }

  if (loading) return <p>Loading activities...</p>

  return (
    <div>
      <h2>Activities</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit} className="row g-2 mb-3">
        <div className="col-auto">
          <select className="form-select" value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })} required>
            <option value="">Select User</option>
            {users.map((u) => <option key={u.id} value={u.id}>{u.username}</option>)}
          </select>
        </div>
        <div className="col-auto">
          <select className="form-select" value={form.activity_type} onChange={(e) => setForm({ ...form, activity_type: e.target.value })}>
            <option value="running">Running</option>
            <option value="walking">Walking</option>
            <option value="strength">Strength</option>
          </select>
        </div>
        <div className="col-auto">
          <input className="form-control" type="number" placeholder="Duration (min)" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} required min="1" />
        </div>
        <div className="col-auto">
          <input className="form-control" type="number" placeholder="Calories" value={form.calories_burned} onChange={(e) => setForm({ ...form, calories_burned: e.target.value })} required min="1" />
        </div>
        <div className="col-auto">
          <button className="btn btn-primary" type="submit">Log Activity</button>
        </div>
      </form>
      <table className="table table-striped">
        <thead><tr><th>ID</th><th>User</th><th>Type</th><th>Duration</th><th>Calories</th><th>Date</th><th></th></tr></thead>
        <tbody>
          {activities.map((a) => (
            <tr key={a.id}>
              <td>{a.id}</td>
              <td>{users.find((u) => u.id === a.user_id)?.username || a.user_id}</td>
              <td>{a.activity_type}</td>
              <td>{a.duration_minutes} min</td>
              <td>{a.calories_burned}</td>
              <td>{new Date(a.date).toLocaleDateString()}</td>
              <td><button className="btn btn-sm btn-danger" onClick={() => handleDelete(a.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
