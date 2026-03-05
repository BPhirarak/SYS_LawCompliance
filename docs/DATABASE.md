# Database Schema & ERD

## Overview
SQLite database with WAL (Write-Ahead Logging) mode for better concurrency.

## Entity Relationship Diagram

```
┌─────────────────────┐
│   law_categories    │
│─────────────────────│
│ id (PK)             │
│ code (UNIQUE)       │
│ name_th             │
│ name_en             │
└──────────┬──────────┘
           │
           │ 1:N
           │
┌──────────▼──────────┐         ┌─────────────────────┐
│       laws          │         │    departments      │
│─────────────────────│         │─────────────────────│
│ id (PK)             │         │ id (PK)             │
│ category_id (FK)    │         │ code (UNIQUE)       │
│ code (UNIQUE)       │         │ name_th             │
│ name_th             │         │ name_en             │
│ name_en             │         │ created_at          │
│ description         │         └──────────┬──────────┘
│ effective_date      │                    │
│ last_updated        │                    │
│ status              │                    │
│ risk_level          │                    │
│ penalty_summary     │                    │
│ source_url          │                    │
│ created_at          │                    │
│ updated_at          │                    │
└──────────┬──────────┘                    │
           │                               │
           │ N:M                           │
           │                               │
           │    ┌──────────────────────────┘
           │    │
           │    │
┌──────────▼────▼──────┐
│ department_law_matrix│
│──────────────────────│
│ id (PK)              │
│ department_id (FK)   │
│ law_id (FK)          │
│ relevance_level      │
│ notes                │
│ UNIQUE(dept, law)    │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼──────────┐
│  compliance_tasks   │
│─────────────────────│
│ id (PK)             │
│ law_id (FK)         │
│ department_id (FK)  │
│ title               │
│ description         │
│ status              │
│ priority            │
│ assignee            │
│ plan                │
│ due_date            │
│ completed_at        │
│ created_at          │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐
│    law_updates      │
│─────────────────────│
│ id (PK)             │
│ law_id (FK)         │
│ update_type         │
│ summary             │
│ detected_at         │
│ source              │
│ agent_run_id        │
└─────────────────────┘

┌─────────────────────┐
│    agent_runs       │
│─────────────────────│
│ id (PK)             │
│ run_id (UNIQUE)     │
│ started_at          │
│ completed_at        │
│ status              │
│ laws_checked        │
│ updates_found       │
│ summary             │
└─────────────────────┘

┌─────────────────────┐
│   chat_sessions     │
│─────────────────────│
│ id (PK)             │
│ session_id (UNIQUE) │
│ username            │
│ title               │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
           │ 1:N
           │
┌──────────▼──────────┐
│   chat_messages     │
│─────────────────────│
│ id (PK)             │
│ session_id (FK)     │
│ role                │
│ content             │
│ law_updates (JSON)  │
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│       users         │
│─────────────────────│
│ id (PK)             │
│ username (UNIQUE)   │
│ password_hash       │
│ role                │
│ created_at          │
└─────────────────────┘
```

## Table Definitions

### law_categories
กลุ่มหมวดหมู่กฎหมาย (9 categories)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| code | TEXT UNIQUE | รหัสหมวดหมู่ (FACTORY, SAFETY, ENV, LABOR, QUALITY, TAX, TRADE, CSRLAW, CYBER) |
| name_th | TEXT | ชื่อภาษาไทย |
| name_en | TEXT | ชื่อภาษาอังกฤษ |

### laws
กฎหมายทั้งหมดในระบบ (17+ laws)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| category_id | INTEGER FK | Foreign key → law_categories |
| code | TEXT UNIQUE | รหัสกฎหมาย (FACTORY-001, LABOR-001, etc.) |
| name_th | TEXT | ชื่อกฎหมายภาษาไทย |
| name_en | TEXT | ชื่อภาษาอังกฤษ |
| description | TEXT | รายละเอียดสำคัญ |
| effective_date | TEXT | วันที่มีผลบังคับใช้ |
| last_updated | TEXT | วันที่แก้ไขล่าสุด |
| status | TEXT | สถานะ (active/inactive) |
| risk_level | TEXT | ระดับความเสี่ยง (critical/high/medium/low) |
| penalty_summary | TEXT | สรุปบทลงโทษ |
| source_url | TEXT | URL ไปยังเว็บไซต์ราชกิจจานุเบกษา |
| created_at | DATETIME | วันที่สร้างระเบียน |
| updated_at | DATETIME | วันที่แก้ไขล่าสุด |

### departments
หน่วยงานภายในองค์กร (25 departments)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| code | TEXT UNIQUE | รหัสหน่วยงาน (SP-MP, RM-MP, DX&IT, etc.) |
| name_th | TEXT | ชื่อภาษาไทย |
| name_en | TEXT | ชื่อภาษาอังกฤษ |
| created_at | DATETIME | วันที่สร้างระเบียน |

