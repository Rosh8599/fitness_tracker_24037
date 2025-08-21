import psycopg2
from datetime import datetime, timedelta

def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="fitnesstracker",
            user="postgres",
            password="Rosh@8599",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# --- CRUD Operations for Users ---
def create_user(name, email, weight):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, weight_kg) VALUES (%s, %s, %s)",
                (name, email, weight)
            )
            conn.commit()
            return True
    return False

def get_user_by_email(email):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            return user
    return None

def update_user_profile(user_id, name, weight):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET name = %s, weight_kg = %s WHERE user_id = %s",
                (name, weight, user_id)
            )
            conn.commit()
            return True
    return False

# --- CRUD Operations for Workouts and Exercises ---
def create_workout(user_id, date, duration):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO workouts (user_id, workout_date, duration_minutes) VALUES (%s, %s, %s) RETURNING workout_id",
                (user_id, date, duration)
            )
            workout_id = cur.fetchone()[0]
            conn.commit()
            return workout_id
    return None

def add_exercise(workout_id, name, reps, sets, weight):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO exercises (workout_id, exercise_name, reps, sets, weight_kg) VALUES (%s, %s, %s, %s, %s)",
                (workout_id, name, reps, sets, weight)
            )
            conn.commit()

def get_workout_history(user_id):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT w.workout_date, w.duration_minutes, e.exercise_name, e.reps, e.sets, e.weight_kg "
                "FROM workouts w JOIN exercises e ON w.workout_id = e.workout_id "
                "WHERE w.user_id = %s ORDER BY w.workout_date DESC",
                (user_id,)
            )
            return cur.fetchall()
    return []

# --- CRUD Operations for Friends ---
def add_friend(user_id, friend_email):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE email = %s", (friend_email,))
            friend_id = cur.fetchone()
            if friend_id:
                cur.execute(
                    "INSERT INTO friends (user_id_1, user_id_2) VALUES (%s, %s)",
                    (user_id, friend_id[0])
                )
                conn.commit()
                return True
    return False

def remove_friend(user_id, friend_id):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM friends WHERE (user_id_1 = %s AND user_id_2 = %s) OR (user_id_1 = %s AND user_id_2 = %s)",
                (user_id, friend_id, friend_id, user_id)
            )
            conn.commit()
            return True
    return False

def get_friends(user_id):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT u.name, u.email, u.user_id FROM users u "
                "JOIN friends f ON (u.user_id = f.user_id_1 AND f.user_id_2 = %s) OR (u.user_id = f.user_id_2 AND f.user_id_1 = %s)",
                (user_id, user_id)
            )
            return cur.fetchall()
    return []

# --- CRUD Operations for Goals ---
def create_goal(user_id, description, target_value):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO goals (user_id, goal_description, target_value) VALUES (%s, %s, %s)",
                (user_id, description, target_value)
            )
            conn.commit()

def get_goals(user_id):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM goals WHERE user_id = %s", (user_id,))
            return cur.fetchall()
    return []

def update_goal_progress(goal_id, current_value):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE goals SET current_value = %s WHERE goal_id = %s",
                (current_value, goal_id)
            )
            conn.commit()

# --- Business Insights Functions ---
def get_business_insights():
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            # Total users
            cur.execute("SELECT COUNT(*) FROM users")
            total_users = cur.fetchone()[0]

            # Total workouts
            cur.execute("SELECT COUNT(*) FROM workouts")
            total_workouts = cur.fetchone()[0]

            # Average workout duration
            cur.execute("SELECT AVG(duration_minutes) FROM workouts")
            avg_duration = cur.fetchone()[0]

            # Max reps in a single exercise
            cur.execute("SELECT MAX(reps) FROM exercises")
            max_reps = cur.fetchone()[0]
            
            # Min weight lifted in a single exercise
            cur.execute("SELECT MIN(weight_kg) FROM exercises")
            min_weight = cur.fetchone()[0]
            
            return {
                "total_users": total_users,
                "total_workouts": total_workouts,
                "avg_workout_duration": avg_duration,
                "max_reps": max_reps,
                "min_weight_lifted": min_weight
            }
    return {}

# --- Leaderboard Function ---
def get_leaderboard_by_metric(metric="total_minutes"):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            # Get the date one week ago
            one_week_ago = datetime.now() - timedelta(days=7)
            
            if metric == "total_minutes":
                cur.execute(
                    "SELECT u.name, SUM(w.duration_minutes) AS total_minutes "
                    "FROM users u JOIN workouts w ON u.user_id = w.user_id "
                    "WHERE w.workout_date >= %s "
                    "GROUP BY u.name ORDER BY total_minutes DESC",
                    (one_week_ago,)
                )
                return cur.fetchall()
            
            elif metric == "total_workouts":
                cur.execute(
                    "SELECT u.name, COUNT(w.workout_id) AS total_workouts "
                    "FROM users u JOIN workouts w ON u.user_id = w.user_id "
                    "WHERE w.workout_date >= %s "
                    "GROUP BY u.name ORDER BY total_workouts DESC",
                    (one_week_ago,)
                )
                return cur.fetchall()
    return []