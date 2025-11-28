"""
Hash calculation logic module.
Handles both synchronous (text) and asynchronous (file) hash calculations.
"""

import os
import subprocess
import hashlib
import threading
import queue
import re
from typing import Optional, Callable, Dict, Any
import tkinter as tk  # For messagebox if needed, though ideally we'd raise exceptions

from config import HashAlgorithm

class HashCalculator:
    """Handles hash calculations."""
    
    def __init__(self):
        self._current_process: Optional[subprocess.Popen] = None
    
    def calculate_text_sync(self, algorithms: list[str], text: str) -> dict[str, str]:
        """
        Calculate hashes for text synchronously.
        
        Args:
            algorithms: List of algorithm names
            text: Input text
            
        Returns:
            Dictionary mapping algorithm name to hash string
        """
        results = {}
        input_bytes = text.encode('utf-8')
        
        for algo in algorithms:
            algo_config = HashAlgorithm.get_algorithm_config(algo)
            if not algo_config:
                results[algo] = f"Error: Unknown algorithm"
                continue
                
            algo_type = algo_config.get('type')
            
            if algo_type == 'executable':
                executable_name = algo_config.get('executable')
                if not executable_name:
                    results[algo] = "Error: No executable specified"
                    continue
                
                script_dir = os.path.dirname(os.path.abspath(__file__))
                executable_path = os.path.join(script_dir, executable_name)
                
                if not os.path.exists(executable_path):
                    results[algo] = "Error: Executable not found"
                    continue
                
                try:
                    result = subprocess.run(
                        [executable_path],
                        input=input_bytes,
                        capture_output=True,
                        check=True,
                        timeout=5
                    )
                    results[algo] = result.stdout.decode('utf-8').strip()
                except Exception as e:
                    results[algo] = f"Error: {str(e)}"
            elif algo_type == 'hashlib':
                # Handle hashlib types for text too
                hashlib_name = algo_config.get('hashlib_name')
                h = hashlib.new(hashlib_name)
                h.update(input_bytes)
                results[algo] = h.hexdigest()
            else:
                results[algo] = f"Error: Unknown type {algo_type}"
                
        return results

    def calculate_file(self, 
                      algorithms: list[str], 
                      file_path: str, 
                      progress_callback: Callable[[int], None],
                      check_cancel_callback: Callable[[], bool],
                      error_callback: Callable[[str], None],
                      success_callback: Callable[[dict[str, str]], None]) -> None:
        """
        Calculate multiple hashes for a file in a single pass.
        
        Args:
            algorithms: List of algorithm names
            file_path: Path to file
            progress_callback: Function to call with progress percentage
            check_cancel_callback: Function that returns True if calculation should be cancelled
            error_callback: Function to call with error message
            success_callback: Function to call with result dictionary
        """
        # Map algorithm names to hashlib functions/constructors
        hashlib_map = {
            'SHA-256': hashlib.sha256,
            'SHA-384': hashlib.sha384,
            'SHA-512': hashlib.sha512
        }
        
        # Separate algorithms into fast (hashlib/zlib) and slow (subprocess)
        fast_algos = []
        subprocess_algos = []
        
        for algo in algorithms:
            if algo in hashlib_map or algo == 'CRC-32':
                fast_algos.append(algo)
            else:
                subprocess_algos.append(algo)
        
        results = {}
        
        try:
            # 1. Process all fast algorithms in ONE pass
            if fast_algos:
                file_size = os.path.getsize(file_path)
                CHUNK_SIZE = 16 * 1024 * 1024  # 16MB
                bytes_processed = 0
                last_progress = 0
                
                # Initialize hashers
                hashers = {}
                crc_val = 0
                
                for algo in fast_algos:
                    if algo == 'CRC-32':
                        crc_val = 0
                    else:
                        hashers[algo] = hashlib_map[algo]()
                
                import zlib
                
                with open(file_path, 'rb') as f:
                    while True:
                        if check_cancel_callback():
                            return
                        
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        
                        # Update all hashers with the same chunk
                        for algo in fast_algos:
                            if algo == 'CRC-32':
                                crc_val = zlib.crc32(chunk, crc_val)
                            else:
                                hashers[algo].update(chunk)
                        
                        bytes_processed += len(chunk)
                        current_progress = int((bytes_processed / file_size) * 100)
                        
                        if current_progress >= last_progress + 5:
                            progress_callback(current_progress)
                            last_progress = current_progress
                
                # Finalize results
                for algo in fast_algos:
                    if algo == 'CRC-32':
                        results[algo] = format(crc_val & 0xFFFFFFFF, '08x')
                    else:
                        results[algo] = hashers[algo].hexdigest()

            # 2. Process subprocess algorithms (sequentially, unfortunately)
            # Note: Running these in parallel with fast algos would be complex due to disk I/O contention
            for algo in subprocess_algos:
                if check_cancel_callback():
                    return
                    
                # We reuse the single-file subprocess logic but adapt it
                # For now, let's just run them one by one. 
                # Ideally, we shouldn't mix fast and slow algos often.
                self._calculate_file_subprocess(
                    algo, 
                    file_path, 
                    progress_callback, # This might be jumpy if mixed with fast ones
                    check_cancel_callback, 
                    lambda res: results.update({algo: res})
                )
            
            success_callback(results)
            
        except Exception as ex:
            error_callback(str(ex))

    def _calculate_file_subprocess(self, 
                                  algorithm: str, 
                                  file_path: str, 
                                  progress_callback: Callable[[int], None],
                                  check_cancel_callback: Callable[[], bool],
                                  success_callback: Callable[[str], None]) -> None:
        """Internal method for subprocess fallback."""
        algo_config = HashAlgorithm.get_algorithm_config(algorithm)
        
        if not algo_config or algo_config.get('type') != 'executable':
            raise ValueError("Invalid algorithm configuration")
        
        executable_name = algo_config.get('executable')
        if not executable_name:
            raise ValueError("No executable specified")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        executable_path = os.path.join(script_dir, executable_name)
        
        if not os.path.exists(executable_path):
            raise FileNotFoundError(f"Executable not found: {executable_name}")
        
        # Launch C++ process
        proc = subprocess.Popen(
            [executable_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
        
        self._current_process = proc
        
        try:
            CHUNK_SIZE = 16 * 1024 * 1024
            
            # Thread to read stderr for progress
            progress_queue = queue.Queue()
            
            def read_stderr():
                progress_pattern = re.compile(r'PROGRESS:(\d+)')
                while True:
                    line = proc.stderr.readline()
                    if not line:
                        break
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    match = progress_pattern.match(line_str)
                    if match:
                        progress_queue.put(int(match.group(1)))
            
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stderr_thread.start()
            
            # Stream file to stdin
            with open(file_path, 'rb') as f:
                while True:
                    if check_cancel_callback():
                        proc.terminate()
                        proc.wait()
                        return
                    
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    proc.stdin.write(chunk)
                    
                    while not progress_queue.empty():
                        progress_callback(progress_queue.get())
            
            proc.stdin.close()
            
            # Wait for completion
            while True:
                if check_cancel_callback():
                    proc.terminate()
                    proc.wait()
                    return
                if proc.poll() is not None:
                    break
                while not progress_queue.empty():
                    progress_callback(progress_queue.get())
            
            stdout, _ = proc.communicate()
            
            if proc.returncode != 0:
                raise RuntimeError("Hash calculation failed")
            
            success_callback(stdout.decode('utf-8').strip())
            
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()
            self._current_process = None

    def terminate_subprocess(self):
        """Force terminate any running subprocess."""
        if self._current_process and self._current_process.poll() is None:
            self._current_process.terminate()
            try:
                self._current_process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                self._current_process.kill()
