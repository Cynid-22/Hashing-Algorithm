#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>
#include <cstring>
#include "common.h"

using namespace std;

// SHA-512/384 Circular Rotate Right
inline uint64_t rightRotate(uint64_t x, uint64_t c) {
    return (x >> c) | (x << (64 - c));
}

// SHA-512 Constants
const uint64_t K[80] = {
    0x428a2f98d728ae22ULL, 0x7137449123ef65cdULL, 0xb5c0fbcfec4d3b2fULL, 0xe9b5dba58189dbbcULL,
    0x3956c25bf348b538ULL, 0x59f111f1b605d019ULL, 0x923f82a4af194f9bULL, 0xab1c5ed5da6d8118ULL,
    0xd807aa98a3030242ULL, 0x12835b0145706fbeULL, 0x243185be4ee4b28cULL, 0x550c7dc3d5ffb4e2ULL,
    0x72be5d74f27b896fULL, 0x80deb1fe3b1696b1ULL, 0x9bdc06a725c71235ULL, 0xc19bf174cf692694ULL,
    0xe49b69c19ef14ad2ULL, 0xefbe4786384f25e3ULL, 0x0fc19dc68b8cd5b5ULL, 0x240ca1cc77ac9c65ULL,
    0x2de92c6f592b0275ULL, 0x4a7484aa6ea6e483ULL, 0x5cb0a9dcbd41fbd4ULL, 0x76f988da831153b5ULL,
    0x983e5152ee66dfabULL, 0xa831c66d2db43210ULL, 0xb00327c898fb213fULL, 0xbf597fc7beef0ee4ULL,
    0xc6e00bf33da88fc2ULL, 0xd5a79147930aa725ULL, 0x06ca6351e003826fULL, 0x142929670a0e6e70ULL,
    0x27b70a8546d22ffcULL, 0x2e1b21385c26c926ULL, 0x4d2c6dfc5ac42aedULL, 0x53380d139d95b3dfULL,
    0x650a73548baf63deULL, 0x766a0abb3c77b2a8ULL, 0x81c2c92e47edaee6ULL, 0x92722c851482353bULL,
    0xa2bfe8a14cf10364ULL, 0xa81a664bbc423001ULL, 0xc24b8b70d0f89791ULL, 0xc76c51a30654be30ULL,
    0xd192e819d6ef5218ULL, 0xd69906245565a910ULL, 0xf40e35855771202aULL, 0x106aa07032bbd1b8ULL,
    0x19a4c116b8d2d0c8ULL, 0x1e376c085141ab53ULL, 0x2748774cdf8eeb99ULL, 0x34b0bcb5e19b48a8ULL,
    0x391c0cb3c5c95a63ULL, 0x4ed8aa4ae3418acbULL, 0x5b9cca4f7763e373ULL, 0x682e6ff3d6b2b8a3ULL,
    0x748f82ee5defb2fcULL, 0x78a5636f43172f60ULL, 0x84c87814a1f0ab72ULL, 0x8cc702081a6439ecULL,
    0x90befffa23631e28ULL, 0xa4506cebde82bde9ULL, 0xbef9a3f7b2c67915ULL, 0xc67178f2e372532bULL,
    0xca273eceea26619cULL, 0xd186b8c721c0c207ULL, 0xeada7dd6cde0eb1eULL, 0xf57d4f7fee6ed178ULL,
    0x06f067aa72176fbaULL, 0x0a637dc5a2c898a6ULL, 0x113f9804bef90daeULL, 0x1b710b35131c471bULL,
    0x28db77f523047d84ULL, 0x32caab7b40c72493ULL, 0x3c9ebe0a15c9bebcULL, 0x431d67c49c100d4cULL,
    0x4cc5d4becb3e42b6ULL, 0x597f299cfc657e2aULL, 0x5fcb6fab3ad6faecULL, 0x6c44198c4a475817ULL
};

