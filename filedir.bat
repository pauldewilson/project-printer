@echo off
setlocal enabledelayedexpansion

:: Check if directory parameter is provided
if "%~1"=="" (
    set "search_dir=%CD%"
) else (
    set "search_dir=%~1"
)

:: Create output file in the same directory as the script
set "output_file=%~dp0file_listing.txt"

:: Clear output file if it exists
if exist "%output_file%" del "%output_file%"

:: Echo start message
echo Generating file listing for: %search_dir%
echo Results will be saved to: %output_file%

:: Use dir /s /b to get full file paths, redirect to output file
dir /s /b "%search_dir%" > "%output_file%"

:: Count total files
for /f %%A in ('type "%output_file%" ^| find /c /v ""') do set "total_files=%%A"

:: Echo completion message
echo.
echo Complete! Found %total_files% files and directories.
echo Results saved to: %output_file%
pause