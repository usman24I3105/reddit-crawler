# Reddit Crawler - Worker Dashboard Frontend

A clean, simple React frontend for workers to manage Reddit posts.

## Features

- ✅ Login page with authentication
- ✅ Dashboard showing pending posts
- ✅ Post detail view
- ✅ Assign posts to yourself
- ✅ Reply to posts
- ✅ Clean, admin-style UI
- ✅ Mobile-friendly layout

## Tech Stack

- React 18
- Vite
- React Router
- Axios
- Tailwind CSS

## Setup

### Install Dependencies

```bash
npm install
```

### Configure API URL

Create a `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

### Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

## Usage

1. **Login**: Use any email/password (mock authentication for now)
2. **Dashboard**: View all pending Reddit posts
3. **View Post**: Click "View" to see post details
4. **Assign**: Click "Assign to Me" to claim a post
5. **Reply**: Write and submit a reply
6. **Auto-update**: Post status updates automatically

## API Integration

The frontend uses these backend endpoints:

- `GET /posts?status=pending` - Get pending posts
- `POST /posts/{id}/assign` - Assign post
- `POST /posts/{id}/reply` - Reply to post

## Project Structure

```
src/
 ├── api/
 │    └── client.js          # API client with axios
 ├── auth/
 │    └── AuthContext.jsx    # Authentication context
 ├── pages/
 │    ├── Login.jsx          # Login page
 │    ├── Dashboard.jsx      # Post list
 │    └── PostDetail.jsx     # Post detail & reply
 ├── components/
 │    ├── PostCard.jsx       # Post card component
 │    ├── Loader.jsx         # Loading spinner
 │    └── ReplyForm.jsx      # Reply form
 ├── App.jsx                 # Main app with routing
 └── main.jsx               # Entry point
```

## Authentication

Currently uses mock authentication. To implement real JWT:

1. Update `api.login()` in `src/api/client.js`
2. Update `get_current_worker()` in backend to validate JWT
3. Token is stored in localStorage

## Styling

Uses Tailwind CSS for all styling. Clean, minimal admin-style design.

## Browser Support

Modern browsers (Chrome, Firefox, Safari, Edge)





