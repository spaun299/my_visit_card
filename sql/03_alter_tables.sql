ALTER TABLE experience ADD COLUMN web_site VARCHAR(50);
ALTER TABLE projects ADD COLUMN company_id INTEGER REFERENCES experience(id);
