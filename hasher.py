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
    
    def calculate_text_sync(self, algorithm: str, text: str) -> str:
        """
        Calculate hash for text synchronously.
        
        Args:
            algorithm: Name of the algorithm
            text: Input text
            
        Returns:
            The calculated hash string
            
        Raises:
            ValueError: If algorithm config is invalid
            RuntimeError: If calculation fails
        """
        algo_config = HashAlgorithm.get_algorithm_config(algorithm)
        if not algo_config:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        input_bytes = text.encode('utf-8')
        
        algo_type = algo_config.get('type')
        
        if algo_type == 'executable':
            executable_name = algo_config.get('executable')
            if not executable_name:
                raise ValueError(f"No executable specified for {algorithm}")
            
            # Get the directory where this script is located
            # Note: We assume this script is in the same dir as the executables
            script_dir = os.path.dirname(os.path.abspath(__file__))
            executable_path = os.path.join(script_dir, executable_name)
            
            if not os.path.exists(executable_path):
                raise FileNotFoundError(
                    f"Executable not found: {executable_name}\n"
                    f"Please compile the C++ files first."
                )
            
            try:
                result = subprocess.run(
                    [executable_path],
                    input=input_bytes,
                    capture_output=True,
                    check=True,
                    timeout=5
                )
                return result.stdout.decode('utf-8').strip()
            except subprocess.TimeoutExpired:
                raise RuntimeError("Hash calculation timed out")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Hash calculation failed: {e}")
        else:
            raise ValueError(f"Unknown algorithm type: {algo_type}")

    def calculate_file(self, 
                      algorithm: str, 
                      file_path: str, 
                      progress_callback: Callable[[int], None],
                      check_cancel_callback: Callable[[], bool],
                      error_callback: Callable[[str], None],
                      success_callback: Callable[[str], None]) -> None:
        """
        Calculate hash for a file. Designed to be run in a separate thread.
        
        Args:
            algorithm: Algorithm name
            file_path: Path to file
            progress_callback: Function to call with progress percentage (0-100)
            check_cancel_callback: Function that returns True if calculation should be cancelled
            error_callback: Function to call with error message
            success_callback: Function to call with result hash
        """
        # Map algorithm names to hashlib functions
        hashlib_map = {
            'SHA-256': hashlib.sha256,
            'SHA-384': hashlib.sha384,
            'SHA-512': hashlib.sha512
        }
        
        try:
            # Check if we have a fast Python implementation
            if algorithm in hashlib_map:
                self._calculate_file_hashlib(
                    hashlib_map[algorithm], 
                    file_path, 
                    progress_callback, 
                    check_cancel_callback, 
                    success_callback
                )
            elif algorithm == 'CRC-32':
                self._calculate_file_crc32(
                    file_path, 
                    progress_callback, 
                    check_cancel_callback, 
                    success_callback
                )
            else:
                # Fallback to C++ subprocess
                self._calculate_file_subprocess(
                    algorithm, 
                    file_path, 
                    progress_callback, 
                    check_cancel_callback, 
                    success_callback
                )
        except Exception as ex:
            error_callback(str(ex))

    def _calculate_file_hashlib(self, 
                               hash_constructor, 
                               file_path: str, 
                               progress_callback: Callable[[int], None],
                               check_cancel_callback: Callable[[], bool],
                               success_callback: Callable[[str], None]) -> None:
        """Internal method for hashlib calculation."""
        hash_func = hash_constructor()
        file_size = os.path.getsize(file_path)
        CHUNK_SIZE = 16 * 1024 * 1024  # 16MB
        bytes_processed = 0
        last_progress = 0
        
        with open(file_path, 'rb') as f:
            while True:
                if check_cancel_callback():
                    return
                
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                hash_func.update(chunk)
                
                bytes_processed += len(chunk)
                current_progress = int((bytes_processed / file_size) * 100)
                
                if current_progress >= last_progress + 5:
                    progress_callback(current_progress)
                    last_progress = current_progress
        
        success_callback(hash_func.hexdigest())

    def _calculate_file_crc32(self, 
                             file_path: str, 
                             progress_callback: Callable[[int], None],
                             check_cancel_callback: Callable[[], bool],
                             success_callback: Callable[[str], None]) -> None:
        """Internal method for CRC-32 calculation."""
        import zlib
        file_size = os.path.getsize(file_path)
        CHUNK_SIZE = 16 * 1024 * 1024
        bytes_processed = 0
        last_progress = 0
        crc = 0
        
        with open(file_path, 'rb') as f:
            while True:
                if check_cancel_callback():
                    return
                
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                crc = zlib.crc32(chunk, crc)
                
                bytes_processed += len(chunk)
                current_progress = int((bytes_processed / file_size) * 100)
                
                if current_progress >= last_progress + 5:
                    progress_callback(current_progress)
                    last_progress = current_progress
        
        success_callback(format(crc & 0xFFFFFFFF, '08x'))

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
        
        file_size = os.path.getsize(file_path)
        
        if check_cancel_callback():
            return
        
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
                    
                    # We can't easily track bytes sent vs processed by C++ here accurately 
                    # for progress bar without blocking, so we rely on C++ stderr reporting
                    # But we can check the queue
                    while not progress_queue.empty():
                        progress_callback(progress_queue.get())
            
            proc.stdin.close()
            
            # Wait for completion and final progress updates
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
                raise RuntimeError("Hash calculation failed (subprocess returned non-zero)")
            
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
