import { useEffect, useState } from 'react'
import { api } from '../services/api'

const DIFFICULTIES = ['beginner', 'intermediate', 'advanced']
const TYPES = ['running', 'walking', 'strength']

export default function Workouts() {
  const [workouts, setWorkouts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState({ difficulty: '', activity_type: '' })
  const [form, setForm] = useState({ name: '', description: '', activity_type: 'running', duration_minutes: '', difficulty: 'beginner' })

  const load = (params = filter) => {
    setLoading(true)
    const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v))
    api.getWorkouts(clean)
      .then(setWorkouts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => load(), [])

  const handleFilter = (key, value) => {
    const next = { ...filter, [key]: value }
    setFilter(next)
    load(next)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError(null)
    api.createWorkout({ ...form, duration_minutes: Number(form.duration_minutes) })
      .then(() => { setForm({ name: '', description: '', activity_type: 'running', duration_minutes: '', difficulty: 'beginner' }); load() })
      .catch((err) => setError(err.message))
  }

  const handleDelete = (id) => {
    api.deleteWorkout(id).then(() => load()).catch((err) => setError(err.message))
  }

  return (
    <div>
      <h2>Workout Suggestions</h2>
      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row g-2 mb-3">
        <div className="col-auto">
          <select className="form-select" value={filter.difficulty} onChange={(e) => handleFilter('difficulty', e.target.value)}>
            <option value="">All Difficulties</option>
            {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <div className="col-auto">
          <select className="form-select" value={filter.activity_type} onChange={(e) => handleFilter('activity_type', e.target.value)}>
            <option value="">All Types</option>
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="row g-2 mb-3">
        <div className="col-auto">
          <input className="form-control" placeholder="Workout Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        </div>
        <div className="col-auto">
          <input className="form-control" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <div className="col-auto">
          <select className="form-select" value={form.activity_type} onChange={(e) => setForm({ ...form, activity_type: e.target.value })}>
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div className="col-auto">
          <input className="form-control" type="number" placeholder="Duration (min)" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} required min="1" />
        </div>
        <div className="col-auto">
          <select className="form-select" value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value })}>
            {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <div className="col-auto">
          <button className="btn btn-primary" type="submit">Add Workout</button>
        </div>
      </form>

      {loading ? <p>Loading workouts...</p> : (
        <div className="row g-3">
          {workouts.map((w) => (
            <div className="col-md-4" key={w.id}>
              <div className="card">
                <div className="card-body">
                  <h5 className="card-title">{w.name}</h5>
                  <p className="card-text">{w.description}</p>
                  <span className="badge bg-info me-1">{w.activity_type}</span>
                  <span className="badge bg-secondary me-1">{w.difficulty}</span>
                  <span className="badge bg-dark">{w.duration_minutes} min</span>
                  <div className="mt-2">
                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(w.id)}>Delete</button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
