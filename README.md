# Enterprise ITSM – Intelligent IT Operations & Support Management Platform

A production-grade, enterprise IT Service Management (ITSM) and IT Operations platform built to simulate a Fortune 500 company's internal IT operations department. Engineered with a modular monolithic architecture, clean REST API, database-driven business intelligence, infrastructure APM telemetry, and cybersecurity operations.

---

## Architecture Overview

```
                      ┌───────────────────────────────────────────────┐
                      │          React 18 + Tailwind CSS +            │
                      │      Recharts Executive Ops Dashboard         │
                      └───────────────────────┬───────────────────────┘
                                              │ Axios (JWT + Refresh Rotation)
                                              ▼
                      ┌───────────────────────────────────────────────┐
                      │            FastAPI REST API (v1)              │
                      │  - Argon2 Password Hashing & Account Lockout  │
                      │  - 6-Tier Role-Based Access Control (RBAC)    │
                      │  - Resource-Level Ticket Isolation            │
                      │  - Declarative Workflow Automation Engine     │
                      │  - Configurable SLA Policy Matrix Engine      │
                      └───────┬───────────────────────────────┬───────┘
                              │                               │
                              ▼                               ▼
       ┌──────────────────────────────┐              ┌────────────────────────┐
       │   PostgreSQL / SQLite        │              │  Redis & Celery Queue  │
       │   Normalized ITSM Database   │              │  Background Tasks      │
       └──────────────────────────────┘              └────────────────────────┘
```

---

## 1. Technology Stack

### Backend
- **Python 3.11+ / 3.14**
- **FastAPI**: Modern, high-performance web framework for APIs.
- **SQLAlchemy 2.0**: Relational ORM with connection pooling and eager joining.
- **Pydantic V2**: Robust request validation and response schemas.
- **PostgreSQL 16**: Normalized production database (with automatic fallback to SQLite for local zero-dependency testing).
- **Alembic**: Database migrations framework.
- **Redis & Celery**: Distributed asynchronous task processing and scheduled jobs.
- **Argon2id & PyJWT**: Cryptographic password hashing and secure refresh-token rotation.

### Frontend
- **React 18**: Component-driven SPA with React Router v6.
- **Tailwind CSS**: Modern enterprise theme with glassmorphic panels and dark-mode ergonomics.
- **Axios**: HTTP client with automatic refresh-token rotation interceptors.
- **Recharts**: Database-driven analytics, area velocity trends, and priority distribution charts.
- **Lucide React**: Clean enterprise iconography.

### DevOps & Testing
- **Docker & Docker Compose**: Multi-container orchestration (DB, Redis, Backend, Celery, Frontend).
- **GitHub Actions**: Continuous Integration pipeline for automated Pytest suite and Vite bundle compilation.
- **Pytest**: Automated test suite with 100% pass rate across RBAC, SLA calculations, and auth workflows.
- **Swagger / OpenAPI**: Interactive documentation at `/docs` and `/redoc`.
- **Postman Collection**: Exported API collection at `docs/postman_collection.json`.

---

## 2. Six Enterprise User Roles & Pre-Seeded Personas

The platform includes a **1-Click Persona Switcher** in the top navigation bar to test permission boundaries immediately:

| Role | Username | Password | Key Responsibilities & Access Boundary |
|---|---|---|---|
| **System Administrator** | `admin` | `Admin123!` | Global administration, user management, department config, audit logs, system-wide reports. |
| **IT Operations Manager** | `sarah.manager` | `Manager123!` | Supervise IT operations, approve/reject Change Requests (CAB), monitor SLA, manage major incidents. |
| **IT Support Technician** | `alex.tech` | `Tech123!` | Triage tickets, update progress, internal technician notes, resolve incidents, manage asset maintenance. |
| **Employee** | `john.employee` | `User123!` | Submit IT requests, view personal company assets, confirm ticket resolutions (**strictly isolated from viewing other employees' tickets**). |
| **Security Analyst** | `elena.sec` | `Security123!` | Investigate cybersecurity threats, attach IOC evidence, containment actions, manage security dashboards. |
| **Auditor** | `marcus.audit` | `Auditor123!` | Read-only compliance access to immutable audit records, ticket histories, and change approval records. |

---

## 3. Core Business Modules

### Module A: Advanced Service Desk
- **Configurable Priority Matrix**: Priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) is computed from an Impact $\times$ Urgency matrix.
- **Full Lifecycle**: `NEW` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `PENDING_USER` $\rightarrow$ `RESOLVED` $\rightarrow$ `CLOSED` $\rightarrow$ `CANCELLED`.
- **Ticket Reopening & Escalation**: Tracks reopen counts and increases escalation tiers.
- **Internal vs. Public Notes**: Technicians can post confidential troubleshooting steps hidden from employees.
- **File Attachments & Timeline**: Upload log files, screenshots, and view full immutable history.

