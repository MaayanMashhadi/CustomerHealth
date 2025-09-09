-- Create database
-- CREATE DATABASE customer_health;
USE customer_health;

-- Customers table
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    segment ENUM('Enterprise', 'SMB', 'Startup'),
    created_at DATE
);

-- Login activity (frequency)
CREATE TABLE logins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    login_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Feature adoption
CREATE TABLE feature_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    feature_name VARCHAR(50),
    usage_count INT,
    usage_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Support tickets
CREATE TABLE support_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    created_at DATE,
    status ENUM('open', 'closed', 'pending'),
    priority ENUM('low', 'medium', 'high'),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Invoices (payment timeliness)
CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10,2),
    due_date DATE,
    paid_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- API usage
CREATE TABLE api_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    calls_count INT,
    usage_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);