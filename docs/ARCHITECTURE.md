# Architecture Overview

## 1. System Overview

The Customer Health application is a containerized web-based system that calculates, stores, and displays customer health scores for a SaaS platform. It provides:

* A REST API for managing customer data and events
* A simple dashboard for visualizing customer health scores
* A MySQL database for storing customer data and historical events
* Containerized test environment for automated testing

All components run in isolated Docker containers for ease of deployment and reproducibility.

## 2. High-Level Architecture

The system consists of three main components:

1. **Backend Service (FastAPI)**
   * Exposes REST API endpoints (`/api/customers`, `/api/customers/{id}/health`, `/api/dashboard`, `/api/customers/{id}/events`)
   * Renders HTML templates for browser users (dashboard and detail views)
   * Handles incoming customer events and updates the database accordingly
2. **Database (MySQL)**

* Stores customer information and events
* Schema and sample data are initialized using `schema.sql` and `creating_samples.py` during container startup

3. **Testing Service**

* Runs automated tests in an isolated container
* Uses its own `docker-compose.tests.yml` configuration to avoid interfering with production data

## 3. Container Orchestration

The system uses **Docker Compose** to orchestrate containers.

Two configurations are provided:

* **Backend Application:**

  <pre class="overflow-visible!" data-start="1830" data-end="1893"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.backend.yml up
  </span></span></code></div></div></pre>

  * Starts the MySQL database container (`db`)
  * Starts the FastAPI backend container (`backend`)
  * Initializes schema and inserts sample data on startup
* **Test Environment:**

  <pre class="overflow-visible!" data-start="2079" data-end="2146"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose -f docker-compose.tests.yml up tests
  </span></span></code></div></div></pre>

  * Runs automated tests against a test database
  * Does not affect production database data

## 4. Data Flow

1. **Initialization**
   * MySQL database starts with schema and initial sample data.
   * FastAPI backend connects to the database using credentials defined in the Docker environment (`DB_HOST=db`, `DB_USER=root`, etc.).
2. **User Interaction**
   * Users access the dashboard via a browser (`/api/dashboard`).
   * API consumers (e.g., Postman) send requests to manage events or retrieve data.
3. **Event Processing**
   * Events such as logins, feature usage, tickets, and invoices are submitted to `/api/customers/{customer_id}/events`.
   * The backend validates the event type and inserts it into the database.
4. **Health Score Calculation**
   * Health scores are computed dynamically via helper functions (`get_health_scores()`, `get_health_details()`).
