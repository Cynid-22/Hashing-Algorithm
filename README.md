# Secure Hash Algorithm GUI

A simple, user-friendly graphical interface for calculating **SHA-256**, **SHA-384**, and **SHA-512** cryptographic hashes.

## Features

✅ **No Compilation Required** - Pure Python implementation using built-in `hashlib`  
✅ **Multiple Algorithms** - SHA-256, SHA-384, and SHA-512  
✅ **Text & Binary File Support** - Hash any type of file  
✅ **Cross-Platform** - Works on Windows, macOS, and Linux  
✅ **Modern GUI** - Clean interface built with tkinter  
✅ **Clipboard Integration** - Copy hash results with one click

## Requirements

- Python 3.6 or higher
- tkinter (usually comes pre-installed with Python)

## Installation

No installation needed! Just download `gui.py` and run it.

## Usage

### Running the GUI

```bash
python gui.py
```

### How to Use

1. **Select Algorithm** - Choose SHA-256, SHA-384, or SHA-512 from the dropdown
2. **Input Data** - Either:
   - Type or paste text directly into the input box, OR
   - Click "Browse File..." to load a file (text or binary)
3. **Calculate** - Click "Calculate Hash" to generate the hash
4. **Copy** - Click "Copy" to copy the hash to your clipboard
5. **Clear** - Click "Clear" to reset both input and output

### Example Hashes

For the string `"Hello, World!"`:

- **SHA-256**: `dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f`
- **SHA-384**: `5485cc9b3365b4305dfb4e8337e0a598a574f8242bf17289e0dd6c20a3cd44a089de16ab4ab308f63e44b1170eb5f515`
- **SHA-512**: `374d794a95cdcfd8b35993185fef9ba368f160d8daf432d08ba9f1ed1e5abe6cc69291e0fa2fe0006a52570ef18c19def4e617c33ce52ef0a6e5fbe318cb0387`

## Technical Details

### Python Implementation

This GUI uses Python's built-in `hashlib` library, which provides:
- **FIPS-compliant** implementations
- **Optimized C implementations** for performance
- **No external dependencies** required
- **Cross-platform compatibility**

### Previous C++ Implementation

The original implementation used separate C++ executables (`Sha256.exe`, `Sha384.exe`, `Sha512.exe`) that needed to be compiled. The Python version eliminates this complexity while maintaining the same functionality.

## File Structure

```
Secure-Hash-Algorithm/
├── gui.py           # Main GUI application (Python)
├── test_hash.py     # Test script for verification
├── README.md        # This file
├── Sha256.cpp       # Original C++ implementation (kept for reference)
├── Sha384.cpp       # Original C++ implementation (kept for reference)
├── Sha512.cpp       # Original C++ implementation (kept for reference)
└── sha.h            # C++ header file (kept for reference)
```

## Testing

Run the test script to verify hash calculations:

```bash
python test_hash.py
```

## Code Quality

The Python implementation follows modern best practices:
- ✅ Type hints for better IDE support
- ✅ Comprehensive docstrings
- ✅ Clean separation of concerns
- ✅ Proper error handling
- ✅ PEP 8 compliant

## Security Note

The hash functions provided are cryptographic-quality and suitable for:
- File integrity verification
- Checksum generation
- Digital signatures

## License

This project is open source and available for educational purposes.

## Contributing

Feel free to submit issues or pull requests to improve this tool!

---

**Author**: Converted from C# to Python with modern refactoring  
**Last Updated**: November 2025
