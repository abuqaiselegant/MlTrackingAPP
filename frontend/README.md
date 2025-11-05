# ML Experiment Tracker - Frontend

Next.js 14 frontend for the ML Experiment Tracking Platform.

## Quick Start

```bash
npm install
npm run dev
```

Visit **http://localhost:3000**

## Features

- 📊 Dashboard with experiment filtering
- ➕ Create new experiments
- 📈 Interactive metrics charts
- 📦 Artifact management
- 🎨 Modern UI with shadcn/ui

## Tech Stack

- Next.js 14 + TypeScript
- Tailwind CSS
- shadcn/ui components
- TanStack Query
- Recharts
- Axios

## Environment

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Pages

- `/` - Dashboard (experiments list)
- `/experiments/new` - Create experiment
- `/experiments/[id]` - Experiment details (overview, metrics, artifacts)

Make sure the backend is running at http://localhost:8000
