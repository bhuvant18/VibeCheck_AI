# VibeCheck AI - React Frontend

Modern React frontend for the VibeCheck AI Hallucination Detector.

## Features

- 🎨 Modern, responsive UI with dark theme
- 🔍 Real-time text analysis
- ✅ Color-coded claim verification (green = verified, red = hallucination)
- 📊 Live statistics dashboard
- 🔧 One-click auto-fix for hallucinations
- ⚡ Built with React + Vite for blazing fast performance

## Prerequisites

- Node.js 18+ 
- Backend API running on http://localhost:8000

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:3000

## Build for Production

```bash
npm run build
npm run preview
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`.
Make sure the backend is running before starting the frontend.

## Project Structure

```
src/
├── components/
│   ├── Header.jsx          # App header with branding
│   ├── TextInput.jsx       # Text input and action buttons
│   ├── Stats.jsx           # Statistics dashboard
│   └── ClaimCard.jsx       # Individual claim display
├── api.js                  # API service layer
├── App.jsx                 # Main app component
└── main.jsx               # React entry point
```

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **CSS Modules** - Styling
