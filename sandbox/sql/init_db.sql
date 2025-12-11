-- SQL Sandbox Initialization Script
-- This script sets up the default database and sample tables

-- Create default database if not exists
CREATE DATABASE IF NOT EXISTS sandbox_db;
USE sandbox_db;

-- Sample employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample departments table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100),
    manager_id INT,
    budget DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample projects table
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    department_id INT,
    start_date DATE,
    end_date DATE,
    status ENUM('planning', 'active', 'completed', 'cancelled') DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- Sample employee_projects (many-to-many)
CREATE TABLE IF NOT EXISTS employee_projects (
    employee_id INT NOT NULL,
    project_id INT NOT NULL,
    role VARCHAR(50),
    assigned_date DATE,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Insert sample data for departments
INSERT INTO departments (name, location, budget) VALUES
('Engineering', 'San Francisco', 500000.00),
('Marketing', 'New York', 300000.00),
('Sales', 'Chicago', 400000.00),
('Human Resources', 'San Francisco', 200000.00),
('Finance', 'New York', 350000.00);

-- Insert sample data for employees
INSERT INTO employees (first_name, last_name, email, department, salary, hire_date) VALUES
('John', 'Doe', 'john.doe@example.com', 'Engineering', 95000.00, '2020-01-15'),
('Jane', 'Smith', 'jane.smith@example.com', 'Marketing', 75000.00, '2020-03-22'),
('Bob', 'Johnson', 'bob.johnson@example.com', 'Sales', 85000.00, '2019-11-10'),
('Alice', 'Williams', 'alice.williams@example.com', 'Engineering', 105000.00, '2018-07-01'),
('Charlie', 'Brown', 'charlie.brown@example.com', 'Human Resources', 65000.00, '2021-02-14'),
('Diana', 'Davis', 'diana.davis@example.com', 'Finance', 90000.00, '2019-09-05'),
('Eve', 'Martinez', 'eve.martinez@example.com', 'Engineering', 98000.00, '2020-06-20'),
('Frank', 'Garcia', 'frank.garcia@example.com', 'Sales', 78000.00, '2021-04-12'),
('Grace', 'Wilson', 'grace.wilson@example.com', 'Marketing', 72000.00, '2021-08-30'),
('Henry', 'Moore', 'henry.moore@example.com', 'Finance', 88000.00, '2020-10-18');

-- Insert sample data for projects
INSERT INTO projects (name, description, department_id, start_date, end_date, status) VALUES
('Website Redesign', 'Complete overhaul of company website', 2, '2023-01-01', '2023-06-30', 'completed'),
('Mobile App Development', 'Native mobile app for iOS and Android', 1, '2023-03-15', '2023-12-31', 'active'),
('Sales Campaign Q2', 'Spring sales initiative', 3, '2023-04-01', '2023-06-30', 'completed'),
('HR System Upgrade', 'Upgrade to new HRIS platform', 4, '2023-05-01', '2023-09-30', 'active'),
('Financial Audit 2023', 'Annual financial audit process', 5, '2023-01-01', '2023-03-31', 'completed');

-- Insert sample data for employee_projects
INSERT INTO employee_projects (employee_id, project_id, role, assigned_date) VALUES
(1, 2, 'Lead Developer', '2023-03-15'),
(4, 2, 'Senior Developer', '2023-03-15'),
(7, 2, 'Developer', '2023-04-01'),
(2, 1, 'Project Manager', '2023-01-01'),
(9, 1, 'Designer', '2023-01-01'),
(3, 3, 'Sales Lead', '2023-04-01'),
(8, 3, 'Sales Representative', '2023-04-01'),
(5, 4, 'HR Lead', '2023-05-01'),
(6, 5, 'Financial Analyst', '2023-01-01');

-- Create additional sample tables for practice

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50),
    country VARCHAR(50),
    registration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Insert sample customers
INSERT INTO customers (first_name, last_name, email, phone, city, country, registration_date) VALUES
('Michael', 'Scott', 'michael.scott@example.com', '555-0101', 'Scranton', 'USA', '2022-01-15'),
('Pam', 'Beesly', 'pam.beesly@example.com', '555-0102', 'Scranton', 'USA', '2022-02-20'),
('Jim', 'Halpert', 'jim.halpert@example.com', '555-0103', 'Scranton', 'USA', '2022-01-25'),
('Dwight', 'Schrute', 'dwight.schrute@example.com', '555-0104', 'Scranton', 'USA', '2022-03-10'),
('Angela', 'Martin', 'angela.martin@example.com', '555-0105', 'Scranton', 'USA', '2022-04-05');

-- Insert sample products
INSERT INTO products (name, description, category, price, stock_quantity) VALUES
('Laptop Pro', 'High-performance laptop', 'Electronics', 1299.99, 50),
('Wireless Mouse', 'Ergonomic wireless mouse', 'Electronics', 29.99, 200),
('Office Chair', 'Comfortable office chair', 'Furniture', 299.99, 30),
('Desk Lamp', 'LED desk lamp', 'Furniture', 49.99, 100),
('Notebook Set', 'Pack of 5 notebooks', 'Stationery', 15.99, 500),
('Pen Set', 'Premium pen collection', 'Stationery', 24.99, 300),
('Monitor 27"', '4K Ultra HD monitor', 'Electronics', 399.99, 40),
('Keyboard Mechanical', 'RGB mechanical keyboard', 'Electronics', 129.99, 75),
('Webcam HD', '1080p webcam', 'Electronics', 79.99, 60),
('Headphones', 'Noise-cancelling headphones', 'Electronics', 199.99, 80);

-- Insert sample orders
INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
(1, '2023-05-01', 1329.98, 'delivered'),
(2, '2023-05-05', 349.98, 'delivered'),
(3, '2023-05-10', 1699.97, 'shipped'),
(4, '2023-05-15', 40.98, 'delivered'),
(5, '2023-05-20', 579.98, 'processing');

-- Insert sample order items
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
(2, 3, 1, 299.99),
(2, 4, 1, 49.99),
(3, 1, 1, 1299.99),
(3, 7, 1, 399.99),
(4, 5, 1, 15.99),
(4, 6, 1, 24.99),
(5, 8, 1, 129.99),
(5, 9, 1, 79.99),
(5, 10, 2, 199.99);

FLUSH PRIVILEGES;
