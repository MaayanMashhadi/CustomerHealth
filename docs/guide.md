### Brief Deployment Guide

This project runs entirely in  **Docker containers** , with separate services for the backend application, tests, and the MySQL database.

#### 1. Prerequisites

* Docker & Docker Compose installed
* Port 8000 and 3306 available

#### 2. Running the Application

Start the backend and database:

<pre class="overflow-visible!" data-start="410" data-end="477"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.backend.yml up --build
</span></span></code></div></div></pre>

* Backend will be accessible at: `http://localhost:8000`
* Database service is available as `db` inside Docker.

#### 3. Running Tests

Run tests in a separate container:

<pre class="overflow-visible!" data-start="652" data-end="715"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.tests.yml up tests
</span></span></code></div></div></pre>

* Tests automatically recognize the backend code.
* Code coverage and test results will be displayed in the console.

#### 4. Database Setup

The backend container automatically initializes the database using:

* `schema.sql` → creates tables
* `creating_samples.py` → inserts sample data

#### 5. Cleaning Up / Troubleshooting

* To remove database data (reset):

<pre class="overflow-visible!" data-start="1156" data-end="1207"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker volume </span><span>rm</span><span> customerhealth_db_data
</span></span></code></div></div></pre>

* To rebuild containers after code changes:

<pre class="overflow-visible!" data-start="1254" data-end="1321"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.backend.yml up --build</span></span></code></div></div></pre>
