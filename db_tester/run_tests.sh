#!/bin/bash
# Quick Start Script for Exercise Testing (Linux/Mac)
# =====================================================

echo ""
echo "================================================================================"
echo "                    Python Exercise QA Testing Suite"
echo "================================================================================"
echo ""

show_menu() {
    echo "Select an option:"
    echo ""
    echo "  1. Test Course 5, Lesson 6 (Default)"
    echo "  2. Test a specific exercise by ID"
    echo "  3. List all available courses"
    echo "  4. Batch test specific courses"
    echo "  5. Batch test ALL courses"
    echo "  6. Exit"
    echo ""
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1) test_default ;;
        2) test_single ;;
        3) list_courses ;;
        4) batch_specific ;;
        5) batch_all ;;
        6) exit 0 ;;
        *) echo "Invalid choice. Please try again." ; show_menu ;;
    esac
}

test_default() {
    echo ""
    echo "Testing Course 5, Lesson 6..."
    echo ""
    python db_tester/test_python_exercises.py
    read -p "Press Enter to continue..."
    show_menu
}

test_single() {
    echo ""
    read -p "Enter Exercise ID: " exercise_id
    echo ""
    echo "Testing Exercise $exercise_id..."
    echo ""
    python db_tester/test_validator.py $exercise_id
    read -p "Press Enter to continue..."
    show_menu
}

list_courses() {
    echo ""
    echo "Listing available courses and lessons..."
    echo ""
    python db_tester/batch_tester.py list
    read -p "Press Enter to continue..."
    show_menu
}

batch_specific() {
    echo ""
    echo "Running batch tests on specific courses..."
    echo "(Edit batch_tester.py to customize which courses to test)"
    echo ""
    python db_tester/batch_tester.py specific
    read -p "Press Enter to continue..."
    show_menu
}

batch_all() {
    echo ""
    echo "WARNING: This will test ALL courses and lessons!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        show_menu
        return
    fi
    echo ""
    echo "Running batch tests on ALL courses..."
    echo ""
    python db_tester/batch_tester.py all
    read -p "Press Enter to continue..."
    show_menu
}

# Start menu
show_menu
