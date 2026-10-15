import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function Leaderboard() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getLeaderboard()
      .then(setEntries)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading leaderboard...</p>
  if (error) return <div className="alert alert-danger">{error}</div>

  return (
    <div>
      <h2>Leaderboard</h2>
      {entries.length === 0 ? (
        <p className="text-muted">No activity data yet. Log some activities to see the leaderboard!</p>
      ) : (
        <table className="table table-striped">
          <thead>
            <tr><th>Rank</th><th>User</th><th>Activities</th><th>Total Duration</th><th>Total Calories</th></tr>
          </thead>
          <tbody>
            {entries.map((e, i) => (
              <tr key={e.user.id} className={i === 0 ? 'table-warning fw-bold' : ''}>
                <td>{i + 1}</td>
                <td>{e.user.full_name}</td>
                <td>{e.activity_count}</td>
                <td>{e.total_duration} min</td>
                <td>{e.total_calories}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
