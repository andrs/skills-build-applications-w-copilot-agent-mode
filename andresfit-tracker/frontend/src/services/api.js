const BASE_URL = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `Request failed: ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  getUsers: () => request('/users/'),
  getUser: (id) => request(`/users/${id}`),
  createUser: (data) => request('/users/', { method: 'POST', body: JSON.stringify(data) }),
  deleteUser: (id) => request(`/users/${id}`, { method: 'DELETE' }),

  getActivities: () => request('/activities/'),
  createActivity: (data) => request('/activities/', { method: 'POST', body: JSON.stringify(data) }),
  deleteActivity: (id) => request(`/activities/${id}`, { method: 'DELETE' }),

  getTeams: () => request('/teams/'),
  createTeam: (data) => request('/teams/', { method: 'POST', body: JSON.stringify(data) }),
  deleteTeam: (id) => request(`/teams/${id}`, { method: 'DELETE' }),

  getLeaderboard: () => request('/leaderboard/'),

  getWorkouts: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/workouts/${qs ? `?${qs}` : ''}`)
  },
  createWorkout: (data) => request('/workouts/', { method: 'POST', body: JSON.stringify(data) }),
  deleteWorkout: (id) => request(`/workouts/${id}`, { method: 'DELETE' }),
}
