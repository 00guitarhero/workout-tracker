import sqlite3
from datetime import date

def create_database():
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            exercise TEXT NOT NULL,
            weight INTEGER NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            FOREIGN KEY (session_id) REFERENCES workout_sessions(id)
        )
    """)

    connection.commit()
    connection.close()

def create_workout_session():
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    today = str(date.today())

    cursor.execute(
        "INSERT INTO workout_sessions (date) VALUES (?)",
        (today,)
    )

    session_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return session_id

def save_exercise(session_id, workout_data):
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO exercises (session_id, exercise, weight, sets, reps)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session_id,
        workout_data["exercise"],
        workout_data["weight"],
        workout_data["sets"],
        workout_data["reps"]
    ))

    connection.commit()
    connection.close()

def get_exercises(session_id):
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, exercise, weight, sets, reps
        FROM exercises
        WHERE session_id = ?
    """, (session_id,))

    rows = cursor.fetchall()

    exercises = []

    for row in rows:
        exercise = {
            "id": row[0],
            "exercise": row[1],
            "weight": row[2],
            "sets": row[3],
            "reps": row[4]
        }

        exercises.append(exercise)

    connection.close()

    return exercises

def remove_exercise(session_id):
    exercises = get_exercises(session_id)

    if not exercises:
        print("No exercises to remove.")
        return

    for index, exercise in enumerate(exercises, start=1):
        print(f"{index}. {exercise['exercise']}")

    try:
        choice = int(input("Enter the number of the exercise to remove: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice < 1 or choice > len(exercises):
        print("Invalid exercise number.")
        return

    exercise_id = exercises[choice - 1]["id"]

    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM exercises WHERE id = ? AND session_id = ?",
        (exercise_id, session_id)
    )

    connection.commit()
    connection.close()

    print("Exercise removed successfully!")

def edit_exercise(session_id):
    exercises = get_exercises(session_id)

    if not exercises:
        print("No exercises to edit.")
        return

    for index, exercise in enumerate(exercises, start=1):
        print(f"{index}. {exercise['exercise']}")

    try:
        choice = int(input("Enter the number of the exercise to edit: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    if choice < 1 or choice > len(exercises):
        print("Invalid exercise number.")
        return

    exercise = exercises[choice - 1]

    print("Press Enter to keep the current value.")

    new_name = input(
        f"Exercise name ({exercise['exercise']}): "
    )
    new_weight = input(
        f"Weight ({exercise['weight']}): "
    )
    new_sets = input(
        f"Sets ({exercise['sets']}): "
    )
    new_reps = input(
        f"Reps ({exercise['reps']}): "
    )

    if new_name:
        exercise["exercise"] = new_name

    try:
        if new_weight:
            exercise["weight"] = int(new_weight)
        if new_sets:
            exercise["sets"] = int(new_sets)
        if new_reps:
            exercise["reps"] = int(new_reps)
    except ValueError:
        print("Weight, sets, and reps must be whole numbers. No changes saved.")
        return

    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE exercises
        SET exercise = ?, weight = ?, sets = ?, reps = ?
        WHERE id = ? AND session_id = ?
    """, (
        exercise["exercise"],
        exercise["weight"],
        exercise["sets"],
        exercise["reps"],
        exercise["id"],
        session_id
    ))

    connection.commit()
    connection.close()

    print("Exercise updated successfully!")

def add_exercise():
    exercise = input("Exercise: ")

    while True:
        try:
            weight = int(input("Weight: "))
            break
        except ValueError:
            print("Please enter a valid number")
    while True:
        try:
            sets = int(input("Sets: "))
            break
        except ValueError:
            print("Please enter a valid number")
    while True:
        try:
            reps = int(input("Reps: "))
            break
        except ValueError:
            print("Please enter a valid number")

    workout_data = {
        "exercise": exercise,
        "weight": weight,
        "sets": sets,
        "reps": reps
    }

    return workout_data

def calculate_volume(workout):
    total_volume = 0

    for exercise in workout:
        exercise_volume = exercise["weight"] * exercise["sets"] * exercise["reps"]
        print(f'Total Volume for {exercise["exercise"]}: {exercise_volume} lbs')
        total_volume += exercise_volume
    print(f"Total Workout Volume: {total_volume} lbs")

def display_workout(workout):
    for i, exercise in enumerate(workout):
        print(f"{i+1}. {exercise['exercise']}")
        print(f"   Weight: {exercise['weight']} lbs")
        print(f"   Sets: {exercise['sets']}")
        print(f"   Reps: {exercise['reps']}")

def display_history():
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, date
        FROM workout_sessions
        ORDER BY date DESC, id DESC
    """)

    sessions = cursor.fetchall()
    connection.close()

    if not sessions:
        print("No workout history yet.")
        return

    for session in sessions:
        history_session_id = session[0]
        session_date = session[1]

        print(f"\nWorkout Date: {session_date}")

        exercises = get_exercises(history_session_id)

        if exercises:
            display_workout(exercises)
        else:
            print("No exercises recorded.")

def main():
    session_id = None

    while True:
        print("========================")
        print("     WORKOUT TRACKER")
        print("========================")
        print("1. Add Exercise")
        print("2. View Workout")
        print("3. Remove Exercise")
        print("4. Edit Exercise")
        print("5. View Volume")
        print("6. View Workout History")
        print("7. Exit")

        user_input = input("Choose an option: ")
        
        if user_input == "1":
            workout_data = add_exercise()

            if session_id is None:
                session_id = create_workout_session()

            save_exercise(session_id, workout_data)
            print("Exercise added successfully!")

        elif user_input == "2":
            if session_id is None:
                print("No exercises in this workout yet.")
            else:
                exercises = get_exercises(session_id)

                if not exercises:
                    print("No exercises in this workout yet.")
                else:
                    display_workout(exercises)

        elif user_input == "3":
            if session_id is None:
                print("No exercises in this workout yet.")
            else:
                remove_exercise(session_id)

        elif user_input == "4":
            if session_id is None:
                print("No exercises in this workout yet.")
            else:
                edit_exercise(session_id)

        elif user_input == "5":
            if session_id is None:
                print("No exercises in this workout yet.")
            else:
                exercises = get_exercises(session_id)

                if not exercises:
                    print("No exercises in this workout yet.")
                else:
                    calculate_volume(exercises)

        elif user_input == "6":
            display_history()

        elif user_input == "7":
            print("Workout tracker closed. Your data is saved.")
            break

        else:
            print("Invalid option. Please choose 1-7.")

main()