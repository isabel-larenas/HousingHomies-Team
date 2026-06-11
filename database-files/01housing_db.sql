DROP DATABASE IF EXISTS housing_db;
CREATE DATABASE IF NOT EXISTS housing_db;
USE housing_db;

CREATE TABLE country (
    country_id INTEGER PRIMARY KEY,
    country_name VARCHAR(30) NOT NULL,
    country_code VARCHAR(10) NOT NULL
);

CREATE TABLE social_indicator_types (
    sit_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE social_indicator_stats (
    stats_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    country_id INTEGER NOT NULL,
    sit_id INTEGER NOT NULL,
    year YEAR,
    value DECIMAL,
    unit VARCHAR(50),

    CONSTRAINT fk_sis_country FOREIGN KEY (country_id) REFERENCES country (country_id),
    CONSTRAINT fk_sis_sit FOREIGN KEY (sit_id) REFERENCES social_indicator_types (sit_id)
);

CREATE TABLE university (
    university_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    country_id INTEGER NOT NULL,
    university_name VARCHAR(150) NOT NULL,
    city_name VARCHAR(30),
    address VARCHAR(250),

    CONSTRAINT fk_uni_country FOREIGN KEY (country_id) REFERENCES country (country_id)
);

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    university_id INTEGER,
    country_id INTEGER,
    name VARCHAR(100),
    role VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    max_budget DECIMAL,
    max_distance_km DECIMAL,

    CONSTRAINT fk_user_country FOREIGN KEY (country_id) REFERENCES country (country_id),
    CONSTRAINT fk_user_uni FOREIGN KEY (university_id) REFERENCES university (university_id)
);

CREATE TABLE listing (
    listing_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200),
    country_id INTEGER,
    associated_university_id INTEGER,
    user_id INTEGER,
    price DECIMAL,
    property_type VARCHAR(50),
    city_name VARCHAR(50),

    CONSTRAINT fk_listing_country FOREIGN KEY (country_id) REFERENCES country (country_id),
    CONSTRAINT fk_listing_uni FOREIGN KEY (associated_university_id) REFERENCES university (university_id),
    CONSTRAINT fk_listing_user FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    listing_id INTEGER NOT NULL,
    rating INTEGER,
    comment VARCHAR(2000),

    CONSTRAINT fk_reviews_listing FOREIGN KEY (listing_id) REFERENCES listing (listing_id)
);

CREATE TABLE favorites (
    user_id INT,
    listing_id INT,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, listing_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (listing_id) REFERENCES listing(listing_id)
);

CREATE TABLE funding (
    funding_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    country_id INTEGER NOT NULL,
    year YEAR,
    amount DECIMAL,
    program VARCHAR(100),
    agency VARCHAR(100),

    CONSTRAINT fk_funding_country FOREIGN KEY (country_id) REFERENCES country (country_id)
);

CREATE TABLE funding_draft (
    draft_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    country_id INT,
    program VARCHAR(255),
    amount DECIMAL(10,2),
    indicators_targeted VARCHAR(255),
    demographics_targeted VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE student_model_params (
    id INT PRIMARY KEY AUTO_INCREMENT,
    beta_vals TEXT NOT NULL,
    scaler_mean TEXT NOT NULL,
    scaler_std TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gov_model_params (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ga_beta_vals TEXT NOT NULL,
    ga_scaler_mean TEXT NOT NULL,
    ga_scaler_std TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);