### department_law_matrix
ความสัมพันธ์ระหว่างหน่วยงานกับกฎหมาย (N:M relationship)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| department_id | INTEGER FK | Foreign key → departments |
| law_id | INTEGER FK | Foreign key → laws |
| relevance_level | TEXT | ระดับความเกี่ยวข้อง (primary/high/medium/low) |
| notes | TEXT | หมายเหตุเพิ่มเติม |
| UNIQUE(department_id, law_id) | | ป้องกันข้อมูลซ้ำ |

### compliance_tasks
งาน compliance ที่ต้องทำ (Kanban board)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| law_id | INTEGER FK | Foreign key → laws |
| department_id | INTEGER FK | Foreign key → departments |
| title | TEXT | ชื่องาน |
| description | TEXT | รายละเอียด |
| status | TEXT | สถานะ (todo/in_progress/done) |
| priority | TEXT | ความสำคัญ (critical/high/medium/low) |
| assignee | TEXT | ผู้รับผิดชอบ |
| plan | TEXT | แผนการดำเนินงาน |
| due_date | TEXT | วันครบกำหนด |
| completed_at | DATETIME | วันที่เสร็จสิ้น |
| created_at | DATETIME | วันที่สร้าง |
| updated_at | DATETIME | วันที่แก้ไขล่าสุด |

### law_updates
บันทึกการเปลี่ยนแปลงกฎหมาย

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| law_id | INTEGER FK | Foreign key → laws |
| update_type | TEXT | ประเภท (new/amended/repealed) |
| summary | TEXT | สรุปการเปลี่ยนแปลง |
| detected_at | DATETIME | วันที่ตรวจพบ |
| source | TEXT | แหล่งที่มา |
| agent_run_id | TEXT | ID ของ agent run |

### agent_runs
บันทึกการรัน law scanner agent

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| run_id | TEXT UNIQUE | Unique run identifier |
| started_at | DATETIME | เวลาเริ่มต้น |
| completed_at | DATETIME | เวลาเสร็จสิ้น |
| status | TEXT | สถานะ (running/completed/failed) |
| laws_checked | INTEGER | จำนวนกฎหมายที่ตรวจสอบ |
| updates_found | INTEGER | จำนวนการเปลี่ยนแปลงที่พบ |
| summary | TEXT | สรุปผลการรัน |

### chat_sessions
Session การสนทนากับ AI agent

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| session_id | TEXT UNIQUE | Unique session ID |
| username | TEXT | ชื่อผู้ใช้ |
| title | TEXT | หัวข้อการสนทนา |
| created_at | DATETIME | วันที่สร้าง |
| updated_at | DATETIME | วันที่แก้ไขล่าสุด |

### chat_messages
ข้อความในการสนทนา

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| session_id | TEXT FK | Foreign key → chat_sessions |
| role | TEXT | บทบาท (user/assistant) |
| content | TEXT | เนื้อหาข้อความ |
| law_updates | TEXT | JSON array ของ law updates |
| created_at | DATETIME | วันที่สร้าง |

### users
บัญชีผู้ใช้งานระบบ

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| username | TEXT UNIQUE | ชื่อผู้ใช้ |
| password_hash | TEXT | รหัสผ่าน (SHA-256 hash) |
| role | TEXT | บทบาท (admin/user) |
| created_at | DATETIME | วันที่สร้าง |

## Indexes
- `law_categories.code` — UNIQUE index
- `laws.code` — UNIQUE index
- `departments.code` — UNIQUE index
- `department_law_matrix(department_id, law_id)` — UNIQUE composite index
- `users.username` — UNIQUE index
- `chat_sessions.session_id` — UNIQUE index

## Data Integrity
- Foreign key constraints enabled
- UNIQUE constraints on codes and identifiers
- NOT NULL constraints on required fields
- Default values for timestamps (CURRENT_TIMESTAMP)
- WAL mode for better concurrency

## Sample Queries

### Get all laws with category and department count
```sql
SELECT l.*, lc.name_th as category_name,
       COUNT(DISTINCT dlm.department_id) as dept_count
FROM laws l
LEFT JOIN law_categories lc ON l.category_id = lc.id
LEFT JOIN department_law_matrix dlm ON l.id = dlm.law_id
GROUP BY l.id
ORDER BY l.risk_level DESC, l.code;
```

### Get tasks by department with law details
```sql
SELECT ct.*, d.name_th as dept_name, l.name_th as law_name, l.risk_level
FROM compliance_tasks ct
LEFT JOIN departments d ON ct.department_id = d.id
LEFT JOIN laws l ON ct.law_id = l.id
WHERE ct.status != 'done'
ORDER BY CASE ct.priority 
  WHEN 'critical' THEN 1 
  WHEN 'high' THEN 2 
  WHEN 'medium' THEN 3 
  ELSE 4 
END;
```

### Get department-law matrix with relevance
```sql
SELECT d.code as dept_code, d.name_th as dept_name,
       l.code as law_code, l.name_th as law_name,
       dlm.relevance_level, l.risk_level
FROM department_law_matrix dlm
JOIN departments d ON dlm.department_id = d.id
JOIN laws l ON dlm.law_id = l.id
ORDER BY d.code, l.code;
```
