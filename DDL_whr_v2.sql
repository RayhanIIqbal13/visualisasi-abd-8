-- ================================================
-- WORLD HAPPINESS REPORT DATABASE SCHEMA (FINAL)
-- ================================================

-- =============================
-- 1. TABEL REGION
-- =============================
CREATE TABLE IF NOT EXISTS region (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL UNIQUE
);

COMMENT ON COLUMN region.region_name IS 'Nama region sesuai atribut Regional Indicator dalam dataset';

-- 🔍 Index tambahan
CREATE INDEX idx_region_name ON region (region_name);



-- =============================
-- 2. TABEL COUNTRY
-- =============================
CREATE TABLE IF NOT EXISTS country (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    region_id INT NOT NULL,
    UNIQUE(country_name),
    CONSTRAINT fk_region
        FOREIGN KEY (region_id)
        REFERENCES region(region_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

COMMENT ON COLUMN country.country_name IS 'Nama negara';
COMMENT ON COLUMN country.region_id IS 'Relasi ke tabel region';

-- 🔍 Index tambahan
CREATE INDEX idx_country_name ON country (country_name);
CREATE INDEX idx_country_region_id ON country (region_id);



-- =============================
-- 3. TABEL HAPPINESS_REPORT
-- =============================
CREATE TABLE IF NOT EXISTS happiness_report (
    report_id SERIAL PRIMARY KEY,
    country_id INT NOT NULL,
    year INT NOT NULL,
    ranking INT,
    happiness_score DECIMAL(5,3),
    dystopia_residual DECIMAL(5,3),
    UNIQUE(country_id, year),
    CONSTRAINT fk_country
        FOREIGN KEY (country_id)
        REFERENCES country(country_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

COMMENT ON COLUMN happiness_report.happiness_score IS 'Nilai Happiness Score (Ladder Score)';
COMMENT ON COLUMN happiness_report.dystopia_residual IS 'Nilai Dystopia Residual';
COMMENT ON COLUMN happiness_report.ranking IS 'Posisi ranking negara';

-- 🔍 Index tambahan
CREATE INDEX idx_happiness_year ON happiness_report (year);
CREATE INDEX idx_happiness_country_id ON happiness_report (country_id);
CREATE INDEX idx_happiness_ranking ON happiness_report (ranking);
CREATE INDEX idx_happiness_score ON happiness_report (happiness_score);



-- =============================
-- 4. TABEL ECONOMIC_INDICATOR
-- =============================
CREATE TABLE IF NOT EXISTS economic_indicator (
    economic_id SERIAL PRIMARY KEY,
    report_id INT NOT NULL UNIQUE,
    gdp_per_capita DECIMAL(5,3),
    CONSTRAINT fk_econ_report
        FOREIGN KEY (report_id)
        REFERENCES happiness_report(report_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

COMMENT ON COLUMN economic_indicator.gdp_per_capita IS 'GDP per Capita negara';

-- 🔍 Index tambahan
CREATE INDEX idx_econ_report_id ON economic_indicator (report_id);
CREATE INDEX idx_econ_gdp ON economic_indicator (gdp_per_capita);



-- =============================
-- 5. TABEL SOCIAL_INDICATOR
-- =============================
CREATE TABLE IF NOT EXISTS social_indicator (
    social_id SERIAL PRIMARY KEY,
    report_id INT NOT NULL UNIQUE,
    social_support DECIMAL(5,3),
    healthy_life_expectancy DECIMAL(5,3),
    freedom_to_make_life_choices DECIMAL(5,3),
    CONSTRAINT fk_social_report
        FOREIGN KEY (report_id)
        REFERENCES happiness_report(report_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

COMMENT ON COLUMN social_indicator.social_support IS 'Tingkat dukungan sosial';
COMMENT ON COLUMN social_indicator.healthy_life_expectancy IS 'Harapan hidup sehat';
COMMENT ON COLUMN social_indicator.freedom_to_make_life_choices IS 'Indeks kebebasan memilih';

-- 🔍 Index tambahan
CREATE INDEX idx_social_report_id ON social_indicator (report_id);
CREATE INDEX idx_social_support ON social_indicator (social_support);
CREATE INDEX idx_social_life_expectancy ON social_indicator (healthy_life_expectancy);
CREATE INDEX idx_social_freedom ON social_indicator (freedom_to_make_life_choices);



-- =============================
-- 6. TABEL PERCEPTION_INDICATOR
-- =============================
CREATE TABLE IF NOT EXISTS perception_indicator (
    perception_id SERIAL PRIMARY KEY,
    report_id INT NOT NULL UNIQUE,
    generosity DECIMAL(5,3),
    perceptions_of_corruption DECIMAL(5,3),
    CONSTRAINT fk_perception_report
        FOREIGN KEY (report_id)
        REFERENCES happiness_report(report_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

COMMENT ON COLUMN perception_indicator.generosity IS 'Tingkat kemurahan hati masyarakat';
COMMENT ON COLUMN perception_indicator.perceptions_of_corruption IS 'Persepsi tentang tingkat korupsi';

-- 🔍 Index tambahan
CREATE INDEX idx_perception_report_id ON perception_indicator (report_id);
CREATE INDEX idx_perception_generosity ON perception_indicator (generosity);
CREATE INDEX idx_perception_corruption ON perception_indicator (perceptions_of_corruption);
