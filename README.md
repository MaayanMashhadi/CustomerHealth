# CustomerHealth


This project provides a **Customer Health Monitoring System** with a FastAPI backend and a MySQL database.

It includes two Docker-based environments:

1. **Application environment** – runs the backend and database.
2. **Test environment** – runs the automated tests in an isolated container


## **Prerequisites**

Before you start, ensure you have the following installed:

* [Docker]() (recommended: Docker Desktop for Windows/macOS)
* [Docker Compose]()

## **1. Running the Application**

This will start:

* The **MySQL database container**
* The **FastAPI backend container**

### **Start the application:**

<pre class="overflow-visible!" data-start="1375" data-end="1442"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.backend.yml up --build</span></span></code></div></div></pre>

* The backend will be available at: [http://localhost:8000](http://localhost:8000)
* The database will be exposed on: `localhost:3306`

### **Stop the application:**

<pre class="overflow-visible!" data-start="1612" data-end="1673"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.backend.yml down</span></span></code></div></div></pre>


## **2. Running the Tests**

The tests run in a **separate Docker environment** to ensure isolation from the production containers.

### **Run the tests:**

<pre class="overflow-visible!" data-start="1836" data-end="1907"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.tests.yml up --build tests
</span></span></code></div></div></pre>

* This will spin up a temporary database and backend for testing.
* Test results will be printed in the terminal.

### **Stop and clean up:**

<pre class="overflow-visible!" data-start="2051" data-end="2110"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.tests.yml down</span></span></code></div></div></pre>

## **3. Database Setup (Automated)**

You  **do not need to manually create the database** .

The following happens automatically when you run the app:

1. `schema.sql` creates the database structure (tables, indexes, etc.).
2. `creating_samples.py` populates the tables with sample data.


## **4. Environment Variables**

Backend uses the following environment variables (from `docker-compose.backend.yml`):

* `DB_HOST` – Database host (default: `db`)
* `DB_USER` – Database user (default: `root`)
* `DB_PASSWORD` – Database password
* `DB_NAME` – Database name

## **6. Troubleshooting**

* **Port 3306 already in use?**

  Stop local MySQL or change port mapping in `docker-compose.backend.yml`.
* **Containers not starting properly?**

  Reset everything:

  <pre class="overflow-visible!" data-start="3321" data-end="3447"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.backend.yml down -v
  docker-compose -f docker-compose.backend.yml up --build</span></span></code></div></div></pre>
