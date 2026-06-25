-- Poster database schema
-- Run this in phpMyAdmin (XAMPP locally, cPanel in production)

CREATE DATABASE IF NOT EXISTS poster_db;
USE poster_db;

-- Traditional email/password login
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(50) not null,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Linked Twitter accounts (one user can later have multiple)
CREATE TABLE IF NOT EXISTS twitter_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    twitter_user_id VARCHAR(50) UNIQUE NOT NULL,
    twitter_username VARCHAR(100),
    access_token TEXT,
    refresh_token TEXT,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

ALTER TABLE twitter_accounts
ADD COLUMN token_expires_at DATETIME NULL,
ADD COLUMN token_type VARCHAR(50) DEFAULT 'bearer';