# Student Dictionary Frontend — React + TypeScript + Vite

**Purpose:** Hour 4 frontend for the existing Student Dictionary Flask API. This is a working source project, **not a new standalone backend**. Runs locally on **Windows 10 or 11** during Hour 4; public EC2 deployment is Hour 5.

## Folder structure

| File | What it does |
|---|---|
| `index.html` | Browser page and root element |
| `src/main.tsx` | React entry point |
| `src/App.tsx` | Student CRUD interface, API calls and error handling |
| `src/style.css` | Responsive styling |
| `vite.config.ts` | Proxies requests beginning `/api` to local Flask port 5000 |
| `package.json` | Dependency versions and scripts |
| `tsconfig*.json` | TypeScript configuration |

## Start from Windows PowerShell

**Prerequisites:** Install Node.js **20.19+ or 22.12+** (prefer current LTS), pnpm, and Python. Have the existing repository checked out. Do **not** run these commands in the Ubuntu EC2 SSH terminal.

**Terminal A — Flask backend:**

```powershell
cd "$HOME\AWS_DEPLOYMENT_6_HOUR\studentdictionary"
if (!(Test-Path .venv)) { py -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
# For this local Windows lab, use DATABASE_URL=sqlite:///students.db in .env
.\.venv\Scripts\python.exe -m flask --app app db upgrade
.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000
```

Check from a separate terminal: `curl.exe -i http://127.0.0.1:5000/api/v1/students` (expect **HTTP 200**).

**Terminal B — React:**

```powershell
cd "$HOME\AWS_DEPLOYMENT_6_HOUR\studentdictionary\frontend"

# First install generates pnpm-lock.yaml; commit it to the repository.
pnpm install

# Run React + Vite
pnpm dev
```

Open the URL printed by Vite, generally **http://localhost:5173/**. Flask should remain running in Terminal A.

## Try the frontend

1. Enter a student name, whole-number age and optional email; choose **Add student**.
2. Verify the new record appears under **Saved students**.
3. Choose **Edit**, modify the data and **Save changes**.
4. Choose **Delete** and confirm. Only the selected student should be removed.
5. Refresh the browser: records persist because Flask stores them in the database.
6. Open browser developer tools (**F12 → Network → Fetch/XHR**) and inspect **GET 200**, **POST 201**, **PUT 200**, and **DELETE 200** requests for `/api/v1/students`.

## Build

```powershell
# Stop Vite with Ctrl+C first; then:
pnpm build
Get-ChildItem dist
```

`pnpm build` runs TypeScript checks and Vite's production build. The generated `dist/` folder is the output for Hour 5 deployment. **Vite preview does not use the dev proxy**, so run `pnpm dev` for local API integration testing.

## Important security and scope notes

- No login or authentication: the *existing* Student Dictionary backend has no auth API; do not invent one to mimic the superseded starter.
- Use **test student data** only. Frontend and backend are not secured for public use.
- Do not commit `.env`, credentials, keys or `node_modules/`.
- The React dev server on Windows does **not** connect directly to EC2 PostgreSQL. Its browser requests go through the local Vite proxy to local Flask.
- This source has not yet passed a dependency-install/build validation in the current editing environment; the workflow and learner build must confirm it.

## Official documentation

- [React Learn](https://react.dev/learn)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Vite Getting Started](https://vite.dev/guide/)
- [Vite server proxy](https://vite.dev/config/server-options#server-proxy)
- [pnpm Installation](https://pnpm.io/installation)
