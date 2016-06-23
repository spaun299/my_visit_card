CREATE TABLE IF NOT EXISTS me(description TEXT NOT NULL, short_description TEXT NOT NULL,
github_link VARCHAR(150) NOT NULL, linkedin_link VARCHAR(150) NOT NULL,
bitbucket_link VARCHAR(150) NOT NULL, facebook_link VARCHAR(150) NOT NULL,
email VARCHAR(100) NOT NULL, email_password VARCHAR(100) NOT NULL, location VARCHAR(100) NOT NULL,
  status VARCHAR(100) DEFAULT 'Now work, but open for proposals' NOT NULL,
  skype VARCHAR(50) NOT NULL , phone VARCHAR(50) NOT NULL,
  english_level VARCHAR(50) NOT NULL
);


CREATE SEQUENCE experience_id;
CREATE TABLE IF NOT EXISTS experience(id INT PRIMARY KEY NOT NULL DEFAULT nextval('experience_id'),
company_name VARCHAR(100) NOT NULL, position VARCHAR(100) NOT NULL,
date_from DATE NOT NULL, date_to DATE , company_description TEXT NOT NULL,
my_responsobility TEXT NOT NULL, workers_amount INT NOT NULL,
location VARCHAR(100) NOT NULL );

CREATE SEQUENCE all_skills_id;
CREATE TABLE all_skills(id INT PRIMARY KEY DEFAULT nextval('all_skills_id') NOT NULL ,
name VARCHAR(150) NOT NULL, icon_link VARCHAR(150));

CREATE SEQUENCE my_skills_id;
CREATE TABLE IF NOT EXISTS my_skills(id INT PRIMARY KEY NOT NULL DEFAULT nextval('my_skills_id'),skill_id INTEGER REFERENCES all_skills(id),
priority INT DEFAULT 1 NOT NULL);

CREATE SEQUENCE projects_id;
CREATE TABLE IF NOT EXISTS projects(id INT PRIMARY KEY NOT NULL DEFAULT nextval('projects_id'),
name VARCHAR(150) NOT NULL, type VARCHAR(100) NOT NULL DEFAULT 'Website',
web_site VARCHAR(200) NOT NULL, logo_link VARCHAR(150),
description TEXT NOT NULL, status VARCHAR(50) NOT NULL DEFAULT 'Production');

CREATE SEQUENCE projects_skills_id;
CREATE TABLE projects_skills_assoc(id INT PRIMARY KEY NOT NULL DEFAULT nextval('projects_skills_id'),
skill_id INTEGER REFERENCES all_skills(id), project_id INTEGER REFERENCES projects(id));

CREATE SEQUENCE users_id;
CREATE TABLE users(id INTEGER PRIMARY KEY DEFAULT nextval('users_id'),
location VARCHAR(200), date DATE NOT NULL, time TIME NOT NULL, ip VARCHAR(50));