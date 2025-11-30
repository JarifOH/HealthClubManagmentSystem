-- DROP TABLES (clean reset)
DROP TABLE IF EXISTS EquipmentMaintenance CASCADE;
DROP TABLE IF EXISTS Equipment CASCADE;
DROP TABLE IF EXISTS PTSession CASCADE;
DROP TABLE IF EXISTS TrainerAvailability CASCADE;
DROP TABLE IF EXISTS ClassRegistration CASCADE;
DROP TABLE IF EXISTS GroupClass CASCADE;
DROP TABLE IF EXISTS Room CASCADE;
DROP TABLE IF EXISTS HealthMetric CASCADE;
DROP TABLE IF EXISTS Trainer CASCADE;
DROP TABLE IF EXISTS Member CASCADE;


-- MEMBER
CREATE TABLE Member (
    member_id          SERIAL PRIMARY KEY,
    full_name          VARCHAR(100) NOT NULL,
    date_of_birth      DATE,
    gender             VARCHAR(20),
    email              VARCHAR(100) UNIQUE NOT NULL,
    phone              VARCHAR(20),
    join_date          DATE DEFAULT CURRENT_DATE,
    goal_description   TEXT,
    target_weight      DECIMAL(5,2)
);


-- TRAINER
CREATE TABLE Trainer (
    trainer_id              SERIAL PRIMARY KEY,
    full_name               VARCHAR(100) NOT NULL,
    email                   VARCHAR(100),
    phone                   VARCHAR(20),
    specialization          VARCHAR(100),
    employment_start_date   DATE
);


-- ROOM
CREATE TABLE Room (
    room_id     SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    room_type   VARCHAR(50),
    capacity    INT CHECK(capacity > 0)
);


-- GROUP CLASS
CREATE TABLE GroupClass (
    class_id        SERIAL PRIMARY KEY,
    title           VARCHAR(100) NOT NULL,
    description     TEXT,
    start_time      TIMESTAMP NOT NULL,
    end_time        TIMESTAMP NOT NULL,
    capacity        INT CHECK (capacity > 0),
    trainer_id      INT REFERENCES Trainer(trainer_id) ON DELETE SET NULL,
    room_id         INT REFERENCES Room(room_id) ON DELETE SET NULL,
    CHECK (end_time > start_time)
);


-- CLASS REGISTRATION
CREATE TABLE ClassRegistration (
    registration_id     SERIAL PRIMARY KEY,
    member_id           INT NOT NULL REFERENCES Member(member_id) ON DELETE CASCADE,
    class_id            INT NOT NULL REFERENCES GroupClass(class_id) ON DELETE CASCADE,
    registration_time   TIMESTAMP DEFAULT NOW(),
    UNIQUE(member_id, class_id)
);


-- HEALTH METRIC
CREATE TABLE HealthMetric (
    metric_id           SERIAL PRIMARY KEY,
    member_id           INT NOT NULL REFERENCES Member(member_id) ON DELETE CASCADE,
    recorded_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    weight              DECIMAL(5,2),
    heart_rate          INT,
    body_fat_percentage DECIMAL(5,2),
    notes               TEXT
);


-- PT SESSION (Personal Training Session)
CREATE TABLE PTSession (
    pt_session_id   SERIAL PRIMARY KEY,
    member_id       INT NOT NULL REFERENCES Member(member_id) ON DELETE CASCADE,
    trainer_id      INT NOT NULL REFERENCES Trainer(trainer_id) ON DELETE CASCADE,
    room_id         INT REFERENCES Room(room_id) ON DELETE SET NULL,     -- FIXED
    start_time      TIMESTAMP NOT NULL,
    end_time        TIMESTAMP NOT NULL,
    status          VARCHAR(20) DEFAULT 'Scheduled',
    CHECK (end_time > start_time)
);


-- TRAINER AVAILABILITY
CREATE TABLE TrainerAvailability (
    availability_id     SERIAL PRIMARY KEY,
    trainer_id          INT NOT NULL REFERENCES Trainer(trainer_id) ON DELETE CASCADE,
    day_of_week         VARCHAR(20) NOT NULL,
    start_time          TIME NOT NULL,
    end_time            TIME NOT NULL,
    CHECK (end_time > start_time)
);


CREATE INDEX idx_trainer_avail ON TrainerAvailability(trainer_id, day_of_week, start_time);


-- TRIGGER FUNCTION
CREATE OR REPLACE FUNCTION prevent_availability_overlap()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM TrainerAvailability ta
        WHERE ta.trainer_id = NEW.trainer_id
        AND ta.day_of_week = NEW.day_of_week
        AND (NEW.start_time, NEW.end_time) OVERLAPS (ta.start_time, ta.end_time)
        AND ta.availability_id <> NEW.availability_id
    ) THEN
        RAISE EXCEPTION 'Trainer availability overlaps with existing availability.';
    END IF;


    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- TRIGGER
CREATE TRIGGER trg_prevent_availability_overlap
BEFORE INSERT OR UPDATE ON TrainerAvailability
FOR EACH ROW EXECUTE FUNCTION prevent_availability_overlap();


-- EQUIPMENT
CREATE TABLE Equipment (
    equipment_id        SERIAL PRIMARY KEY,
    room_id             INT REFERENCES Room(room_id) ON DELETE SET NULL,
    name                VARCHAR(100) NOT NULL,
    equipment_type      VARCHAR(100),
    status              VARCHAR(50) DEFAULT 'Working'
);


-- EQUIPMENT MAINTENANCE
CREATE TABLE EquipmentMaintenance (
    maintenance_id      SERIAL PRIMARY KEY,
    equipment_id        INT NOT NULL REFERENCES Equipment(equipment_id) ON DELETE CASCADE,
    reported_at         TIMESTAMP DEFAULT NOW(),
    issue_description   TEXT NOT NULL,
    status              VARCHAR(30) DEFAULT 'Open',
    assigned_to         VARCHAR(100),
    resolved_at         TIMESTAMP
);


-- VIEW: Member Dashboard
CREATE OR REPLACE VIEW member_dashboard_view AS
SELECT
    m.member_id,
    m.full_name,
    m.goal_description,
    m.target_weight,


    -- Latest health metric
    (SELECT weight FROM HealthMetric hm
     WHERE hm.member_id = m.member_id
     ORDER BY hm.recorded_at DESC LIMIT 1) AS latest_weight,


    (SELECT heart_rate FROM HealthMetric hm
     WHERE hm.member_id = m.member_id
     ORDER BY hm.recorded_at DESC LIMIT 1) AS latest_heart_rate,


    (SELECT body_fat_percentage FROM HealthMetric hm
     WHERE hm.member_id = m.member_id
     ORDER BY hm.recorded_at DESC LIMIT 1) AS latest_body_fat,


    -- Upcoming classes
    (SELECT COUNT(*) FROM ClassRegistration cr
     JOIN GroupClass gc ON gc.class_id = cr.class_id
     WHERE cr.member_id = m.member_id
     AND gc.start_time > NOW()) AS upcoming_classes


FROM Member m;
