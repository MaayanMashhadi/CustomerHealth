## API Documentation

This web application provides a REST API for calculating and managing **customer health scores** and related events for a SaaS platform. It also includes an HTML dashboard to view customer health data.

### Base URL

When running locally via Docker Compose, the API is available at:

<pre class="overflow-visible!" data-start="511" data-end="540"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>http:</span><span>//localhost:8000</span></span></code></div></div></pre>

### Endpoints

#### 1. **List Customers**

* **URL:** `/api/customers`
* **Method:** `GET`
* **Response:** HTML page displaying all customers and their health scores.

#### 2. **Customer Health Details**

* **URL:** `/api/customers/{customer_id}/health`
* **Method:** `GET`
* **Path Parameters:**
  * `customer_id` (integer) – ID of the customer.
* **Response:** HTML page with detailed health information for the specified customer.
* **Errors:**
  * `404 Not Found` – Customer does not exist.

#### 3. **Add Customer Event**

* **URL:** `/api/customers/{customer_id}/events`
* **Method:** `POST`
* **Path Parameters:**

  * `customer_id` (integer) – ID of the customer.
* **Request Body (JSON):**

  <pre class="overflow-visible!" data-start="1244" data-end="1371"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>
    </span><span>"type"</span><span>:</span><span></span><span>"feature"</span><span>,</span><span> 
    </span><span>"details"</span><span>:</span><span></span><span>{</span><span>
      </span><span>"feature_name"</span><span>:</span><span></span><span>"NewFeature"</span><span>,</span><span>
      </span><span>"usage_count"</span><span>:</span><span></span><span>3</span><span>
    </span><span>}</span><span>
  </span><span>}</span><span>
  </span></span></code></div></div></pre>

  Supported event types:

  * `"login"` – Tracks customer login.
  * `"feature"` – Tracks feature usage (`feature_name`, optional `usage_count`).
  * `"ticket"` – Logs a support ticket (`status`, `priority`).
  * `"invoice"` – Adds invoice info (`amount`, `due_date`, optional `paid_date`).
  * `"api"` – Logs API calls (optional `calls_count`).
* **Response:** HTML page indicating success or missing fields.

#### 4. **Dashboard**

* **URL:** `/api/dashboard`
* **Method:** `GET`
* **Response:** HTML dashboard summarizing all customers and their health metrics.

### Authentication

No authentication is required for local development.
