# SwayAlgo Education ERP - Local Setup Guide

This guide covers the end-to-end process of setting up the Education ERP project (both Frappe Backend and React Frontend) on a new machine.

## 🛠️ Prerequisites

Before you begin, ensure your system has the following installed:
- **Git** (for version control)
- **Node.js** (v18+ recommended)
- **Python** (v3.10+ recommended)
- **MariaDB** (v10.6+)
- **Redis**
- **wkhtmltopdf**
- **Bench CLI** (Frappe framework manager)

> **Tip:** If you are setting up Frappe for the first time on Linux/Mac, it is highly recommended to follow the [Official Frappe Framework Installation Guide](https://frappeframework.com/docs/user/en/installation) to install MariaDB, Redis, and Node correctly.

---

## 1️⃣ Backend Setup (Frappe/ERPNext)

We use Frappe v16 with the official `erpnext` and `education` apps, alongside our custom `school_erp` app.

### Step 1: Initialize a new Bench
Open your terminal and initialize a new bench environment:
```bash
bench init edu-backend --frappe-branch version-16
cd edu-backend
```

### Step 2: Download Required Apps
Fetch the necessary core apps and your custom app:
```bash
# Get official apps
bench get-app erpnext --branch version-16
bench get-app education --branch version-16

# Get our custom app (replace with your actual git URL)
bench get-app https://github.com/SwayAlgo/school_erp.git
```

### Step 3: Create a New Site
Create a local site. You will be prompted to set an Administrator password.
```bash
bench new-site edu.local
```
> **Note:** If you are on Linux/Mac, you might want to add `127.0.0.1 edu.local` to your `/etc/hosts` file.

### Step 4: Install Apps to the Site
Install the apps in this specific order:
```bash
bench --site edu.local install-app erpnext
bench --site edu.local install-app education
bench --site edu.local install-app school_erp
```

### Step 5: Migrate Data (Apply Customizations)
This step is **crucial**. It will apply all the custom fields and property setters we exported as fixtures in the `school_erp` app.
```bash
bench --site edu.local migrate
```

### Step 6: Enable Developer Mode (Local Dev Only)
Enable developer mode to allow further customizations to be saved to files.
```bash
bench set-config -g developer_mode 1
bench --site edu.local clear-cache
```

### Step 7: Start the Server
```bash
bench start
```
Your backend is now running at `http://edu.local:8000` (or `http://localhost:8000`).

---

## 2️⃣ Frontend Setup (React / Nx Monorepo)

Our frontend is an Nx Monorepo housing React micro-frontends.

### Step 1: Clone the Repository
Open a new terminal window:
```bash
git clone https://github.com/SwayAlgo/Education-ERP-Frontend.git
cd Education-ERP-Frontend
```

### Step 2: Install Dependencies
Install all required Node modules:
```bash
npm install
# or yarn install / pnpm install (depending on your package manager)
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root directory (or copy from `.env.example` if it exists):
```bash
touch .env
```
Add the API URL pointing to your local Frappe backend:
```env
VITE_API_URL=http://edu.local:8000
```
> **Important:** Make sure CORS is configured correctly on the Frappe backend. If you face CORS issues, you may need to add `http://localhost:4200` to your site config: `bench --site edu.local set-config -g allow_cors "*"`.

### Step 4: Start the Development Server
Since this is an Nx workspace, you can start specific applications (like the `admin` portal or `shell`):
```bash
npx nx serve admin
```
or if you use standard npm scripts:
```bash
npm run dev
```

Your frontend should now be running (usually at `http://localhost:4200`) and seamlessly communicating with the local Frappe backend!