### Module B: Incident Management
- **Major Incident Command**: Declares P1/P2 major incidents with active visual banners.
- **Parent-Child Correlation**: Link 100+ employee support tickets to one major infrastructure outage.
- **Root Cause Analysis (RCA)**: Formal tracking of root causes, immediate workarounds, and permanent solutions.
- **Problem Records & Known Error Database (KEDB)**: Searchable database of verified workarounds.

### Module C: IT Asset & CMDB Management
- **Configuration Items (CI)**: Manage Laptops, Servers, Routers, Switches, Mobile Devices, Cloud Services.
- **Software License Tracking**: Seat utilization gauges and expiration warnings.
- **CMDB Topology Dependency Visualizer**: Interactive mapping of `DEPENDS_ON`, `HOSTS`, and `CONNECTS_TO` CI relationships.
- **Employee Personal Inventory**: Employees can view their assigned devices and warranty statuses.

### Module D: IT Change Management (CAB)
- **Change Types**: Standard (pre-approved), Normal (CAB review), Emergency (expedited).
- **Risk Assessment**: Mandatory business justification, implementation plan, test procedure, and rollback plan.
- **Approval Workflow**: IT Operations Manager CAB decision portal with approval/rejection logging.

### Module E: Cybersecurity Operations (SecOps)
- **Threat Categories**: Phishing, Malware, Suspicious Logins, Unauthorized Access, Data Exposure, Compromised Accounts.
- **Forensic Evidence & IOCs**: SHA-256 hash calculation, email headers, log file attachments.
- **Containment Protocols**: Document quarantine actions, gateway domain blocks, and credential resets.
- **SecOps Dashboard**: Real-time distribution of threat severities and active investigations.

### Module F: Knowledge Management
- **Searchable Solutions**: Instant keyword filtering across articles, tags, and categories.
- **Helpfulness Feedback**: Real-time employee up/down voting (`+48 helpful`).
- **Standard Operating Procedures (SOP)**: Markdown formatted guides for remote work and troubleshooting.

### Module G: SLA & Service Performance Engine
- **Target Calculation**: Configurable response and resolution deadlines per priority tier.
- **SLA Clock Pausing**: Clocks automatically pause when tickets enter `PENDING_USER` state and resume with extended deadlines.
- **Compliance Metrics**: Live calculation of SLA breach percentage and average resolution hours.

### Module H: Infrastructure APM Monitoring
- **Live Device Telemetry**: Real-time CPU, RAM, Disk, and Ping latency gauges.
- **Synthetic Pulse**: Simulated background telemetry pulses.
- **External Webhooks**: Ingestion endpoints for **Prometheus Alertmanager** and **Zabbix** with automated incident creation on threshold breaches.

### Module I: Workflow Automation Engine
- **Declarative Pipeline**: `TRIGGER` $\rightarrow$ `CONDITIONS` $\rightarrow$ `ACTIONS`.
- **Rules Pre-configured**:
  1. *Critical Ticket Notification*: Instantly alerts the IT Manager upon P1 submission.
  2. *Employee Resolution Confirmation*: Prompts requester upon ticket resolution.
- **Execution Log Inspector**: Diagnostic history of all automated rule evaluations.

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- (Optional) Docker & Docker Compose

### Option A: Local Development Setup (Quickest)

#### 1. Backend Setup
```bash
# From repository root
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```
Backend runs at `http://localhost:8000`. Swagger API documentation is available at `http://localhost:8000/docs`.

#### 2. Frontend Setup
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`.

---

### Option B: Docker Compose Deployment

```bash
docker-compose up --build
```
This launches:
- `itsm_postgres`: PostgreSQL 16 on port 5432
- `itsm_redis`: Redis 7 on port 6379
- `itsm_backend`: FastAPI on port 8000
- `itsm_celery_worker`: Celery background worker
- `itsm_frontend`: React + Nginx on port 80 / 5173

---

## 5. Running Automated Tests

```bash
# From repository root (with venv activated)
$env:PYTHONPATH="backend"  # Windows PowerShell
pytest backend/tests -v
```

All 10 test suites validate:
- System health and database readiness
- Argon2 login and invalid credential rejection
- Secure refresh token rotation and revocation
- RBAC role restrictions across endpoints
- Employee resource-level ticket isolation
- Dynamic impact $\times$ urgency priority matrix calculation
- Ticket status lifecycle transitions and technician assignment
