CREATE SEQUENCE education_id;
CREATE TABLE IF NOT EXISTS education(id INTEGER PRIMARY KEY DEFAULT nextval('education_id') NOT NULL,
name VARCHAR(200) NOT NULL , school_name VARCHAR(200), date_from DATE NOT NULL , date_to DATE, location VARCHAR(200));