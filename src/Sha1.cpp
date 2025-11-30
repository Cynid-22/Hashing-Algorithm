#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>
#include <cstring>
#include "common.h"

using namespace std;

// SHA-1 Circular Rotate Left
inline uint32_t leftRotate(uint32_t x, uint32_t c) {
    return (x << c) | (x >> (32 - c));
}

// Process a single 64-byte block
#pragma GCC optimize("unroll-loops")
__attribute__((always_inline))
inline void transform(const uint8_t* block, uint32_t& h0, uint32_t& h1, uint32_t& h2, uint32_t& h3, uint32_t& h4) {
    uint32_t w[80];

    // Unrolled word loading (Big Endian)
    w[0] = (block[0] << 24) | (block[1] << 16) | (block[2] << 8) | block[3];
    w[1] = (block[4] << 24) | (block[5] << 16) | (block[6] << 8) | block[7];
    w[2] = (block[8] << 24) | (block[9] << 16) | (block[10] << 8) | block[11];
    w[3] = (block[12] << 24) | (block[13] << 16) | (block[14] << 8) | block[15];
    w[4] = (block[16] << 24) | (block[17] << 16) | (block[18] << 8) | block[19];
    w[5] = (block[20] << 24) | (block[21] << 16) | (block[22] << 8) | block[23];
    w[6] = (block[24] << 24) | (block[25] << 16) | (block[26] << 8) | block[27];
    w[7] = (block[28] << 24) | (block[29] << 16) | (block[30] << 8) | block[31];
    w[8] = (block[32] << 24) | (block[33] << 16) | (block[34] << 8) | block[35];
    w[9] = (block[36] << 24) | (block[37] << 16) | (block[38] << 8) | block[39];
    w[10] = (block[40] << 24) | (block[41] << 16) | (block[42] << 8) | block[43];
    w[11] = (block[44] << 24) | (block[45] << 16) | (block[46] << 8) | block[47];
    w[12] = (block[48] << 24) | (block[49] << 16) | (block[50] << 8) | block[51];
    w[13] = (block[52] << 24) | (block[53] << 16) | (block[54] << 8) | block[55];
    w[14] = (block[56] << 24) | (block[57] << 16) | (block[58] << 8) | block[59];
    w[15] = (block[60] << 24) | (block[61] << 16) | (block[62] << 8) | block[63];

    // Extend to 80 words
    for (int j = 16; j < 80; ++j) {
        w[j] = leftRotate(w[j - 3] ^ w[j - 8] ^ w[j - 14] ^ w[j - 16], 1);
    }

    uint32_t a = h0;
    uint32_t b = h1;
    uint32_t c = h2;
    uint32_t d = h3;
    uint32_t e = h4;

    // Unrolled loops
    // Round 1: 0-19
    for (int j = 0; j < 20; ++j) {
        uint32_t f = (b & c) | ((~b) & d);
        uint32_t k = 0x5A827999;
        uint32_t temp = leftRotate(a, 5) + f + e + k + w[j];
        e = d; d = c; c = leftRotate(b, 30); b = a; a = temp;
    }

    // Round 2: 20-39
    for (int j = 20; j < 40; ++j) {
        uint32_t f = b ^ c ^ d;
        uint32_t k = 0x6ED9EBA1;
        uint32_t temp = leftRotate(a, 5) + f + e + k + w[j];
        e = d; d = c; c = leftRotate(b, 30); b = a; a = temp;
    }

    // Round 3: 40-59
    for (int j = 40; j < 60; ++j) {
        uint32_t f = (b & c) | (b & d) | (c & d);
        uint32_t k = 0x8F1BBCDC;
        uint32_t temp = leftRotate(a, 5) + f + e + k + w[j];
        e = d; d = c; c = leftRotate(b, 30); b = a; a = temp;
    }

    // Round 4: 60-79
    for (int j = 60; j < 80; ++j) {
        uint32_t f = b ^ c ^ d;
        uint32_t k = 0xCA62C1D6;
        uint32_t temp = leftRotate(a, 5) + f + e + k + w[j];
        e = d; d = c; c = leftRotate(b, 30); b = a; a = temp;
    }

    h0 += a;
    h1 += b;
    h2 += c;
    h3 += d;
    h4 += e;
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
    uint32_t h0 = 0x67452301;
    uint32_t h1 = 0xEFCDAB89;
    uint32_t h2 = 0x98BADCFE;
    uint32_t h3 = 0x10325476;
    uint32_t h4 = 0xC3D2E1F0;
    
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
            transform(buffer.data() + offset, h0, h1, h2, h3, h4);
            offset += 64;
            totalBytes += 64;
        }
        
        // Report progress
        if (totalExpectedSize > 0) {
            reportProgress(totalBytes, totalExpectedSize);
        }
        
        // Handle remaining bytes (partial block at end of buffer)
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
                transform(finalBlock, h0, h1, h2, h3, h4);
            } else {
                // Need two blocks
                transform(finalBlock, h0, h1, h2, h3, h4);
                
                memset(finalBlock, 0, 64);
                for (int i = 7; i >= 0; --i) {
                    finalBlock[56 + (7-i)] = (totalBits >> (i * 8)) & 0xFF;
                }
                transform(finalBlock, h0, h1, h2, h3, h4);
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
         transform(finalBlock, h0, h1, h2, h3, h4);
    }

    // Output
    uint32_t result[5] = {h0, h1, h2, h3, h4};
    for (int i = 0; i < 5; ++i) {
        cout << hex << setfill('0') << setw(8) << result[i];
    }
    cout.flush();
    cout << endl;
    
    return 0;
}
