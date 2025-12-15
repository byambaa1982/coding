# Test solution for Exercise 27
# Format: function-based solution that returns values

def solution():
    # Create variables of different types
    student_name = "John Doe"
    student_id = 12345
    gpa = 3.75
    is_enrolled = True
    
    # Return a formatted string with all information
    result = f"""Student Name: {student_name} (Type: {type(student_name)})
Student ID: {student_id} (Type: {type(student_id)})
GPA: {gpa} (Type: {type(gpa)})
Enrolled: {is_enrolled} (Type: {type(is_enrolled)})"""
    
    return result

# Test it
if __name__ == "__main__":
    output = solution()
    print(output)
