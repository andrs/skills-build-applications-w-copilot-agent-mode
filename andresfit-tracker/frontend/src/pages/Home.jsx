export default function Home() {
  return (
    <div className="text-center">
      <img src="/octofitapp-small.png" alt="AndresFit Logo" width="120" className="mb-3" />
      <h1>AndresFit Tracker</h1>
      <p className="lead">Track your fitness, compete with friends, and reach your goals.</p>
      <div className="row mt-4 g-3 justify-content-center">
        {[
          { title: 'Activities', desc: 'Log running, walking, and strength workouts' },
          { title: 'Teams', desc: 'Create teams and train together' },
          { title: 'Leaderboard', desc: 'See who tops the charts' },
          { title: 'Workouts', desc: 'Get personalized workout suggestions' },
        ].map(({ title, desc }) => (
          <div className="col-md-3" key={title}>
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">{title}</h5>
                <p className="card-text">{desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
