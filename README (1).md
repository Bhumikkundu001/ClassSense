# ClassSense — AI-Powered Classroom Attendance System

ClassSense is an AI-powered classroom attendance project designed to identify enrolled students from images and support attendance tracking and reporting. It combines a Python/FastAPI backend with a React frontend and a face-recognition pipeline.

## Live Demo

- **Frontend:** https://class-sense-alpha.vercel.app/
- **Backend:** https://classesense-backend.onrender.com/
- **API documentation:** https://classesense-backend.onrender.com/docs
- **Health check:** https://classesense-backend.onrender.com/health

> The frontend and backend are deployed separately. A hosted service may take a short time to wake up after inactivity.

## Technology Stack

### Backend and AI
- Python
- FastAPI and Uvicorn
- InsightFace
- ONNX Runtime
- OpenCV and NumPy
- Face embeddings and similarity-based matching

### Frontend
- React
- Vite
- JavaScript
- HTML and CSS

## Key Capabilities

- **Face recognition pipeline:** Detects faces and compares their embeddings against the enrolled-student database.
- **Student enrollment:** Builds a student database from enrollment images.
- **Attendance workflow:** Supports attendance-session creation and attendance processing through the backend.
- **Attendance reporting:** Includes CSV-based reporting in the Python project.
- **REST API:** Provides backend endpoints for frontend integration and API testing.
- **Web interface:** Offers a browser-based frontend connected to the deployed backend.

> Recognition results depend on image quality, lighting, face visibility, enrollment images, and the configured matching threshold. Review results before using them as an official attendance record.

## Project Structure

The project uses a Python package under `src/classesense` and a separate frontend application. The main folders and modules include:

```text
ClassSense/
├── src/
│   └── classesense/
│       ├── backend/
│       │   └── main.py
│       ├── detector.py
│       ├── enrollment.py
│       ├── recognizer.py
│       ├── attendance.py
│       ├── reporting.py
│       └── services/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

The exact files in your local checkout may differ as the project evolves.

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Bhumikkundu001/ClassSense.git
cd ClassSense
```

### 2. Create and activate a Python virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the Python executable in the virtual environment directly or follow your machine's Python environment policy.

### 3. Install backend dependencies

Install the packages listed in the repository's dependency file, if present. For example, if the repository contains `requirements.txt`:

```powershell
pip install -r requirements.txt
```

If the dependency file has a different name, use that file instead.

### 4. Start the backend

From the repository root:

```powershell
python -m uvicorn classesense.backend.main:app --reload --app-dir src
```

The local API should be available at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` to inspect and test the API.

### 5. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite will print the local frontend URL, usually `http://localhost:5173`.

For local development, ensure the frontend's API base URL and the backend's CORS allowlist match your local URLs. The deployed frontend uses the hosted backend URL configured in the frontend source.

## API Endpoints

The backend has included the following routes during development:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API documentation |
| `POST` | `/auth/register` | User registration |
| `POST` | `/auth/login` | User login |
| `POST` | `/attendance` | Attendance workflow |

Use the live `/docs` page as the source of truth for the current deployed API schema and request fields.

## Deployment

- **Frontend hosting:** Vercel
- **Backend hosting:** Render
- The frontend must call the deployed backend API URL.
- The backend CORS configuration must allow the frontend's exact origin: `https://class-sense-alpha.vercel.app`.
- After pushing backend changes to the connected GitHub branch, confirm that the Render deployment has completed successfully before testing the website.

## Development Notes

- The backend defers loading the InsightFace detector until it is needed to reduce startup memory usage.
- AI model initialization and inference can require substantially more memory than a basic API health check. A successful health check does not necessarily prove that a face-recognition request will fit within the hosting service's memory limits.
- Do not commit secrets, production passwords, API keys, or private student images to the repository.
- Use appropriate consent, access controls, and data-retention practices when handling face images or attendance records.

## Troubleshooting

### Frontend shows “Failed to fetch”
1. Open the backend health check: https://classesense-backend.onrender.com/health
2. Confirm the latest Render deployment is live.
3. Check the browser developer tools' **Console** and **Network** tabs for the exact request error.
4. Verify that the frontend API base URL points to the deployed backend and that the backend CORS allowlist contains the exact Vercel origin.
5. If only recognition requests fail, inspect the Render logs for memory or model-initialization errors.

### Backend is slow on the first request
A free hosting service may need to wake up after inactivity, and AI model initialization can add delay to the first recognition request.

### Face recognition does not identify a student
Check that enrollment images are available, faces are clearly visible, and lighting and image quality are adequate. Review the matching threshold and recognition logs before changing production settings.

## Current Project Status

The frontend and backend have been deployed separately, and the frontend API URL and backend CORS configuration have been updated for the deployed frontend. Verify the live login and attendance workflows after each deployment; deployment success alone does not confirm that every workflow is working.

## License

No license is specified here. Add a `LICENSE` file and update this section if you decide to distribute the project under a particular license.
