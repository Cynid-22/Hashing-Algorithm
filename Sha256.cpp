#include <iostream>
#include <bitset>
#include <vector>
#include <sstream>
#include <bits/stdc++.h>
#include "sha.h"

using namespace std;

void preProcessing(size_t length, vector<bool>& binMessage)
{
    int K = 0;
    binMessage.push_back(true);

    while ((length + 1 + K + 64) % 512 != 0) {
        K++;
        binMessage.push_back(false);
    }

    for (int i = 63; i >= 0; --i) {
        binMessage.push_back((length >> i) & 1);
    }
}


vector<bool> processing (vector<bool>& binMessage, uint32_t H[8], uint32_t K[64])
{
    uint32_t sqrtTemp[8];
    for (int i = 0; i < 8; ++i)
        sqrtTemp[i] = H[i];

    size_t length = binMessage.size(), numberOfChunks = length/512;

    if (length % 512 != 0)
        cerr << "Error: Padded message length is not a multiple of 512 bits.\n";

    for (size_t chunkIter = 0; chunkIter < numberOfChunks; ++ chunkIter) {
        uint32_t w[64] = {};

        size_t pointer = chunkIter * 512, index;
        for (int i = 0; i < 16; ++i) {
            index = pointer + i * 32;
            w[i] = bitsToUsignedInt<uint32_t>(binMessage, index);
        }

        for (int i = 16; i < 64; ++i) {
            uint32_t s0 = rotateRightByN<uint32_t>(w[i - 15], 7, 32) ^ rotateRightByN<uint32_t>(w[i - 15], 18, 32) ^ (w[i - 15] >> 3);
            uint32_t s1 = rotateRightByN<uint32_t>(w[i - 2], 17, 32) ^ rotateRightByN<uint32_t>(w[i - 2], 19, 32) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16] + s0 + w[i - 7] + s1;
        }

        uint32_t a = sqrtTemp[0];
        uint32_t b = sqrtTemp[1];
        uint32_t c = sqrtTemp[2];
        uint32_t d = sqrtTemp[3];
        uint32_t e = sqrtTemp[4];
        uint32_t f = sqrtTemp[5];
        uint32_t g = sqrtTemp[6];
        uint32_t h = sqrtTemp[7];
        

        for (int i = 0; i < 64; ++i) {
            uint32_t S1 = rotateRightByN<uint32_t>(e, 6, 32) ^ rotateRightByN<uint32_t>(e, 11, 32) ^ rotateRightByN<uint32_t>(e, 25, 32);
            uint32_t ch = (e & f) ^ (~e & g);
            uint32_t temp1 = h + S1 + ch + K[i] + w[i];
            uint32_t S0 = rotateRightByN<uint32_t>(a, 2, 32) ^ rotateRightByN<uint32_t>(a, 13, 32) ^ rotateRightByN<uint32_t>(a, 22, 32);
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
        
        sqrtTemp[0] += a;
        sqrtTemp[1] += b;
        sqrtTemp[2] += c;
        sqrtTemp[3] += d;
        sqrtTemp[4] += e;
        sqrtTemp[5] += f;
        sqrtTemp[6] += g;
        sqrtTemp[7] += h;
    }
    vector<bool> digest;
    for (int i = 0; i < 8; ++i)
        for (int j = 31; j >= 0; --j)
            digest.push_back((sqrtTemp[i] >> j) & 1);
    return digest;
}


