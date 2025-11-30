#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <cmath>
#include <iomanip>
#include "common.h"
#include "sha.h" // Reusing helper functions if applicable, or defining new ones

using namespace std;

// MD5 Constants
const uint32_t S[64] = {
    7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
    5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
    4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
    6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21
};

const uint32_t K[64] = {
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
};

// Left rotate function
inline uint32_t leftRotate(uint32_t x, uint32_t c) {
    return (x << c) | (x >> (32 - c));
}

// MD5 functions
inline uint32_t F(uint32_t x, uint32_t y, uint32_t z) { return (x & y) | (~x & z); }
inline uint32_t G(uint32_t x, uint32_t y, uint32_t z) { return (x & z) | (y & ~z); }
inline uint32_t H(uint32_t x, uint32_t y, uint32_t z) { return x ^ y ^ z; }
inline uint32_t I(uint32_t x, uint32_t y, uint32_t z) { return y ^ (x | ~z); }

void md5(const string& message) {
    // Initialize variables
    uint32_t a0 = 0x67452301;
    uint32_t b0 = 0xefcdab89;
    uint32_t c0 = 0x98badcfe;
    uint32_t d0 = 0x10325476;

    // Pre-processing: Padding
    uint64_t originalLengthBits = message.length() * 8;
    vector<uint8_t> paddedMessage(message.begin(), message.end());

    paddedMessage.push_back(0x80); // Append '1' bit (0x80 byte)

    while ((paddedMessage.size() * 8) % 512 != 448) {
        paddedMessage.push_back(0x00);
    }

    // Append length (64 bits, little-endian)
    for (int i = 0; i < 8; ++i) {
        paddedMessage.push_back((originalLengthBits >> (i * 8)) & 0xFF);
    }

    // Process message in 512-bit chunks
    for (size_t i = 0; i < paddedMessage.size(); i += 64) {
        uint32_t M[16];
        for (int j = 0; j < 16; ++j) {
            M[j] = paddedMessage[i + j * 4] |
                   (paddedMessage[i + j * 4 + 1] << 8) |
                   (paddedMessage[i + j * 4 + 2] << 16) |
                   (paddedMessage[i + j * 4 + 3] << 24);
        }

        uint32_t A = a0;
        uint32_t B = b0;
        uint32_t C = c0;
        uint32_t D = d0;

        for (int j = 0; j < 64; ++j) {
            uint32_t f, g;
            if (j < 16) {
                f = F(B, C, D);
                g = j;
            } else if (j < 32) {
                f = G(B, C, D);
                g = (5 * j + 1) % 16;
            } else if (j < 48) {
                f = H(B, C, D);
                g = (3 * j + 5) % 16;
            } else {
                f = I(B, C, D);
                g = (7 * j) % 16;
            }

            uint32_t temp = D;
            D = C;
            C = B;
            B = B + leftRotate(A + f + K[j] + M[g], S[j]);
            A = temp;
        }

        a0 += A;
        b0 += B;
        c0 += C;
        d0 += D;
    }

    // Output hash (little-endian)
    uint32_t result[4] = {a0, b0, c0, d0};
    for (int i = 0; i < 4; ++i) {
        // We need to print bytes in little-endian order for each 32-bit word
        uint8_t* bytes = (uint8_t*)&result[i];
        for (int j = 0; j < 4; ++j) {
            cout << hex << setfill('0') << setw(2) << (int)bytes[j];
        }
    }
}

int main() {
    initBinaryMode();
    
    string input = readStdinToString();
    size_t totalSize = input.length();
    
    reportProgress(0, totalSize);
    md5(input);
    reportProgress(totalSize, totalSize);
    
    cout << endl;
    return 0;
}
