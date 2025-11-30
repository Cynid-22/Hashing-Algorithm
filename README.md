# Hashing Algorithm GUI

A modern, high-performance graphical user interface for calculating cryptographic hashes, built with Python and Tkinter.

## Features

- **Supported Algorithms**: MD5, SHA-1, SHA-256, SHA-384, SHA-512, and CRC-32.
- **Input Modes**: 
  - **Text Mode**: Instant hashing of typed text with optional auto-calculation.
  - **File Mode**: Secure hashing of files (or entire folders) of any size.
- **High Performance**: 
  - Uses optimized native libraries (`hashlib`, `zlib`) for maximum speed.
  - Hashes large files (e.g., 5GB+) in seconds.
- **Memory Efficient**: 
  - Uses chunked streaming (16MB chunks) to process files.
  - Minimal memory footprint (~16MB RAM regardless of file size).
- **User-Friendly**:
  - Real-time progress indicators for file hashing.
  - Drag-and-drop support for files.
  - Copy results to clipboard with one click.

## Performance Comparison

Tested on a **5 GB .dat file** with SHA-256, this application significantly outperforms common alternatives:

| Tool | Time Taken |
|------|------------|
| **This Application** | **8 seconds** |
| Windows PowerShell | 24 seconds |
| HashMyFiles | 78 seconds |

*Results may vary based on hardware, but this tool consistently delivers maximum throughput.*

## Requirements

- **Python 3.x** (with Tkinter)
- **G++ Compiler** (MinGW for Windows)
  - Download from: [MinGW-w64](https://www.mingw-w64.org/) or [WinLibs](https://winlibs.com/)
  - Ensure `g++` is in your system PATH

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Hashing-Algorithm
   ```

2. **Build the C++ executables:**
   
   Run the build script to compile all hash algorithm implementations:
   ```cmd
   build.bat
   ```
   
   This will create executables in the `bin/` directory:
   - `Sha256.exe`, `Sha384.exe`, `Sha512.exe`
   - `Sha1.exe`, `Md5.exe`
   - `Crc.exe`

3. **Verify the build:**
   
   Check that the `bin/` directory contains all `.exe` files.

## Usage

1. **Start the application:**
   ```cmd
   python app/gui.py
   ```

2. **Select algorithms:**
   - Go to **Hash Option** menu and select one or more algorithms.

3. **Calculate hashes:**
   
   **Text Mode:**
   - Type or paste text into the input field.
   - Check "Calculate Immediately" for auto-hashing as you type.
   - Or click "Calculate Hash" to hash manually.
   
   **File Mode:**
   - Click **+** to add individual files.
   - Click **+F** to add all files from a folder.
   - Click **Calculate Hash** to process all files.
   - View progress indicators during hashing.

4. **Copy results:**
   - Click the **Copy** button to copy all hash results to clipboard.

## Project Structure

```
Hashing-Algorithm/
├── src/                    # C++ source code
│   ├── Sha256.cpp, Sha384.cpp, Sha512.cpp
│   ├── Sha1.cpp, Md5.cpp, Crc.cpp
│   ├── common.h           # Shared utilities
│   └── sha.h              # SHA helper functions
├── app/                    # Python application
│   ├── gui.py             # Main GUI application
│   ├── hasher.py          # Hash calculation logic
│   ├── config.py          # Configuration management
│   ├── components.py      # UI components
│   └── algorithms.json    # Algorithm definitions
├── bin/                    # Compiled executables (created by build.bat)
├── build.bat              # Build script for C++ code
└── README.md
```

## Troubleshooting

**"Executable not found" error:**
- Make sure you've run `build.bat` successfully.
- Check that the `bin/` directory contains all `.exe` files.

**Build fails:**
- Ensure `g++` is installed and in your PATH.
- Try running `g++ --version` to verify installation.

**Python import errors:**
- Ensure you're running Python 3.x.
- Tkinter should be included by default; if not, reinstall Python with Tkinter enabled.

## License

Open source for educational and personal use.
