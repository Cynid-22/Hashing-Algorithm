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

    // Padding for SHA-384 (same as SHA-512): L + 1 + K + 128 = 0 mod 1024
    while ((length + 1 + K + 128) % 1024 != 0) {
        K++;
        binMessage.push_back(false);
    }

    // Append length as 128-bit big-endian integer
    for (int i = 127; i >= 0; --i) {
        if (i < 64)
            binMessage.push_back((length >> i) & 1);
        else
            binMessage.push_back(0);
    }
}

vector<bool> processing (vector<bool>& binMessage, uint64_t H[8], uint64_t K[80])
{
    uint64_t sqrtTemp[8];
    for (int i = 0; i < 8; ++i)
        sqrtTemp[i] = H[i];

    size_t length = binMessage.size(), numberOfChunks = length/1024;

    if (length % 1024 != 0)
        cerr << "Error: Padded message length is not a multiple of 1024 bits.\n";

    for (size_t chunkIter = 0; chunkIter < numberOfChunks; ++ chunkIter) {
        uint64_t w[80] = {};

        size_t pointer = chunkIter * 1024, index;
        for (int i = 0; i < 16; ++i) {
            index = pointer + i * 64;
            w[i] = bitsToUsignedInt<uint64_t>(binMessage, index);
        }

        for (int i = 16; i < 80; ++i) {
            uint64_t s0 = rotateRightByN<uint64_t>(w[i - 15], 1, 64) ^ rotateRightByN<uint64_t>(w[i - 15], 8, 64) ^ (w[i - 15] >> 7);
            uint64_t s1 = rotateRightByN<uint64_t>(w[i - 2], 19, 64) ^ rotateRightByN<uint64_t>(w[i - 2], 61, 64) ^ (w[i - 2] >> 6);
            w[i] = w[i - 16] + s0 + w[i - 7] + s1;
        }

        uint64_t a = sqrtTemp[0];
        uint64_t b = sqrtTemp[1];
        uint64_t c = sqrtTemp[2];
        uint64_t d = sqrtTemp[3];
        uint64_t e = sqrtTemp[4];
        uint64_t f = sqrtTemp[5];
        uint64_t g = sqrtTemp[6];
        uint64_t h = sqrtTemp[7];
        

        for (int i = 0; i < 80; ++i) {
            uint64_t S1 = rotateRightByN<uint64_t>(e, 14, 64) ^ rotateRightByN<uint64_t>(e, 18, 64) ^ rotateRightByN<uint64_t>(e, 41, 64);
            uint64_t ch = (e & f) ^ (~e & g);
            uint64_t temp1 = h + S1 + ch + K[i] + w[i];
            uint64_t S0 = rotateRightByN<uint64_t>(a, 28, 64) ^ rotateRightByN<uint64_t>(a, 34, 64) ^ rotateRightByN<uint64_t>(a, 39, 64);
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
    // SHA-384 uses the first 6 64-bit words (384 bits)
    for (int i = 0; i < 6; ++i)
        for (int j = 63; j >= 0; --j)
            digest.push_back((sqrtTemp[i] >> j) & 1);
    return digest;
}


void sha384(string strMessage)
{
    // SHA-384 Initial Hash Values
    uint64_t H[8] = {
        0xcbbb9d5dc1059ed8ULL, 0x629a292a367cd507ULL, 0x9159015a3070dd17ULL, 0x152fecd8f70e5939ULL,
        0x67332667ffc00b31ULL, 0x8eb44a8768581511ULL, 0xdb0c2e0d64f98fa7ULL, 0x47b5481dbefa4fa4ULL
    };

    uint64_t K[80] = {
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
    
    vector<bool> binMessage, hash;
    size_t messageBitLength = 0;
    bitset<384> digest;

    binMessage = TextToBinaryString(strMessage, messageBitLength);
    preProcessing(messageBitLength, binMessage);
    hash = processing(binMessage, H, K);

    for (int i = 0; i < 384; ++i) {
        digest[i] = hash[i];
    }

    cout << bitsetToHex<bitset<384>>(digest, 384) << endl;
}

int main()
{
    // Read entire input from stdin
    string input((istreambuf_iterator<char>(cin)), istreambuf_iterator<char>());
    sha384(input);
    cout << endl;
    return 0;
}
