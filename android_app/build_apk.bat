@echo off
REM Android App Build Script
REM This script builds the APK automatically

echo.
echo ================================================================================
echo Building Item Assistant Android App
echo ================================================================================
echo.

REM Check if gradlew exists
if not exist "gradlew.bat" (
    echo Error: gradlew.bat not found
    echo Please run this script from the android_app directory
    pause
    exit /b 1
)

REM Build debug APK
echo Building debug APK...
call gradlew.bat build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo Build Successful!
    echo ================================================================================
    echo.
    echo APK Location: app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo Next steps:
    echo 1. Connect your phone via USB
    echo 2. Enable USB Debugging on phone
    echo 3. Run: adb install app\build\outputs\apk\debug\app-debug.apk
    echo.
    pause
) else (
    echo.
    echo ================================================================================
    echo Build Failed!
    echo ================================================================================
    echo.
    echo Please check the error messages above
    pause
    exit /b 1
)
