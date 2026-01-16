# Subtracker  Saas subscription manager

A ful-stack django application to track monthly subscription, visualize spending, and recieve automated emails before due date
## Tech Stack
- **Backend:** Django 5, Python 3.12
- **Database:** PostgreSQL
- **Async Tasks:** Celery + Redis (for daily email automation)
- **Frontend:** TailwindCSS + Chart.js
- **DevOps:** Docker & Docker Compose

## Key Features
- **Dashboard Visualization:** Interactive Doughnut chart showing spending breakdown.
- **Automated Alerts:** Background workers (Celery) send email notifications 3 days before billing.
- **Secure Authentication:** User registration, login, and secure password handling.
- **Microservices Architecture:** Fully containerized services.

