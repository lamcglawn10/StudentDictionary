# Student Dictionary — Hour 6 Deployment Evidence Tracker

This file is a template, **not evidence of passing tests**. Record real GitHub Actions run links and EC2 output after execution; never include secrets or real student data.

| Gate | Verification | Expected | Actual status |
| --- | --- | --- | --- |
| Backend CI | GitHub Actions: `backend-tests` | Python tests pass, migration succeeds | Not verified |
| Frontend CI | GitHub Actions: `frontend-build` | TypeScript + Vite build pass, `dist/index.html` exists | Not verified |
| Trigger | Small commit to `studentdictionary/` | CI starts automatically | Not verified |
| Artifact | `studentdictionary-react-dist` | Compiled HTML/assets, no secrets | Not verified |
| Deployment connectivity | Approved runner-to-EC2 SSH path | Trusted host + key login | Not configured/verified |
| Manual release | `deploy_to_ec2=true` on `main` | Gated release runs only after both CI jobs pass | Not verified |
| EC2 service | `sudo systemctl is-active student-dictionary` | active | Not verified |
| Nginx service | `sudo systemctl is-active nginx` | active | Not verified |
| Public site | `curl.exe -I http://EC2_PUBLIC_IP/` from allowed IP | HTTP 200 React page | Not verified |
| Public API | `curl.exe -i http://EC2_PUBLIC_IP/api/v1/students` | HTTP 200 JSON | Not verified |
| Database | Read existing test student after service restart | Row persists | Not verified |
| Recovery | Inspect backups/rollback plan | Backup paths and DB migration limitation understood | Not verified |

**Evidence to capture:** Workflow URL, source commit SHA, execution date, abbreviated logs with credentials removed, observed HTTP status codes, and any failures. Never upload `.env`, SSH keys, database URLs containing passwords, or credentials.

**Deployment design:** A manually triggered workflow deploys CI-generated artifacts. A remote EC2 release script backs up files and static assets, then runs migration and smoke checks. Its rollback does **not reverse database schema migrations**.

**Known constraint:** EC2 SSH restricted to Aaron's `My IP` will block a GitHub-hosted runner. An approved static-address or private-network deployment path is required; do not open SSH to everyone.
