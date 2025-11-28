@echo off
echo Compiling Hash Algorithms with optimizations...
echo.

g++ -O3 -march=native -o Sha256.exe Sha256.cpp
if %errorlevel% neq 0 (
    echo Error compiling Sha256.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o Sha384.exe Sha384.cpp  
if %errorlevel% neq 0 (
    echo Error compiling Sha384.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o Sha512.exe Sha512.cpp
if %errorlevel% neq 0 (
    echo Error compiling Sha512.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o Crc.exe Crc.cpp
if %errorlevel% neq 0 (
    echo Error compiling Crc.cpp
    exit /b %errorlevel%
)

echo.
echo All executables compiled successfully!
echo Optimization flags: -O3 -march=native
