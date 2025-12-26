# Frontend Setup Instructions

## Quick Start

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API URL (optional):**
   ```bash
   cp .env.example .env
   # Edit .env if your backend runs on different port
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   ```
   http://localhost:3000
   ```

## Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

## Development

The frontend runs on port 3000 and proxies API requests to the backend.

## Production Build

```bash
npm run build
```

Output will be in `dist/` directory.

## Troubleshooting

### API Connection Issues

- Ensure backend is running on http://localhost:8000
- Check browser console for CORS errors
- Verify `VITE_API_URL` in `.env` matches your backend URL

### Authentication Issues

- Currently uses mock authentication
- Any email/password will work for login
- Token is stored in localStorage

### Posts Not Loading

- Check backend logs for errors
- Verify `/posts?status=pending` endpoint works
- Check browser network tab for failed requests





