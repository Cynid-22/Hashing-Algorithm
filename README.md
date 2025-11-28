# Hashing Algorithm GUI

A modern, high-performance graphical user interface for calculating cryptographic hashes, built with Python and Tkinter.

## Features

- **Supported Algorithms**: SHA-256, SHA-384, SHA-512, and CRC-32.
- **Input Modes**: 
  - **Text**: Instant hashing of typed text.
  - **File**: Secure hashing of files of any size.
- **High Performance**: 
  - Uses optimized native libraries (`hashlib`, `zlib`) for maximum speed.
  - Hashes large files (e.g., 5GB+) in seconds.
- **Memory Efficient**: 
  - Uses chunked streaming (16MB chunks) to process files.
  - Minimal memory footprint (uses ~16MB RAM regardless of file size).

## Performance Comparison

Tested on a **5 GB .dat file** with SHA-256, this application significantly outperforms common alternatives:

| Tool | Time Taken |
|------|------------|
| **This Application** | **8 seconds** |
| Windows PowerShell | 24 seconds |
| HashMyFiles | 78 seconds |

*Results may vary based on hardware, but this tool consistently delivers maximum throughput.*


## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- G++ Compiler (MinGW) - *Only required if you want to rebuild the C++ components*

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Hashing-Algorithm
   ```

2. (Optional) Build the C++ executables:
   Double-click `build.bat` or run it from the command line:
   ```cmd
   build.bat
   ```
   *Note: The GUI uses Python's built-in libraries for speed by default, but includes C++ implementations as a fallback or for educational exploration.*

## Usage

1. Start the application:
   ```cmd
   python gui.py
   ```

2. **Calculate a Hash**:
   - Select your desired algorithm (SHA-256, etc.) from the dropdown.
   - **Text Mode**: Type or paste text into the input field.
   - **File Mode**: Click "+" or "+F" to add files or folders to the window.
   - Click **Calculate Hash**.

## Project Structure

- `gui.py`: Main Python application entry point.
- `common.h`: Shared C++ utilities for binary mode and progress reporting.
- `Sha256.cpp`, `Sha384.cpp`, `Sha512.cpp`, `Crc.cpp`: C++ implementations of the algorithms.
- `build.bat`: Script to compile the C++ code.

## License

Open source for educational and personal use.
