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

// Convert CRC-32 value to hexadecimal string
string crc32ToHex(uint32_t crc)
{
    stringstream ss;
    ss << hex << setfill('0') << setw(8) << crc;
    return ss.str();
}

int main(int argc, char* argv[])
{
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
    
    uint32_t crcTable[256];
    generateCRC32Table(crcTable);
    
    uint32_t crc = 0xFFFFFFFF; // Initial value
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
        
        for (size_t i = 0; i < bytesRead; ++i) {
            uint8_t index = (crc ^ buffer[i]) & 0xFF;
            crc = (crc >> 8) ^ crcTable[index];
        }
        
        totalBytes += bytesRead;
        
        // Report progress
        if (totalExpectedSize > 0) {
            reportProgress(totalBytes, totalExpectedSize);
        }
    }
    
    crc ^= 0xFFFFFFFF; // Final XOR
    
    cout << crc32ToHex(crc);
    cout.flush();
    cout << endl;
    
    return 0;
}
