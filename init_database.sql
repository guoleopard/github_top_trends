-- GitHub Trending Crawler Database Initialization Script
-- This script creates the database and table structure for storing trending GitHub repositories

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS github_trending CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE github_trending;

-- Create repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repo_name VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(100),
    stars INT DEFAULT 0,
    forks INT DEFAULT 0,
    stars_weekly INT DEFAULT 0,
    html_url VARCHAR(500) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_repo (author, repo_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional: Index for better query performance
CREATE INDEX idx_language ON repositories(language);
CREATE INDEX idx_stars ON repositories(stars DESC);
CREATE INDEX idx_stars_weekly ON repositories(stars_weekly DESC);
CREATE INDEX idx_created_at ON repositories(created_at DESC);

-- Optional: Sample query to test the table
-- SELECT * FROM repositories ORDER BY stars_weekly DESC LIMIT 10;

SELECT 'Database and table creation completed successfully!' AS message;
