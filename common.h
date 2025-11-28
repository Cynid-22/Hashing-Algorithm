#ifndef COMMON_H
#define COMMON_H

#include <iostream>
#include <string>
#include <cstdio>

// Platform-specific includes for binary mode
#ifdef _WIN32
    #include <io.h>
    #include <fcntl.h>
#endif

// Initialize stdin to binary mode to prevent corruption of binary data
inline void initBinaryMode() {
    #ifdef _WIN32
        _setmode(_fileno(stdin), _O_BINARY);
    #endif
}

// Read all input from stdin
inline std::string readStdinToString() {
    return std::string((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());
}

// Report progress to stderr for GUI monitoring
// Format: "PROGRESS:XX" where XX is percentage (0-100)
inline void reportProgress(size_t bytesProcessed, size_t totalBytes) {
    if (totalBytes == 0) return;
    int percentage = static_cast<int>((bytesProcessed * 100) / totalBytes);
    // Only report on 5% increments to avoid flooding
    static int lastReported = -5;
    if (percentage >= lastReported + 5 || percentage == 100) {
        std::fprintf(stderr, "PROGRESS:%d\n", percentage);
        std::fflush(stderr);
        lastReported = percentage;
    }
}

#endif
