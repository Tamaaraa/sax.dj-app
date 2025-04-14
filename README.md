# sax.dj

Web app inspired by plug.dj created with a Flask backend and Vue.js frontend. 
Users can join rooms, chat, and queue YouTube videos together.

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

---

### Running with Docker

Make sure to fill out both ".env.example" files (in the backend and frontend root folders), then remove ".example"

From the root of the repo
```bash
docker-compose up --build
```

This launches both frontend and backend using Docker Compose.

Frontend runs at: http://localhost:8080
Backend API at: http://localhost:5000

---

### Testing
End-to-End Tests
```bash
cd frontend
npm install
npx cypress install
npx cypress open
```
### Quality Checks

Backend Linting with Flake8:
```bash
pip install flake8
flake8 backend
```
Install pre-commit to enforce linting before commits.

pip install pre-commit
pre-commit install

### Local Development
Backend (Flask API)

```bash
cd backend
pip install -r requirements.txt
# change DEV_MODE in .env to 'true'
python ./app.py
```

Frontend (Vue)
```bash
cd frontend
npm install
npm run dev
```
