import os
import sys
import subprocess

def find_python():
    # Try venv first
    venv_py_win = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
    
    if os.path.exists(venv_py_win):
        return venv_py_win
    
    # Try common aliases
    for cmd in ["py", "python", "python3"]:
        try:
            # On windows, 'py' or 'python' should work. 
            # We use shell=True for 'py' to be found correctly in some environments, 
            # though usually not needed for subprocess.run list.
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            return cmd
        except:
            continue
    return None

def main():
    py_cmd = find_python()
    if not py_cmd:
        print("Error: Could not find Python. Please ensure it is installed and in your PATH.")
        return

    backend_path = os.path.join(os.getcwd(), "backend", "server.py")
    if not os.path.exists(backend_path):
        print(f"Error: Could not find backend server at {backend_path}")
        return

    print("--- YojnaAI Unified Backend Startup ---")
    print(f"Using Python: {py_cmd}")
    print(f"Starting backend at: {backend_path}")
    
    # Set environment variable for UTF-8 encoding to prevent UnicodeEncodeError on Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Run the backend server
    try:
        # Use shell=True if py_cmd is just a name and subprocess.run can't find it
        subprocess.run([py_cmd, backend_path], env=env)
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")

if __name__ == "__main__":
    main()
