#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <iomanip>
#include <cstdint>
#include "common.h"

using namespace std;

// Constants for MD5 transform
const uint32_t S[64] = {
    7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
    5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
    4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
    6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21
};

const uint32_t K[64] = {
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
};

// Bitwise rotation
inline uint32_t leftRotate(uint32_t x, uint32_t c) {
    return (x << c) | (x >> (32 - c));
}

// MD5 basic functions
inline uint32_t F(uint32_t x, uint32_t y, uint32_t z) { return (x & y) | (~x & z); }
inline uint32_t G(uint32_t x, uint32_t y, uint32_t z) { return (x & z) | (y & ~z); }
inline uint32_t H(uint32_t x, uint32_t y, uint32_t z) { return x ^ y ^ z; }
inline uint32_t I(uint32_t x, uint32_t y, uint32_t z) { return y ^ (x | ~z); }

// Process a single 64-byte block
#pragma GCC optimize("unroll-loops")
__attribute__((always_inline))
inline void transform(const uint8_t* block, uint32_t& a0, uint32_t& b0, uint32_t& c0, uint32_t& d0) {
    // Direct zero-copy access (Little Endian)
    const uint32_t* M = reinterpret_cast<const uint32_t*>(block);

    uint32_t A = a0;
    uint32_t B = b0;
    uint32_t C = c0;
    uint32_t D = d0;

    // Unrolled rounds
    #define STEP1(f, a, b, c, d, k, s) \
        a += F(b, c, d) + M[k] + K[k]; a = b + leftRotate(a, s)
        
    STEP1(F, A, B, C, D, 0, 7); STEP1(F, D, A, B, C, 1, 12); STEP1(F, C, D, A, B, 2, 17); STEP1(F, B, C, D, A, 3, 22);
    STEP1(F, A, B, C, D, 4, 7); STEP1(F, D, A, B, C, 5, 12); STEP1(F, C, D, A, B, 6, 17); STEP1(F, B, C, D, A, 7, 22);
    STEP1(F, A, B, C, D, 8, 7); STEP1(F, D, A, B, C, 9, 12); STEP1(F, C, D, A, B, 10, 17); STEP1(F, B, C, D, A, 11, 22);
    STEP1(F, A, B, C, D, 12, 7); STEP1(F, D, A, B, C, 13, 12); STEP1(F, C, D, A, B, 14, 17); STEP1(F, B, C, D, A, 15, 22);

    #define STEP2(f, a, b, c, d, k, s, i) \
        a += G(b, c, d) + M[k] + K[i]; a = b + leftRotate(a, s)
        
    STEP2(G, A, B, C, D, 1, 5, 16); STEP2(G, D, A, B, C, 6, 9, 17); STEP2(G, C, D, A, B, 11, 14, 18); STEP2(G, B, C, D, A, 0, 20, 19);
    STEP2(G, A, B, C, D, 5, 5, 20); STEP2(G, D, A, B, C, 10, 9, 21); STEP2(G, C, D, A, B, 15, 14, 22); STEP2(G, B, C, D, A, 4, 20, 23);
    STEP2(G, A, B, C, D, 9, 5, 24); STEP2(G, D, A, B, C, 14, 9, 25); STEP2(G, C, D, A, B, 3, 14, 26); STEP2(G, B, C, D, A, 8, 20, 27);
    STEP2(G, A, B, C, D, 13, 5, 28); STEP2(G, D, A, B, C, 2, 9, 29); STEP2(G, C, D, A, B, 7, 14, 30); STEP2(G, B, C, D, A, 12, 20, 31);

    #define STEP3(f, a, b, c, d, k, s, i) \
        a += H(b, c, d) + M[k] + K[i]; a = b + leftRotate(a, s)
        
    STEP3(H, A, B, C, D, 5, 4, 32); STEP3(H, D, A, B, C, 8, 11, 33); STEP3(H, C, D, A, B, 11, 16, 34); STEP3(H, B, C, D, A, 14, 23, 35);
    STEP3(H, A, B, C, D, 1, 4, 36); STEP3(H, D, A, B, C, 4, 11, 37); STEP3(H, C, D, A, B, 7, 16, 38); STEP3(H, B, C, D, A, 10, 23, 39);
    STEP3(H, A, B, C, D, 13, 4, 40); STEP3(H, D, A, B, C, 0, 11, 41); STEP3(H, C, D, A, B, 3, 16, 42); STEP3(H, B, C, D, A, 6, 23, 43);
    STEP3(H, A, B, C, D, 9, 4, 44); STEP3(H, D, A, B, C, 12, 11, 45); STEP3(H, C, D, A, B, 15, 16, 46); STEP3(H, B, C, D, A, 2, 23, 47);

    #define STEP4(f, a, b, c, d, k, s, i) \
        a += I(b, c, d) + M[k] + K[i]; a = b + leftRotate(a, s)
        
    STEP4(I, A, B, C, D, 0, 6, 48); STEP4(I, D, A, B, C, 7, 10, 49); STEP4(I, C, D, A, B, 14, 15, 50); STEP4(I, B, C, D, A, 5, 21, 51);
    STEP4(I, A, B, C, D, 12, 6, 52); STEP4(I, D, A, B, C, 3, 10, 53); STEP4(I, C, D, A, B, 10, 15, 54); STEP4(I, B, C, D, A, 1, 21, 55);
    STEP4(I, A, B, C, D, 8, 6, 56); STEP4(I, D, A, B, C, 15, 10, 57); STEP4(I, C, D, A, B, 6, 15, 58); STEP4(I, B, C, D, A, 13, 21, 59);
    STEP4(I, A, B, C, D, 4, 6, 60); STEP4(I, D, A, B, C, 11, 10, 61); STEP4(I, C, D, A, B, 2, 15, 62); STEP4(I, B, C, D, A, 9, 21, 63);

    a0 += A;
    b0 += B;
    c0 += C;
    d0 += D;
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
    
    // State variables
    uint32_t a0 = 0x67452301;
    uint32_t b0 = 0xefcdab89;
    uint32_t c0 = 0x98badcfe;
    uint32_t d0 = 0x10325476;
    
    uint64_t totalBytes = 0;
    
    // 4MB buffer (reduced loop overhead)
    const size_t BUFFER_SIZE = 4 * 1024 * 1024;
    vector<uint8_t> buffer(BUFFER_SIZE);
    
    // Report initial progress
    if (totalExpectedSize > 0) reportProgress(0, totalExpectedSize);
    
    while (cin) {
        cin.read((char*)buffer.data(), BUFFER_SIZE);
        size_t bytesRead = cin.gcount();
        if (bytesRead == 0) break;
        
        size_t offset = 0;
        while (offset + 64 <= bytesRead) {
            transform(buffer.data() + offset, a0, b0, c0, d0);
            offset += 64;
            totalBytes += 64;
        }
        
        // Report progress
        if (totalExpectedSize > 0) {
            reportProgress(totalBytes, totalExpectedSize);
        }
        
        // Handle remaining bytes (partial block at end of buffer)
        // If we have remaining bytes, they must be the end of the file
        // because we read in multiples of 64 unless EOF.
        // Wait, 1MB is multiple of 64, so this only happens at EOF.
        if (offset < bytesRead) {
            // This is the last partial block
            // We need to handle padding here
            size_t remaining = bytesRead - offset;
            
            // Copy remaining to a temp buffer for padding
            uint8_t finalBlock[128];
            memset(finalBlock, 0, 128);
            memcpy(finalBlock, buffer.data() + offset, remaining);
            
            totalBytes += remaining;
            
            // Add '1' bit
            finalBlock[remaining] = 0x80;
            
            uint64_t totalBits = totalBytes * 8;
            
            if (remaining < 56) {
                // Fits in one block
                for (int i = 0; i < 8; ++i) {
                    finalBlock[56 + i] = (totalBits >> (i * 8)) & 0xFF;
                }
                transform(finalBlock, a0, b0, c0, d0);
            } else {
                // Need two blocks
                transform(finalBlock, a0, b0, c0, d0);
                
                memset(finalBlock, 0, 64);
                for (int i = 0; i < 8; ++i) {
                    finalBlock[56 + i] = (totalBits >> (i * 8)) & 0xFF;
                }
                transform(finalBlock, a0, b0, c0, d0);
            }
            break; // Done
        }
    }
    
    // If exact multiple of 64 bytes, we still need padding
    if (totalBytes % 64 == 0) {
         uint8_t finalBlock[64];
         memset(finalBlock, 0, 64);
         finalBlock[0] = 0x80;
         
         uint64_t totalBits = totalBytes * 8;
         
         // If 0x80 leaves enough room for length (56 bytes)
         // 0 < 56, so yes.
         // Wait, if totalBytes % 64 == 0, we are at start of new block.
         // So we have 0 bytes of data in this block.
         // 0 bytes data + 1 byte (0x80) = 1 byte used.
         // 1 < 56, so we fit in one block.
         
         for (int i = 0; i < 8; ++i) {
             finalBlock[56 + i] = (totalBits >> (i * 8)) & 0xFF;
         }
         transform(finalBlock, a0, b0, c0, d0);
    }

    // Output
    uint32_t result[4] = {a0, b0, c0, d0};
    for (int i = 0; i < 4; ++i) {
        uint8_t* bytes = (uint8_t*)&result[i];
        for (int j = 0; j < 4; ++j) {
            cout << hex << setfill('0') << setw(2) << (int)bytes[j];
        }
    }
    cout.flush();
    cout << endl;
    
    return 0;
}
