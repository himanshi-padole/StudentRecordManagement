
import json
import os

# Hash table settings
TABLE_SIZE = 10
FILE_NAME = "student_database.json"

# Hash table using Separate Chaining
hash_table = [[] for _ in range(TABLE_SIZE)]


# Hash function
def hash_function(roll_no):
    hash_value = 0

    for character in roll_no:
        hash_value += ord(character)

    return hash_value % TABLE_SIZE


# Search record using hashing
def search_record(roll_no):
    index = hash_function(roll_no)

    for student in hash_table[index]:
        if student["roll_no"] == roll_no:
            return student

    return None


# Save database
def save_database():
    all_students = []

    for bucket in hash_table:
        for student in bucket:
            all_students.append(student)

    with open(FILE_NAME, "w") as file:
        json.dump(all_students, file, indent=4)


# Load database
def load_database():
    if not os.path.exists(FILE_NAME):
        return

    try:
        with open(FILE_NAME, "r") as file:
            all_students = json.load(file)

        for student in all_students:
            index = hash_function(student["roll_no"])
            hash_table[index].append(student)

    except (json.JSONDecodeError, OSError, KeyError, TypeError):
        print("Warning: Could not load the database.")


# Add student
def add_student():
    print("\n--- ADD STUDENT ---")

    roll_no = input("Enter Roll Number: ").strip()

    if not roll_no:
        print("Roll number cannot be empty.")
        return

    if search_record(roll_no):
        print("Roll number already exists!")
        return

    name = input("Enter Student Name: ").strip()
    department = input("Enter Department: ").strip()

    if not name or not department:
        print("Name and department cannot be empty.")
        return

    try:
        year = int(input("Enter Year: "))
        marks = float(input("Enter Marks (0-100): "))

        if year < 1 or not 0 <= marks <= 100:
            print("Invalid year or marks.")
            return

    except ValueError:
        print("Please enter valid numeric values.")
        return

    student = {
        "roll_no": roll_no,
        "name": name,
        "department": department,
        "year": year,
        "marks": marks
    }

    index = hash_function(roll_no)
    hash_table[index].append(student)

    save_database()

    print("Student added successfully!")
    print("Hash bucket index:", index)


# Display all students
def display_students():
    print("\n--- ALL STUDENT RECORDS ---")

    found = False

    print("-" * 75)
    print(
        f"{'Roll No':<12}{'Name':<20}"
        f"{'Department':<15}{'Year':<8}{'Marks':<10}"
    )
    print("-" * 75)

    for bucket in hash_table:
        for student in bucket:
            found = True
            print(
                f"{student['roll_no']:<12}"
                f"{student['name']:<20}"
                f"{student['department']:<15}"
                f"{student['year']:<8}"
                f"{student['marks']:<10.2f}"
            )

    if not found:
        print("No student records found.")

    print("-" * 75)


# Search student
def search_student():
    print("\n--- SEARCH STUDENT ---")

    roll_no = input("Enter Roll Number: ").strip()
    student = search_record(roll_no)

    if student:
        print("\nStudent Record Found!")
        print("Roll Number:", student["roll_no"])
        print("Name:", student["name"])
        print("Department:", student["department"])
        print("Year:", student["year"])
        print("Marks:", student["marks"])
    else:
        print("Student record not found.")


# Update student
def update_student():
    print("\n--- UPDATE STUDENT ---")

    roll_no = input("Enter Roll Number to update: ").strip()
    student = search_record(roll_no)

    if not student:
        print("Student record not found.")
        return

    print("Press Enter to keep the current value.")

    name = input(f"Name [{student['name']}]: ").strip()
    department = input(
        f"Department [{student['department']}]: "
    ).strip()
    year_text = input(f"Year [{student['year']}]: ").strip()
    marks_text = input(f"Marks [{student['marks']}]: ").strip()

    try:
        year = int(year_text) if year_text else student["year"]
        marks = float(marks_text) if marks_text else student["marks"]

        if year < 1 or not 0 <= marks <= 100:
            print("Invalid year or marks. Update cancelled.")
            return

    except ValueError:
        print("Invalid numeric input. Update cancelled.")
        return

    student["name"] = name if name else student["name"]
    student["department"] = (
        department if department else student["department"]
    )
    student["year"] = year
    student["marks"] = marks

    save_database()
    print("Student record updated successfully!")


# Delete student
def delete_student():
    print("\n--- DELETE STUDENT ---")

    roll_no = input("Enter Roll Number to delete: ").strip()
    index = hash_function(roll_no)

    for student in hash_table[index]:
        if student["roll_no"] == roll_no:
            print("Student Name:", student["name"])

            confirm = input(
                "Confirm deletion? (yes/no): "
            ).strip().lower()

            if confirm == "yes":
                hash_table[index].remove(student)
                save_database()
                print("Student deleted successfully!")
            else:
                print("Deletion cancelled.")

            return

    print("Student record not found.")


# Display hash table
def display_hash_table():
    print("\n--- HASH TABLE ---")
    print("Table size:", TABLE_SIZE)
    print("Collision handling: Separate Chaining")

    for index, bucket in enumerate(hash_table):
        print(f"Bucket {index}:", end=" ")

        if not bucket:
            print("Empty")
        else:
            records = []

            for student in bucket:
                records.append(
                    f"{student['roll_no']} ({student['name']})"
                )

            print(" -> ".join(records))


# NEW FEATURE 1: Find topper
def find_topper():
    print("\n--- FIND TOPPER ---")

    all_students = [
        student
        for bucket in hash_table
        for student in bucket
    ]

    if not all_students:
        print("No student records available.")
        return

    highest_marks = max(
        student["marks"] for student in all_students
    )

    print("Highest Marks:", f"{highest_marks:.2f}")
    print("Topper(s):")

    for student in all_students:
        if student["marks"] == highest_marks:
            print("------------------------------")
            print("Roll Number:", student["roll_no"])
            print("Name:", student["name"])
            print("Department:", student["department"])
            print("Year:", student["year"])
            print("Marks:", f"{student['marks']:.2f}")


# NEW FEATURE 2: Calculate average marks
def calculate_average():
    print("\n--- CALCULATE AVERAGE MARKS ---")

    all_students = [
        student
        for bucket in hash_table
        for student in bucket
    ]

    if not all_students:
        print("No student records available.")
        return

    total_marks = sum(
        student["marks"] for student in all_students
    )

    total_students = len(all_students)
    average = total_marks / total_students

    print("Total Students:", total_students)
    print("Total Marks:", f"{total_marks:.2f}")
    print("Average Marks:", f"{average:.2f}")


# Main menu
def main():
    load_database()

    while True:
        print("\n========================================")
        print(" STUDENT DATABASE MANAGEMENT SYSTEM")
        print("          USING HASHING")
        print("========================================")
        print("1. Add Student")
        print("2. Display All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Display Hash Table")
        print("7. Find Topper")
        print("8. Calculate Average Marks")
        print("9. Exit")
        print("========================================")

        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            display_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            update_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            display_hash_table()
        elif choice == "7":
            find_topper()
        elif choice == "8":
            calculate_average()
        elif choice == "9":
            print("Database saved. Thank you!")
            break
        else:
            print("Invalid choice. Please select from 1 to 9.")


if __name__ == "__main__":
    main()
