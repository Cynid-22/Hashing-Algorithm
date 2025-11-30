#ifndef sha_H
#define sha_H

#include <bits/stdc++.h>
#include <vector>
#include <string>

using namespace std;

vector<bool> TextToBinaryString(const string& words, size_t& bitLength)
{
    vector<bool> bits;
    for (char c : words) {
        bitset<8> b(c);
        for (int i = 7; i >= 0; --i) {
            bits.push_back(b[i]);
        }
    }
    bitLength = bits.size();
    return bits;
}

template <typename T> //uint32_t or uint64_t
T bitsToUsignedInt(const vector<bool>& bits, size_t start)
{
    T value = 0;
    for (size_t i = 0; i < sizeof(T) * 8; ++i) {
        value <<= 1;
        if (bits[start + i])
            value |= 1;
        else
            value |= 0;
    }
    return value;
}

template <typename T> //uint32_t or uint64_t
T rotateRightByN(T x, unsigned int n, int digestsBit)
{
    return (x >> n) | (x << (digestsBit - n));
}

template <typename T> //bitset<256> or bitset<512>
string bitsetToHex(const T& bits, int digestsBit)
{
    stringstream ss;

    for (int i = digestsBit - 4; i >= 0; i -= 4) {
        int value = 0;
        for (int j = 0; j < 4; ++j) {
            if (bits[i + j]) {
                value |= (1 << (3 - j));
            }
        }
        ss << hex << value;
    }

    string reversing = ss.str();
    reverse(reversing.begin(), reversing.end());
    return reversing;
}

#endif