void sha256(string strMessage)
{
    uint32_t H[8] =  {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
    uint32_t K[64] = {0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
                    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
                    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
                    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
                    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
                    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
                    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
                    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};
    
    vector<bool> binMessage, hash;
    size_t messageBitLength = 0;
    bitset<256> digest;

    

    binMessage = TextToBinaryString(strMessage, messageBitLength);
    preProcessing(messageBitLength, binMessage);
    hash = processing(binMessage, H, K);

    for (int i = 0; i < 256; ++i) {
#include <iostream>
#include <bitset>
#include <vector>
#include <sstream>
#include <bits/stdc++.h>
#include "sha.h"

using namespace std;

void preProcessing(size_t length, vector<bool>& binMessage)
{
    int K = 0;
    binMessage.push_back(true);

    while ((length + 1 + K + 64) % 512 != 0) {
        K++;
        binMessage.push_back(false);
    }

    for (int i = 63; i >= 0; --i) {
        binMessage.push_back((length >> i) & 1);
    }
}


vector<bool> processing (vector<bool>& binMessage, uint32_t H[8], uint32_t K[64])
{
    uint32_t sqrtTemp[8];
    for (int i = 0; i < 8; ++i)
        sqrtTemp[i] = H[i];

    size_t length = binMessage.size(), numberOfChunks = length/512;

    if (length % 512 != 0)
        cerr << "Error: Padded message length is not a multiple of 512 bits.\n";

    for (size_t chunkIter = 0; chunkIter < numberOfChunks; ++ chunkIter) {
        uint32_t w[64] = {};

        size_t pointer = chunkIter * 512, index;
        for (int i = 0; i < 16; ++i) {
            index = pointer + i * 32;
            w[i] = bitsToUsignedInt<uint32_t>(binMessage, index);
        }

        for (int i = 16; i < 64; ++i) {
            uint32_t s0 = rotateRightByN<uint32_t>(w[i - 15], 7, 32) ^ rotateRightByN<uint32_t>(w[i - 15], 18, 32) ^ (w[i - 15] >> 3);
            uint32_t s1 = rotateRightByN<uint32_t>(w[i - 2], 17, 32) ^ rotateRightByN<uint32_t>(w[i - 2], 19, 32) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16] + s0 + w[i - 7] + s1;
        }

        uint32_t a = sqrtTemp[0];
        uint32_t b = sqrtTemp[1];
        uint32_t c = sqrtTemp[2];
        uint32_t d = sqrtTemp[3];
        uint32_t e = sqrtTemp[4];
        uint32_t f = sqrtTemp[5];
        uint32_t g = sqrtTemp[6];
        uint32_t h = sqrtTemp[7];
        

        for (int i = 0; i < 64; ++i) {
            uint32_t S1 = rotateRightByN<uint32_t>(e, 6, 32) ^ rotateRightByN<uint32_t>(e, 11, 32) ^ rotateRightByN<uint32_t>(e, 25, 32);
            uint32_t ch = (e & f) ^ (~e & g);
            uint32_t temp1 = h + S1 + ch + K[i] + w[i];
            uint32_t S0 = rotateRightByN<uint32_t>(a, 2, 32) ^ rotateRightByN<uint32_t>(a, 13, 32) ^ rotateRightByN<uint32_t>(a, 22, 32);
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
        
        sqrtTemp[0] += a;
        sqrtTemp[1] += b;
        sqrtTemp[2] += c;
        sqrtTemp[3] += d;
        sqrtTemp[4] += e;
        sqrtTemp[5] += f;
        sqrtTemp[6] += g;
        sqrtTemp[7] += h;
    }
    vector<bool> digest;
    for (int i = 0; i < 8; ++i)
        for (int j = 31; j >= 0; --j)
            digest.push_back((sqrtTemp[i] >> j) & 1);
    return digest;
}


void sha256(string strMessage)
{
    uint32_t H[8] =  {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
    uint32_t K[64] = {0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
                    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
                    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
                    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
                    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
                    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
                    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
                    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};
    
    vector<bool> binMessage, hash;
    size_t messageBitLength = 0;
    bitset<256> digest;

    

    binMessage = TextToBinaryString(strMessage, messageBitLength);
    preProcessing(messageBitLength, binMessage);
    hash = processing(binMessage, H, K);

    for (int i = 0; i < 256; ++i) {
        digest[i] = hash[i];
    }

    cout << bitsetToHex<bitset<256>>(digest, 256);
}

int main()
{
    // Read entire input from stdin
    string input((istreambuf_iterator<char>(cin)), istreambuf_iterator<char>());
    sha256(input);
    cout << endl;
    return 0;
}