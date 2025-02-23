-- Create a new MySQL user with a password
CREATE USER IF NOT EXISTS 'renfield'@'localhost' IDENTIFIED BY 'renfield123';

-- Grant all privileges on the "renfield" database to the "renfield" user
GRANT ALL PRIVILEGES ON renfield.* TO 'renfield'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS renfield;
USE renfield;

-- Create the "vote_groups" table to store group names
CREATE TABLE IF NOT EXISTS vote_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL UNIQUE
);

-- Create the "votes" table
CREATE TABLE IF NOT EXISTS votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id BIGINT NOT NULL,
    vote_name VARCHAR(255) NOT NULL,
    group_id INT NULL,
    options TEXT NOT NULL,  -- JSON array of options
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (group_id) REFERENCES vote_groups(id) ON DELETE SET NULL
);

-- Create the "votes_users" table
CREATE TABLE IF NOT EXISTS votes_users (
    vote_id INT NOT NULL,
    user_id BIGINT NOT NULL,  -- Use BIGINT for Discord user IDs
    choice VARCHAR(255) NOT NULL,
    PRIMARY KEY (vote_id, user_id),
    FOREIGN KEY (vote_id) REFERENCES votes(id) ON DELETE CASCADE
);
