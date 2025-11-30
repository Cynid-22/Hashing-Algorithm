@echo off
echo Compiling Hash Algorithms with optimizations...
echo.

if not exist bin mkdir bin

g++ -O3 -march=native -o bin/Sha256.exe src/Sha256.cpp
if %errorlevel% neq 0 (
    echo Error compiling Sha256.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o bin/Sha384.exe src/Sha384.cpp  
if %errorlevel% neq 0 (
    echo Error compiling Sha384.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o bin/Sha512.exe src/Sha512.cpp
if %errorlevel% neq 0 (
    echo Error compiling Sha512.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o bin/Crc.exe src/Crc.cpp
if %errorlevel% neq 0 (
    echo Error compiling Crc.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o bin/Md5.exe src/Md5.cpp
if %errorlevel% neq 0 (
    echo Error compiling Md5.cpp
    exit /b %errorlevel%
)

g++ -O3 -march=native -o bin/Sha1.exe src/Sha1.cpp
if %errorlevel% neq 0 (
    echo Error compiling Sha1.cpp
    exit /b %errorlevel%
)

echo.
echo All executables compiled successfully!
echo Optimization flags: -O3 -march=native
