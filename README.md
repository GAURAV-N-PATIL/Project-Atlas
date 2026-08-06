# Project Atlas - Getting Started

**Cloud Storage Platform** inspired by Google Drive / Dropbox.

## What you're building
A web app where users sign up, upload files/folders, organize them, preview them, and share them with others via secure links - with permissions, versioning, and multi-device sync concepts.

## Why this project is a great beginner-to-intermediate pick
It touches almost every core backend skill at once: auth, file I/O, databases, storage abstraction, and API design - while staying scoped enough to finish in a few sprints.

## Learning outcomes
- Designing REST APIs with authentication (JWT/session-based)
- Object storage concepts (buckets, keys, presigned URLs) vs. traditional file storage
- Relational modeling for hierarchical data (folders inside folders)
- Access control (owner, shared-with, public-link, read/write roles)
- Chunked/large file uploads and progress tracking on the frontend

## Prerequisites
- Basic JavaScript/TypeScript and Python
- Comfortable with HTTP concepts (verbs, status codes, headers)
- A GitHub account for version control

## How to use this doc
This is a multi-page guide - use the sidebar to move between **Architecture**, **Tech Stack**, **Learning Resources**, **Features & API**, and the **Kanban Roadmap**. Read them in order the first time.

---PAGE_BREAK---

# Architecture & Requirements

## Step 1 - Define requirements before touching code

### Functional requirements
- User registration/login (email+password, optionally OAuth)
- Create/rename/delete/move folders and files
- Upload files (single + multiple, drag-and-drop, progress bar)
- Download files, preview common types (images, PDF, text)
- Trash/restore (soft delete)
- Share a file/folder via link (public or "specific users") with view/edit roles
- Search files by name/type
- Storage quota per user

### Non-functional requirements
- Uploads must not block the UI (async, chunked for large files)
- Files must be stored securely (private by default, signed URLs for access)
- System should scale storage independently from the database
- Basic rate limiting on auth and upload endpoints

## Step 2 - High-level architecture

```
┌──────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  Next.js App │ ─HTTP→ │   FastAPI (API)   │ ─────→ │  PostgreSQL       │
│  (Frontend)  │ ←JSON─ │  Auth / Files API │        │  metadata, users  │
└──────────────┘        └──────────────────┘        └──────────────────┘
                               │
                               ▼
                     ┌──────────────────────┐
                     │ Object Storage (S3 /  │
                     │ MinIO / GCS bucket)   │
                     │ actual file bytes     │
                     └──────────────────────┘
```

Key architectural decision: **never store raw file bytes in your own database or server disk long-term.** Store bytes in object storage (S3-compatible), and store only *metadata* (filename, size, owner, folder_id, storage_key, mime_type) in Postgres. This is exactly how Drive/Dropbox work at a conceptual level.

## Step 3 - Data model (starting point)

- `users` (id, email, password_hash, storage_quota_bytes, storage_used_bytes)
- `folders` (id, name, parent_folder_id, owner_id, created_at)
- `files` (id, name, folder_id, owner_id, storage_key, size_bytes, mime_type, created_at)
- `shares` (id, file_id/folder_id, shared_with_user_id OR share_token, permission, expires_at)

## Step 4 - Upload strategy (pick one to start)

1. **Simple (beginner):** client uploads to FastAPI → FastAPI streams to S3/MinIO. Easiest to build first.
2. **Presigned URL (intermediate, more scalable):** FastAPI issues a presigned PUT URL → client uploads directly to S3, bypassing your server. Matches real-world production systems.

Start with (1) to get a working demo, then refactor to (2) once basics work - this mirrors how real teams iterate.

---PAGE_BREAK---

# Tech Stack

## Recommended stack (matches your team's Next.js + FastAPI mandate)

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Next.js (App Router) + TypeScript** | File-based routing, server components for auth-gated pages |
| UI | Tailwind CSS + shadcn/ui | Fast to build clean drag-drop/upload UIs |
| Backend | **FastAPI (Python)** | Async by default - great for streaming uploads |
| Auth | FastAPI + JWT (python-jose) or `fastapi-users` | Session or token auth, simple to reason about |
| Database | PostgreSQL + SQLAlchemy (async) / SQLModel | Great fit for hierarchical folder relationships |
| Object storage | **MinIO** (local/dev, S3-compatible) → AWS S3 / GCS (prod) | Lets you develop offline, deploy anywhere |
| File client lib | `boto3` (Python) for S3 API calls | Works identically against MinIO and real S3 |
| Realtime (optional) | WebSockets for live upload progress / shared-folder updates | Nice-to-have, not core |
| Deployment | Docker Compose (Postgres + MinIO + API + Web) | One command spins up the whole stack locally |

## Feasible alternative stacks (if a team wants variation)

- **All-Node stack:** Next.js + Node/Express (or Next.js API routes only) + Prisma + Postgres + S3 SDK. Simpler if the team is weaker in Python.
- **Firebase-lite stack:** Next.js + Firebase Auth + Firebase Storage + Firestore. Fastest to prototype, less "systems design" learning value.
- **Self-hosted heavy stack:** Next.js + FastAPI + Postgres + MinIO + Redis (for background jobs like thumbnail generation) + Celery. Best for teams who want a production-grade capstone.

**Recommendation for this cohort:** Next.js + FastAPI + PostgreSQL + MinIO (Docker Compose), since it directly builds the skills mentioned in the brief (backend architecture, auth, cloud storage concepts, scalable design) without vendor lock-in.

---PAGE_BREAK---

# Learning Resources

