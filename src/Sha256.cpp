#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>
#include <cstring>
#include "common.h"

using namespace std;

// SHA-256 Circular Rotate Right
inline uint32_t rightRotate(uint32_t x, uint32_t c) {
    return (x >> c) | (x << (32 - c));
}

// SHA-256 Constants
const uint32_t K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

// Process a single 64-byte block
__attribute__((always_inline))
inline void transform(const uint8_t* block, uint32_t H[8]) {
    uint32_t w[64];

    // Prepare message schedule
    for (int i = 0; i < 16; ++i) {
        w[i] = (block[i * 4] << 24) |
               (block[i * 4 + 1] << 16) |
               (block[i * 4 + 2] << 8) |
               (block[i * 4 + 3]);
    }

    for (int i = 16; i < 64; ++i) {
        uint32_t s0 = rightRotate(w[i - 15], 7) ^ rightRotate(w[i - 15], 18) ^ (w[i - 15] >> 3);
        uint32_t s1 = rightRotate(w[i - 2], 17) ^ rightRotate(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    uint32_t a = H[0];
    uint32_t b = H[1];
    uint32_t c = H[2];
    uint32_t d = H[3];
    uint32_t e = H[4];
    uint32_t f = H[5];
    uint32_t g = H[6];
    uint32_t h = H[7];

    for (int i = 0; i < 64; ++i) {
        uint32_t S1 = rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25);
        uint32_t ch = (e & f) ^ (~e & g);
        uint32_t temp1 = h + S1 + ch + K[i] + w[i];
        uint32_t S0 = rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        uint32_t temp2 = S0 + maj;

        h = g;
        g = f;
        f = e;
        e = d + temp1;
        d = c;
        c = b;
        b = a;
        a = temp1 + temp2;
    }

    H[0] += a;
    H[1] += b;
    H[2] += c;
    H[3] += d;
    H[4] += e;
    H[5] += f;
    H[6] += g;
    H[7] += h;
}

int main(int argc, char* argv[]) {
    initBinaryMode();
    
    // Check for file size argument
    size_t totalExpectedSize = 0;
    if (argc > 1) {
        try {
            totalExpectedSize = std::stoull(argv[1]);
        } catch (...) {
            totalExpectedSize = 0;
        }
    }
    
    // Initial Hash Values
    uint32_t H[8] = {
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    };
    
    uint64_t totalBytes = 0;
    
    // 1MB buffer
    const size_t BUFFER_SIZE = 1024 * 1024;
    vector<uint8_t> buffer(BUFFER_SIZE);
    
    // Report initial progress
    if (totalExpectedSize > 0) reportProgress(0, totalExpectedSize);
    
    while (cin) {
        cin.read((char*)buffer.data(), BUFFER_SIZE);
        size_t bytesRead = cin.gcount();
        if (bytesRead == 0) break;
        
        size_t offset = 0;
        while (offset + 64 <= bytesRead) {
            transform(buffer.data() + offset, H);
            offset += 64;
            totalBytes += 64;
        }
        
        // Report progress
        if (totalExpectedSize > 0) {
            reportProgress(totalBytes, totalExpectedSize);
        }
        
        // Handle remaining bytes
        if (offset < bytesRead) {
            size_t remaining = bytesRead - offset;
            
            uint8_t finalBlock[128];
            memset(finalBlock, 0, 128);
            memcpy(finalBlock, buffer.data() + offset, remaining);
            
            totalBytes += remaining;
            
            finalBlock[remaining] = 0x80;
            
            uint64_t totalBits = totalBytes * 8;
            
            if (remaining < 56) {
                // Fits in one block
                for (int i = 7; i >= 0; --i) {
                    finalBlock[56 + (7-i)] = (totalBits >> (i * 8)) & 0xFF;
                }
                transform(finalBlock, H);
            } else {
                // Need two blocks
                transform(finalBlock, H);
                
                memset(finalBlock, 0, 64);
                for (int i = 7; i >= 0; --i) {
                    finalBlock[56 + (7-i)] = (totalBits >> (i * 8)) & 0xFF;
                }
                transform(finalBlock, H);
            }
            break;
        }
    }
    
    // If exact multiple of 64 bytes, still need padding
    if (totalBytes % 64 == 0) {
         uint8_t finalBlock[64];
         memset(finalBlock, 0, 64);
         finalBlock[0] = 0x80;
         
         uint64_t totalBits = totalBytes * 8;
         
         for (int i = 7; i >= 0; --i) {
             finalBlock[56 + (7-i)] = (totalBits >> (i * 8)) & 0xFF;
         }
         transform(finalBlock, H);
    }

    // Output
    for (int i = 0; i < 8; ++i) {
        cout << hex << setfill('0') << setw(8) << H[i];
    }
    cout.flush();
    cout << endl;
    
    return 0;
}