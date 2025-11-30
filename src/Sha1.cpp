#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>
#include "common.h"

using namespace std;

// SHA-1 Circular Rotate Left
inline uint32_t leftRotate(uint32_t x, uint32_t c) {
    return (x << c) | (x >> (32 - c));
}

void sha1(const string& message) {
    // Initialize variables
    uint32_t h0 = 0x67452301;
    uint32_t h1 = 0xEFCDAB89;
    uint32_t h2 = 0x98BADCFE;
    uint32_t h3 = 0x10325476;
    uint32_t h4 = 0xC3D2E1F0;

    // Pre-processing: Padding
    uint64_t originalLengthBits = message.length() * 8;
    vector<uint8_t> paddedMessage(message.begin(), message.end());

    paddedMessage.push_back(0x80); // Append '1' bit

    while ((paddedMessage.size() * 8) % 512 != 448) {
        paddedMessage.push_back(0x00);
    }

    // Append length (64 bits, big-endian)
    for (int i = 7; i >= 0; --i) {
        paddedMessage.push_back((originalLengthBits >> (i * 8)) & 0xFF);
    }

    // Process message in 512-bit chunks
    for (size_t i = 0; i < paddedMessage.size(); i += 64) {
        uint32_t w[80];

        // Break chunk into sixteen 32-bit big-endian words w[0..15]
        for (int j = 0; j < 16; ++j) {
            w[j] = (paddedMessage[i + j * 4] << 24) |
                   (paddedMessage[i + j * 4 + 1] << 16) |
                   (paddedMessage[i + j * 4 + 2] << 8) |
                   (paddedMessage[i + j * 4 + 3]);
        }

        // Extend the sixteen 32-bit words into eighty 32-bit words
        for (int j = 16; j < 80; ++j) {
            w[j] = leftRotate(w[j - 3] ^ w[j - 8] ^ w[j - 14] ^ w[j - 16], 1);
        }

        uint32_t a = h0;
        uint32_t b = h1;
        uint32_t c = h2;
        uint32_t d = h3;
        uint32_t e = h4;

        for (int j = 0; j < 80; ++j) {
            uint32_t f, k;

            if (j < 20) {
                f = (b & c) | ((~b) & d);
                k = 0x5A827999;
            } else if (j < 40) {
                f = b ^ c ^ d;
                k = 0x6ED9EBA1;
            } else if (j < 60) {
                f = (b & c) | (b & d) | (c & d);
                k = 0x8F1BBCDC;
            } else {
                f = b ^ c ^ d;
                k = 0xCA62C1D6;
            }

            uint32_t temp = leftRotate(a, 5) + f + e + k + w[j];
            e = d;
            d = c;
            c = leftRotate(b, 30);
            b = a;
            a = temp;
        }

        h0 += a;
        h1 += b;
        h2 += c;
        h3 += d;
        h4 += e;
    }

    // Output hash (big-endian)
    uint32_t result[5] = {h0, h1, h2, h3, h4};
    for (int i = 0; i < 5; ++i) {
        cout << hex << setfill('0') << setw(8) << result[i];
    }
}

int main() {
    initBinaryMode();
    
    string input = readStdinToString();
    size_t totalSize = input.length();
    
    reportProgress(0, totalSize);
    sha1(input);
    reportProgress(totalSize, totalSize);
    
    cout << endl;
    return 0;
}
