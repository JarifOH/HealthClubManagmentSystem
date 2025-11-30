-- MEMBERS
INSERT INTO Member (full_name, date_of_birth, gender, email, phone, goal_description, target_weight)
VALUES
('Alex Caruso', '1995-04-11', 'Male', 'alex@example.com', '555-1111', 'Lose weight and improve cardio', 200),
('Patricia Wanda', '1988-08-02', 'Female', 'wanda@example.com', '555-2222', 'Build muscle mass', 120),
('Ryan Rollins', '1999-12-15', 'Male', 'rollins@example.com', '555-3333', 'Improve endurance', 180);


-- HEALTH METRICS
INSERT INTO HealthMetric(member_id, weight, heart_rate, body_fat_percentage, notes)
VALUES
(1, 150.5, 72, 22.5, 'Good progress'),
(1, 148.9, 69, 22.1, 'Slight improvement'),
(2, 190.0, 85, 26.0, 'High HR observed');


-- TRAINERS
INSERT INTO Trainer(full_name, email, phone, specialization, employment_start_date)
VALUES
('David Walls', 'walls@fitclub.com', '555-4444', 'Strength Training', '2020-01-10'),
('Omar Hossain', 'hossain@fitclub.com', '555-5555', 'HIIT & Cardio', '2021-06-20');


-- TRAINER AVAILABILITY
INSERT INTO TrainerAvailability(trainer_id, day_of_week, start_time, end_time)
VALUES
(1, 'Monday', '09:00', '12:00'),
(1, 'Wednesday', '13:00', '17:00'),
(2, 'Tuesday', '08:00', '12:00');


-- ROOMS
INSERT INTO Room(name, room_type, capacity)
VALUES
('Studio A', 'Yoga/HIIT', 20),
('Studio B', 'Strength Room', 15);


-- GROUP CLASSES
INSERT INTO GroupClass(title, description, start_time, end_time, capacity, trainer_id, room_id)
VALUES
('Morning HIIT', 'High intensity interval training session', '2025-12-02 09:00', '2025-12-02 10:00', 15, 2, 1),
('Strength 101', 'Beginner strength-building class', '2025-12-03 14:00', '2025-12-03 15:00', 12, 1, 2);


-- CLASS REGISTRATIONS
INSERT INTO ClassRegistration(member_id, class_id)
VALUES
(1, 1),
(2, 1),
(3, 2);


-- EQUIPMENT
INSERT INTO Equipment(room_id, name, equipment_type, status)
VALUES
(2, 'Bench Press #1', 'Strength Machine', 'Working'),
(2, 'Dumbbell Rack', 'Weights', 'Working'),
(1, 'Treadmill #3', 'Cardio Machine', 'Needs Maintenance');


-- EQUIPMENT MAINTENANCE
INSERT INTO EquipmentMaintenance(equipment_id, issue_description, status)
VALUES
(3, 'Motor making loud noise', 'Open'),
(3, 'Belt slipping intermittently', 'Open');


-- PT SESSIONS
INSERT INTO PTSession(member_id, trainer_id, room_id, start_time, end_time, status)
VALUES
(1, 1, 2, '2025-12-05 10:00', '2025-12-05 11:00', 'Scheduled'),
(2, 2, 1, '2025-12-06 09:00', '2025-12-06 10:00', 'Scheduled');