## Official docs (read these first)
- Next.js App Router docs - routing, server actions, file uploads: https://nextjs.org/docs
- FastAPI official docs, especially "Request Files" and "Background Tasks": https://fastapi.tiangolo.com/tutorial/request-files/
- SQLAlchemy 2.0 async ORM docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- MinIO docs (S3-compatible object storage): https://min.io/docs/minio/linux/index.html
- AWS S3 developer guide (for concepts that transfer to MinIO/GCS too): https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html

## Curated tutorials & articles
- *Using FastAPI to Build an S3-Compatible Cloud Storage API* - upload/download endpoints against MinIO/S3 with `boto3`, a very close match to this project's core.
- *Building File Storage with Next.js, PostgreSQL, and MinIO S3* (multi-part series) - covers presigned URLs, Docker Compose setup for Minio, and a Next.js upload/download UI end to end.
- *Upload Files from Next.js to AWS S3 Using Presigned URLs* (DEV Community) - clean walkthrough of the "don't proxy bytes through your server" pattern for when you upgrade past the simple version.

## Good YouTube searches (search these titles on YouTube for current top results)
- "FastAPI file upload tutorial" - for the `UploadFile` basics
- "MinIO Docker Compose tutorial" - local S3-compatible storage setup
- "Next.js drag and drop file upload" - frontend UX patterns
- "JWT authentication FastAPI tutorial" - for the auth module
- "System design: how does Google Drive work" - good for the architecture discussion before coding

## Concepts to read up on separately
- Presigned URLs (why they exist, how expiry works)
- Soft delete vs hard delete patterns
- Row-level access control / permission tables

---PAGE_BREAK---

# Features & API Reference

## MVP feature checklist
- [ ] User signup/login/logout (JWT)
- [ ] Create folder, rename, delete, move
- [ ] Upload file(s) with progress bar
- [ ] List files/folders (breadcrumb navigation)
- [ ] Download file
- [ ] Preview file (image/PDF inline, others show icon)
- [ ] Move to trash / restore / permanent delete
- [ ] Share via link (read-only)
- [ ] Storage quota indicator

## Stretch features
- [ ] Share with specific users + edit permission
- [ ] File versioning (keep last N versions)
- [ ] Full-text search across file names and folders
- [ ] Thumbnail generation for images (background job)
- [ ] Activity log ("X uploaded Y on date")
- [ ] Real-time updates when a shared folder changes (WebSockets)

## Suggested API surface (FastAPI)

```
POST   /auth/register
POST   /auth/login
GET    /me

GET    /folders/{id}              # list contents of a folder (null id = root)
POST   /folders                   # create folder
PATCH  /folders/{id}               # rename/move
DELETE /folders/{id}               # soft delete

POST   /files/upload               # multipart upload (MVP)
POST   /files/presign-upload        # returns presigned PUT url (v2)
GET    /files/{id}/download
GET    /files/{id}/preview
PATCH  /files/{id}                 # rename/move
DELETE /files/{id}

POST   /shares                     # create a share link/grant
GET    /shares/{token}             # resolve a public share link
DELETE /shares/{id}                # revoke
```

## Sample response shape

```json
{
  "id": "f_123",
  "name": "resume.pdf",
  "size_bytes": 204800,
  "mime_type": "application/pdf",
  "folder_id": "d_45",
  "owner_id": "u_9",
  "created_at": "2026-08-01T10:00:00Z"
}
```

---PAGE_BREAK---

# Agile Roadmap & Kanban Board

Run this as 4 short sprints (roughly 1 week each for a student team). Track these cards on your kanban board with **Backlog → In Progress → Review → Done** columns.

## Sprint 0 - Design & Setup
- [ ] Write requirements doc (this page's functional list)
- [ ] Draw ER diagram for users/folders/files/shares
- [ ] Choose stack, scaffold Next.js app and FastAPI app
- [ ] Set up Docker Compose: Postgres + MinIO
- [ ] Set up repo, branching strategy, and CI lint check

## Sprint 1 - Auth & Core Data Model
- [ ] Implement signup/login (JWT issuance + verification middleware)
- [ ] Implement folders CRUD API
- [ ] Implement files metadata table + basic upload-to-MinIO endpoint
- [ ] Frontend: login/register pages, protected routes

## Sprint 2 - File Operations UI
- [ ] Frontend: folder browser (breadcrumbs, create/rename/delete folder)
- [ ] Frontend: drag-and-drop upload with progress bar
- [ ] Backend: download endpoint + file preview endpoint
- [ ] Trash/restore flow (soft delete)

## Sprint 3 - Sharing & Polish
- [ ] Share-link generation + public resolve endpoint
- [ ] Storage quota tracking + UI indicator
- [ ] Search by filename
- [ ] Bug bash + deploy (Docker Compose or cloud VM)

## Independent kanban cards (can be picked up by any member in parallel)
- `AUTH-1` Signup/login backend
- `AUTH-2` Login/register frontend forms
- `FOLD-1` Folder CRUD backend
- `FOLD-2` Folder browser UI
- `FILE-1` Upload endpoint (simple, server-proxied)
- `FILE-2` Upload endpoint (presigned URL, v2)
- `FILE-3` Download/preview endpoint
- `FILE-4` Upload UI with progress
- `SHARE-1` Share link backend
- `SHARE-2` Share link UI + public view page
- `INFRA-1` Docker Compose setup
- `INFRA-2` CI pipeline (lint + basic tests)
- `QUOTA-1` Storage quota tracking
- `SEARCH-1` Filename search endpoint + UI
