-- PostgreSQL version of your schema

CREATE TABLE schools(
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    canvas_link TEXT,  
    address TEXT
);

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    phone_number TEXT UNIQUE,
    email_address TEXT UNIQUE,
    school_id INTEGER,
    created_date TEXT,
    FOREIGN KEY (school_id) REFERENCES schools(id)
);

CREATE TABLE sessions(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id TEXT UNIQUE,
    expiry TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE reminders(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    days_ahead INTEGER,
    reminder_number INTEGER CHECK(reminder_number BETWEEN 1 AND 360), -- Limit to a year ahead
    special INTEGER GENERATED ALWAYS AS (CASE WHEN reminder_number = 4 THEN 1 ELSE 0 END) STORED, -- Changed VIRTUAL to STORED
    FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT unique_days_user_pair UNIQUE (user_id, reminder_number)
);

CREATE TABLE tokens(
    id SERIAL PRIMARY KEY,
    token TEXT,
    user_id INTEGER UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE notification_preferences(
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
    email_preference INTEGER,
    phone_preference INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE last_saved_reminder(
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
    details TEXT,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE last_sent_noti(
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
    date TEXT,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE reminder_schedule(
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
    time TEXT DEFAULT '8:00 AM',
    timezone TEXT DEFAULT 'UTC',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE canvas_call_log(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    reason TEXT,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE password_log(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    old_password TEXT,
    new_password TEXT,
    change_date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes to help speed up commonly queried columns
CREATE INDEX school_search 
ON schools(name, canvas_link, address);

CREATE INDEX reminder_search
ON reminders(days_ahead, special);

CREATE INDEX user_search
ON users(username, password, phone_number, email_address, created_date);

CREATE INDEX canvas_api_search
ON tokens(token);

CREATE INDEX canvas_call_log_search
ON canvas_call_log(reason, date);

CREATE INDEX password_log_search
ON password_log(change_date);

CREATE INDEX last_sent_noti_search
ON last_sent_noti(date, details);

CREATE INDEX notification_preferences_search
ON notification_preferences(email_preference, phone_preference);

-- A view to show students and their school
CREATE VIEW school_user_view AS 
SELECT  
    users.username, 
    schools.name AS school_name
FROM users 
JOIN schools ON schools.id = users.school_id;

CREATE VIEW users_schools_tokens_reminders_view AS
SELECT
    users.id,
    schools.canvas_link as school_url,
    tokens.token,
    reminders.days_ahead,
    reminders.special
FROM users
INNER JOIN schools ON schools.id = users.school_id
INNER JOIN reminders ON reminders.user_id = users.id
INNER JOIN tokens ON tokens.user_id = reminders.user_id;

CREATE VIEW users_np_lsr_view AS
SELECT
    users.id,
    notification_preferences.email_preference,
    notification_preferences.phone_preference,
    users.phone_number,
    users.email_address,
    last_saved_reminder.details
FROM users
INNER JOIN notification_preferences ON notification_preferences.user_id = users.id
INNER JOIN last_saved_reminder ON last_saved_reminder.user_id = notification_preferences.user_id;

-- Triggers for PostgreSQL (syntax is different)
CREATE OR REPLACE FUNCTION log_password_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.password != NEW.password THEN
        INSERT INTO password_log(user_id, old_password, new_password, change_date)
        VALUES (OLD.id, OLD.password, NEW.password, CURRENT_TIMESTAMP);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER password_logs_trigger
AFTER UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION log_password_change();

CREATE OR REPLACE FUNCTION create_notification_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO notification_preferences(user_id, email_preference, phone_preference)
    VALUES (NEW.id, 0, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notification_preferences_trigger
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_notification_preferences();

CREATE OR REPLACE FUNCTION create_reminder_schedule()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO reminder_schedule(user_id, time, timezone)
    VALUES (NEW.id, '12:00 PM', 'UTC');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reminder_schedule_trigger
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_reminder_schedule();

-- Insert schools
INSERT INTO schools(id, name, canvas_link, address)
    VALUES (1, 'mdc', 'https://mdc.instructure.com/', '11380 NW 27th Ave');

INSERT INTO schools(id, name, canvas_link, address)
    VALUES (2, 'fiu', 'https://mdc.instructure.com/', '11380 NW 27th Ave');