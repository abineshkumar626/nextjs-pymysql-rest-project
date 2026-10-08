CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;

CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    course VARCHAR(100) NOT NULL
);

INSERT INTO students (name, email, course) VALUES
('Arun', 'arun@gmail.com', 'Python'),
('Priya', 'priya@gmail.com', 'React'),
('Karthik', 'karthik@gmail.com', 'Java');
