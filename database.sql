CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    weight_kg DECIMAL
);

CREATE TABLE friends (
    user_id_1 INT REFERENCES users(user_id),
    user_id_2 INT REFERENCES users(user_id),
    PRIMARY KEY (user_id_1, user_id_2)
);

CREATE TABLE workouts (
    workout_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    workout_date DATE NOT NULL,
    duration_minutes INT
);

CREATE TABLE exercises (
    exercise_id SERIAL PRIMARY KEY,
    workout_id INT REFERENCES workouts(workout_id),
    exercise_name VARCHAR(255) NOT NULL,
    reps INT,
    sets INT,
    weight_kg DECIMAL
);

CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    goal_description TEXT NOT NULL,
    target_value INT,
    current_value INT DEFAULT 0
);