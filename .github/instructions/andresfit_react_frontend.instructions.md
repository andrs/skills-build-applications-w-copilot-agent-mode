---
applyTo: "andresfit-tracker/frontend/**"
---
# AndresFit Tracker React Presentation Tier Guidelines

Use commands that target `andresfit-tracker/frontend` without changing directories.

```bash
npm create vite@latest andresfit-tracker/frontend -- --template react
npm install --prefix andresfit-tracker/frontend
npm install bootstrap react-router-dom --prefix andresfit-tracker/frontend
```

Add Bootstrap CSS import at the top of `andresfit-tracker/frontend/src/main.jsx`.

## Images

Use an app logo stored under `andresfit-tracker/frontend/src/assets/` and import it
in the navbar/header component.
