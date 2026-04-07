# Facility Manager

A comprehensive, production-ready Django application for facility and maintenance management. This platform enables organizations to efficiently manage buildings, rooms, assets, inventory, and maintenance workflows through a centralized system.

## 🚀 Features

- **Facility Management:** Organize and track multiple buildings and rooms.
- **Asset Tracking:** Detailed asset inventory with categories, status tracking, and location mapping.
- **Maintenance Workflows:**
    - Create and assign Work Orders with priority levels.
    - Scheduled and ad-hoc Inspections.
    - Real-time comments and history logging.
- **Inventory & Spare Parts:** Manage suppliers and track stock movements linked to maintenance tasks.
- **Role-Based Access Control:** Secure management with specific roles (Admin, Manager, Technician, Staff).
- **REST API:** Fully integrated Django Rest Framework (DRF) for external integrations.
- **Modern Infrastructure:**
    - **Celery & Redis:** Asynchronous task processing for background jobs.
    - **Cloudflare R2:** Scalable S3-compatible media storage.
    - **PostgreSQL:** Reliable relational data storage.
    - **Mailjet:** Integrated email notifications via Anymail.
    - **Whitenoise:** Efficient static file serving.

## 🌐 Demo

A live demo of the project is available at: [https://facility-manager-production-7f1e.up.railway.app/](https://facility-manager-production-7f1e.up.railway.app/)

**Default Admin Credentials:**
- **Email:** `admin@admin.com`
- **Password:** `123ADMINadmin$%^`

> [!IMPORTANT]
> When testing with your own account, please use a **real email address**. Email verification is required to log in, and you won't be able to access the system without a verified email.

## 🛠 Tech Stack

- **Backend:** Python 3.13+, Django 6.0+
- **Database:** PostgreSQL
- **API:** Django Rest Framework (DRF)
- **Task Queue:** Celery with Redis broker
- **Storage:** Cloudflare R2 (Media), Whitenoise (Static)
- **Deployment:** Optimized for Railway.app

## 📁 Project Structure

```text
├── accounts/           # User models, profiles, and role management
├── api/                # DRF serializers, views, and endpoints
├── assets/             # Asset categories and tracking
├── common/             # Shared utilities, history logging, and menu registry
├── facilities/         # Building and room management
├── inventory/          # Spare parts, suppliers, and stock movements
├── maintenance/        # Work orders, inspections, and maintenance logic
├── facility_manager/   # Core project configuration (settings, URLs, Celery)
├── templates/          # HTML templates for the web interface
└── static/             # CSS and JavaScript assets
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.13+
- Redis (for Celery and caching)
- PostgreSQL

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/facility-manager.git
   cd facility-manager
   ```

2. **Install dependencies:**
   (Using `uv` is recommended based on the presence of `uv.lock`)
   ```bash
   uv sync
   ```

3. **Environment Configuration:**
   Copy `template.env` to `.env` and fill in your credentials:
   ```bash
   cp template.env .env
   ```

4. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```

6. **Start Celery Worker (in a separate terminal):**
   ```bash
   ./start_celery.sh
   ```

## 🚢 Deployment

The project is configured for deployment on **Railway** using the provided `railway.json` and `nixpacks.toml`.

- **Production Settings:** Located in `facility_manager/settings/prod.py`.
- **Media Storage:** Uses Cloudflare R2 (S3 compatible).
- **Static Files:** Handled by Whitenoise with compression.

### Default Admin Creation

The project includes a custom command to create a default **Admin** user (specifically a user added to the `Admin` group, not to be confused with a Django superuser). This is recommended for production environments where having a superuser might be a security concern.

To create this user, you can run:
```bash
python manage.py create_default_admin
```

The email and password for this user are configured via environment variables (see `template.env.production`):
- `DJANGO_ADMIN_EMAIL`
- `DJANGO_ADMIN_PASSWORD`

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details (or add your own license).
