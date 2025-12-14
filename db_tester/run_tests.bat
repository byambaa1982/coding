@echo off
REM Quick Start Script for Exercise Testing
REM ========================================

echo.
echo ================================================================================
echo                     Python Exercise QA Testing Suite
echo ================================================================================
echo.

:menu
echo Select an option:
echo.
echo   1. Test Course 5, Lesson 6 (Default)
echo   2. Test a specific exercise by ID
echo   3. List all available courses
echo   4. Batch test specific courses
echo   5. Batch test ALL courses
echo   6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto test_default
if "%choice%"=="2" goto test_single
if "%choice%"=="3" goto list_courses
if "%choice%"=="4" goto batch_specific
if "%choice%"=="5" goto batch_all
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
goto menu

:test_default
echo.
echo Testing Course 5, Lesson 6...
echo.
python db_tester\test_python_exercises.py
pause
goto menu

:test_single
echo.
set /p exercise_id="Enter Exercise ID: "
echo.
echo Testing Exercise %exercise_id%...
echo.
python db_tester\test_validator.py %exercise_id%
pause
goto menu

:list_courses
echo.
echo Listing available courses and lessons...
echo.
python db_tester\batch_tester.py list
pause
goto menu

:batch_specific
echo.
echo Running batch tests on specific courses...
echo (Edit batch_tester.py to customize which courses to test)
echo.
python db_tester\batch_tester.py specific
pause
goto menu

:batch_all
echo.
echo WARNING: This will test ALL courses and lessons!
set /p confirm="Are you sure? (yes/no): "
if /i not "%confirm%"=="yes" goto menu
echo.
echo Running batch tests on ALL courses...
echo.
python db_tester\batch_tester.py all
pause
goto menu

:end
echo.
echo Goodbye!
echo.
