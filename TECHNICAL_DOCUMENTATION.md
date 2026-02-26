# Advance Notifications
## Technical Architecture & Internal Behavior
Odoo 18 Enterprise

---

# 1. Purpose of the Module

Advance Notifications provides a real-time, AI-enhanced notification system inside Odoo.

It detects incoming email messages, creates user-specific notification records,
pushes live updates to the frontend via Odoo bus, and optionally generates
AI summaries using GPT-4.1-mini.

The module is:

- Non-invasive
- Transaction-safe
- Crash-proof
- Read-only toward business models
- Fully isolated from core logic

It does NOT alter:
- CRM workflows
- Helpdesk workflows
- Mail routing
- Message posting behavior

---

# 2. Folder Structure

advance_notifications/
│
├── __manifest__.py
├── __init__.py
│
├── models/
│   ├── __init__.py
│   ├── notification.py
│   └── openai_service.py
│
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
│
└── static/
    └── src/
        ├── js/
        │   └── systray_notifications.js
        ├── xml/
        │   └── systray_template.xml
        └── scss/
            └── style.scss

---

# 3. Backend Architecture

## 3.1 Model: advance.notification

Purpose:
Stores user notification entries linked to mail messages.

Fields:

- user_id (Many2one res.users)
- message_id (Many2one mail.message)
- model (Char) → source model
- res_id (Integer) → source record ID
- ai_summary (Text) → optional GPT summary
- is_done (Boolean) → user cleared notification

Ordering:
Newest first (create_date desc)

---

## 3.2 Hook: mail.message.create()

The module overrides:

    mail.message.create()

Logic:

1. Let Odoo create message normally.
2. Check:
   - message_type == "email"
   - model exists
   - res_id exists
   - body not empty
3. Fetch related record.
4. If record has user_id:
   - Create advance.notification
5. Push bus event to that user.
6. Attempt AI summary generation.

Important:
- No manual commits
- Wrapped in try/except
- Never raises exception outward

Transaction safety preserved.

---

# 4. AI Service Layer

Model:
    openai.service (AbstractModel)

Method:
    summarize_message(body)

Steps:

1. Fetch API key from ir.config_parameter
2. Convert HTML to plain text
3. Truncate to 1200 chars
4. Send POST request to:
       https://api.openai.com/v1/chat/completions
5. Use:
       model: gpt-4.1-mini
       temperature: 0.2
       timeout: 5 seconds
6. Return summary or False

Failure Handling:

- Network errors caught
- API errors caught
- Timeout caught
- Logged via _logger.warning
- No exception escapes to user

If AI fails:
Notification still exists.
Only summary remains empty.

---

# 5. Live Update System (Odoo Bus)

Backend push:

    bus.bus._sendone(
        (dbname, 'res.partner', partner_id),
        "advance_notifications_channel",
        payload
    )

Payload contains:
- notification id
- model
- res_id

Frontend subscribes to:

    advance_notifications_channel

Result:
New notification appears instantly.
No reload required.

---

# 6. Frontend Architecture (OWL Component)

File:
    systray_notifications.js

Component Responsibilities:

- Load top 10 unread notifications
- Listen to bus events
- Update badge counter
- Play native Odoo sound
- Open related record on click
- Mark notification as done

UI Location:
Odoo systray (top-right bar)

Mobile Support:
Dropdown width responsive under 768px.

---

# 7. Security Model

Two ir.rules defined:

1. Normal Users:
   Domain:
       user_id == current user

2. Admin (group_system):
   Domain:
       [(1,'=',1)]  (see all)

Access Control:
All internal users can read/write their own notifications.

---

# 8. Performance Characteristics

AI Call:
- Only triggered for email messages
- Max 1200 characters
- 5 second timeout
- Non-blocking design

Database:
- Simple model
- Indexed by default
- Limited fetch (10 records)

Scales well for small and medium businesses.

---

# 9. Failure Isolation

Even if:

- OpenAI is down
- API key invalid
- Network fails
- JSON response malformed

System behavior:

- No crash
- No rollback corruption
- No blocked transactions
- Notification still created

Fully crash-proof by design.

---

# 10. Operational Safety

The module:

- Does not mutate business models
- Does not alter mail routing
- Does not override message_post
- Does not manually commit transactions
- Uses proper Odoo 18 bus namespacing
- Logs AI errors for debugging

Enterprise safe.

---

# 11. User Flow Summary

Incoming Email
        ↓
mail.message created
        ↓
advance.notification created
        ↓
Bus event pushed
        ↓
Frontend updates instantly
        ↓
AI summary generated (optional)
        ↓
User clicks → opens record
        ↓
User marks done → notification hidden

---

# 12. Extensibility

Future enhancements possible:

- Async job queue
- AI priority tagging
- Notification grouping
- SLA detection
- Admin analytics dashboard
- Rate limiting

Architecture already supports expansion.

---

END OF TECHNICAL DOCUMENTATION