// Process a single 128-byte block
void transform(const uint8_t* block, uint64_t H[8]) {
    uint64_t w[80];

    // Prepare message schedule
    for (int i = 0; i < 16; ++i) {
        w[i] = ((uint64_t)block[i * 8] << 56) |
               ((uint64_t)block[i * 8 + 1] << 48) |
               ((uint64_t)block[i * 8 + 2] << 40) |
               ((uint64_t)block[i * 8 + 3] << 32) |
               ((uint64_t)block[i * 8 + 4] << 24) |
               ((uint64_t)block[i * 8 + 5] << 16) |
               ((uint64_t)block[i * 8 + 6] << 8) |
               ((uint64_t)block[i * 8 + 7]);
    }

    for (int i = 16; i < 80; ++i) {
        uint64_t s0 = rightRotate(w[i - 15], 1) ^ rightRotate(w[i - 15], 8) ^ (w[i - 15] >> 7);
        uint64_t s1 = rightRotate(w[i - 2], 19) ^ rightRotate(w[i - 2], 61) ^ (w[i - 2] >> 6);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    uint64_t a = H[0];
    uint64_t b = H[1];
    uint64_t c = H[2];
    uint64_t d = H[3];
    uint64_t e = H[4];
    uint64_t f = H[5];
    uint64_t g = H[6];
    uint64_t h = H[7];

    for (int i = 0; i < 80; ++i) {
        uint64_t S1 = rightRotate(e, 14) ^ rightRotate(e, 18) ^ rightRotate(e, 41);
        uint64_t ch = (e & f) ^ (~e & g);
        uint64_t temp1 = h + S1 + ch + K[i] + w[i];
        uint64_t S0 = rightRotate(a, 28) ^ rightRotate(a, 34) ^ rightRotate(a, 39);
        uint64_t maj = (a & b) ^ (a & c) ^ (b & c);
        uint64_t temp2 = S0 + maj;

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
    
    // Initial Hash Values for SHA-384
    uint64_t H[8] = {
        0xcbbb9d5dc1059ed8ULL, 0x629a292a367cd507ULL, 0x9159015a3070dd17ULL, 0x152fecd8f70e5939ULL,
        0x67332667ffc00b31ULL, 0x8eb44a8768581511ULL, 0xdb0c2e0d64f98fa7ULL, 0x47b5481dbefa4fa4ULL
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
        while (offset + 128 <= bytesRead) {
            transform(buffer.data() + offset, H);
            offset += 128;
            totalBytes += 128;
        }
        
        // Report progress
        if (totalExpectedSize > 0) {
            reportProgress(totalBytes, totalExpectedSize);
        }
        
        // Handle remaining bytes
        if (offset < bytesRead) {
            size_t remaining = bytesRead - offset;
            
            uint8_t finalBlock[256]; // Max 2 blocks of 128 bytes
            memset(finalBlock, 0, 256);
            memcpy(finalBlock, buffer.data() + offset, remaining);
            
            totalBytes += remaining;
            
            finalBlock[remaining] = 0x80;
            
            // Length is 128 bits (16 bytes) for SHA-384/512
            // Stored as Big Endian at end of last block
            
            // 128 bytes per block.
            // Last 16 bytes reserved for length.
            // So if remaining < 112, fits in one block.
            
            // For SHA-384/512, length is actually 128 bits (16 bytes)
            // But usually only low 64 bits are used unless file is massive.
            // We'll support full 128 bits but only fill low 64 for now as uint64_t limit.
            // Actually, we should be careful. totalBytes is uint64_t.
            // totalBits = totalBytes * 8.
            
            // We need to write 128-bit length.
            // High 64 bits = 0 (unless file > 2^64 bits = 2 exabytes)
            // Low 64 bits = totalBits
            
            // 128 - 16 = 112 bytes data capacity
            
            if (remaining < 112) {
                // Fits in one block
                // Length at 112-127
                // Write high 64 bits (0) at 112-119
                // Write low 64 bits (totalBits) at 120-127
                
                uint64_t totalBits = totalBytes * 8;
                for (int i = 7; i >= 0; --i) {
                    finalBlock[120 + (7-i)] = (totalBits >> (i * 8)) & 0xFF;
                }
                transform(finalBlock, H);
            } else {
                // Need two blocks
                transform(finalBlock, H);
                
                memset(finalBlock, 0, 128);
                // Length at end of second block
                uint64_t totalBits = totalBytes * 8;
                for (int i = 7; i >= 0; --i) {
                    finalBlock[120 + (7-i)] = (totalBits >> (i * 8)) & 0xFF;
                }
                transform(finalBlock, H);
            }
            break;
        }
    }
    
    // If exact multiple of 128 bytes, still need padding
    if (totalBytes % 128 == 0) {
         uint8_t finalBlock[128];
         memset(finalBlock, 0, 128);
         finalBlock[0] = 0x80;
         
         uint64_t totalBits = totalBytes * 8;
         for (int i = 7; i >= 0; --i) {
             finalBlock[120 + (7-i)] = (totalBits >> (i * 8)) & 0xFF;
         }
         transform(finalBlock, H);
    }

    // Output - SHA-384 is first 6 words (48 bytes)
    for (int i = 0; i < 6; ++i) {
        cout << hex << setfill('0') << setw(16) << H[i];
    }
    cout.flush();
    cout << endl;
    
    return 0;
}
