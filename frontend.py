import streamlit as st
import backend

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# --- Login/Signup Section ---
st.title("💪 Fitness Tracker Roshan Kumar S_30158")
if not st.session_state.logged_in:
    st.subheader("Login / Sign Up")
    email = st.text_input("Enter your email:")
    if st.button("Log In"):
        user = backend.get_user_by_email(email)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.user_email = user[2]
            st.success("Logged in successfully!")
            st.rerun()  # Corrected function call
        else:
            st.error("User not found. Please sign up.")
    
    with st.expander("Or, Sign Up for a new account"):
        name = st.text_input("Full Name")
        signup_email = st.text_input("Email")
        weight = st.number_input("Weight (kg)", min_value=0.0)
        if st.button("Sign Up"):
            if backend.create_user(name, signup_email, weight):
                st.success("Account created! Please log in.")
            else:
                st.error("Error creating account.")

# --- Main Application Sections (after login) ---
if st.session_state.logged_in:
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Go to", ["User Profile", "Workout Tracking", "Leaderboard", "Goals", "Business Insights"])

    # --- User Profile Section ---
    if app_mode == "User Profile":
        st.header("👤 Your Profile")
        user = backend.get_user_by_email(st.session_state.user_email)
        if user:
            st.write(f"**Name:** {user[1]}")
            st.write(f"**Email:** {user[2]}")
            st.write(f"**Weight:** {user[3]} kg")
            
        with st.expander("Update Profile"):
            new_name = st.text_input("New Name", value=user[1])
            new_weight = st.number_input("New Weight (kg)", value=user[3], min_value=0.0)
            if st.button("Update"):
                if backend.update_user_profile(st.session_state.user_id, new_name, new_weight):
                    st.success("Profile updated successfully!")
                    st.rerun()  # Corrected function call
                else:
                    st.error("Failed to update profile.")
        
        st.subheader("Connect with Friends")
        friend_email_to_add = st.text_input("Enter friend's email to add")
        if st.button("Add Friend"):
            if backend.add_friend(st.session_state.user_id, friend_email_to_add):
                st.success("Friend added!")
                st.rerun()  # Corrected function call
            else:
                st.error("Failed to add friend. Check the email address.")
        
        st.subheader("My Friends")
        friends_list = backend.get_friends(st.session_state.user_id)
        if friends_list:
            for friend in friends_list:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{friend[0]} ({friend[1]})")
                with col2:
                    if st.button("Remove", key=f"remove_{friend[2]}"):
                        if backend.remove_friend(st.session_state.user_id, friend[2]):
                            st.success("Friend removed.")
                            st.rerun()  # Corrected function call

    # --- Workout Tracking Section ---
    elif app_mode == "Workout Tracking":
        st.header("🏃‍♂️ Log a New Workout")
        with st.form("new_workout_form"):
            workout_date = st.date_input("Date")
            duration = st.number_input("Duration (minutes)", min_value=1)
            
            st.subheader("Add Exercises")
            exercises = []
            num_exercises = st.number_input("Number of exercises", min_value=1, value=1)
            for i in range(num_exercises):
                st.write(f"**Exercise #{i+1}**")
                name = st.text_input("Exercise Name", key=f"ex_name_{i}")
                reps = st.number_input("Reps", min_value=0, key=f"ex_reps_{i}")
                sets = st.number_input("Sets", min_value=0, key=f"ex_sets_{i}")
                weight = st.number_input("Weight (kg)", min_value=0.0, key=f"ex_weight_{i}")
                exercises.append({"name": name, "reps": reps, "sets": sets, "weight": weight})
            
            submitted = st.form_submit_button("Log Workout")
            if submitted:
                workout_id = backend.create_workout(st.session_state.user_id, workout_date, duration)
                if workout_id:
                    for ex in exercises:
                        backend.add_exercise(workout_id, ex['name'], ex['reps'], ex['sets'], ex['weight'])
                    st.success("Workout logged successfully!")
                    st.rerun()  # Corrected function call
                else:
                    st.error("Failed to log workout.")

        st.header("🏋️‍♂️ Your Workout History")
        history = backend.get_workout_history(st.session_state.user_id)
        if history:
            workouts = {}
            for row in history:
                date, duration, name, reps, sets, weight = row
                if date not in workouts:
                    workouts[date] = {"duration": duration, "exercises": []}
                workouts[date]["exercises"].append({"name": name, "reps": reps, "sets": sets, "weight": weight})
            
            for date, data in workouts.items():
                st.subheader(f"Workout on {date.strftime('%Y-%m-%d')} - {data['duration']} mins")
                for ex in data['exercises']:
                    st.write(f"- {ex['name']}: {ex['sets']} sets of {ex['reps']} reps at {ex['weight']} kg")
        else:
            st.info("No workout history found.")

    # --- Leaderboard Section ---
    elif app_mode == "Leaderboard":
        st.header("🏆 Friends Leaderboard")
        metric = st.radio("Rank by:", ("total_workouts", "total_minutes"))
        
        leaderboard_data = backend.get_leaderboard_by_metric(metric)
        if leaderboard_data:
            st.table(leaderboard_data)
        else:
            st.info("No leaderboard data available for this week.")

    # --- Goals Section ---
    elif app_mode == "Goals":
        st.header("🎯 My Fitness Goals")
        
        with st.expander("Set a New Goal"):
            goal_description = st.text_area("Goal Description (e.g., 'Workout 5 times a week')")
            target_value = st.number_input("Target Value", min_value=1)
            if st.button("Set Goal"):
                backend.create_goal(st.session_state.user_id, goal_description, target_value)
                st.success("Goal set successfully!")
                st.rerun()  # Corrected function call
        
        st.subheader("Your Active Goals")
        goals = backend.get_goals(st.session_state.user_id)
        if goals:
            for goal in goals:
                st.write(f"**Goal:** {goal[2]}")
                st.write(f"**Target:** {goal[3]}")
                current_value = st.number_input("Current Progress", value=goal[4], min_value=0, key=f"goal_{goal[0]}")
                if st.button("Update Progress", key=f"update_{goal[0]}"):
                    backend.update_goal_progress(goal[0], current_value)
                    st.success("Progress updated!")
                    st.rerun()  # Corrected function call
        else:
            st.info("You haven't set any goals yet.")

    # --- Business Insights Section ---
    elif app_mode == "Business Insights":
        st.header("📊 Business Insights")
        insights = backend.get_business_insights()
        
        if insights:
            st.metric(label="Total Users", value=insights["total_users"])
            st.metric(label="Total Workouts Logged", value=insights["total_workouts"])
            st.metric(label="Average Workout Duration (mins)", value=f"{insights['avg_workout_duration']:.2f}" if insights['avg_workout_duration'] else "N/A")
            st.metric(label="Maximum Reps in a Single Exercise", value=insights["max_reps"] if insights['max_reps'] else "N/A")
            st.metric(label="Minimum Weight Lifted (kg)", value=insights["min_weight_lifted"] if insights['min_weight_lifted'] else "N/A")