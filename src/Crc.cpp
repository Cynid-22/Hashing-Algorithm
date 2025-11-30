#include <iostream>
#include <string>
#include <vector>
#include <iomanip>
#include <sstream>
#include <cstdint>
#include "common.h"

using namespace std;

// CRC-32 polynomial (IEEE 802.3)
const uint32_t CRC32_POLYNOMIAL = 0xEDB88320;

// Generate CRC-32 lookup table
void generateCRC32Table(uint32_t table[256])
{
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t crc = i;
        for (uint32_t j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ CRC32_POLYNOMIAL;
            } else {
                crc >>= 1;
            }
        }
        table[i] = crc;
    }
}

// Calculate CRC-32 checksum
uint32_t calculateCRC32(const string& data, uint32_t table[256])
{
    uint32_t crc = 0xFFFFFFFF; // Initial value

    for (char c : data) {
        uint8_t byte = static_cast<uint8_t>(c);
        uint8_t index = (crc ^ byte) & 0xFF;
        crc = (crc >> 8) ^ table[index];
    }

    return crc ^ 0xFFFFFFFF; // Final XOR
}

// Convert CRC-32 value to hexadecimal string
string crc32ToHex(uint32_t crc)
{
    stringstream ss;
    ss << hex << setfill('0') << setw(8) << crc;
    return ss.str();
}

// Main CRC-32 function
void crc32(const string& strMessage)
{
    uint32_t crcTable[256];
    generateCRC32Table(crcTable);
    
    uint32_t crc = calculateCRC32(strMessage, crcTable);
    
    cout << crc32ToHex(crc);
}

int main()
{
    initBinaryMode();
    
    string input = readStdinToString();
    size_t totalSize = input.length();
    
    reportProgress(0, totalSize);
    crc32(input);
    reportProgress(totalSize, totalSize);
    
    cout << endl;
    return 0;
}
