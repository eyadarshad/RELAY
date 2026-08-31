import subprocess
import sys
import time
import os
import signal

def main():
    print("=" * 60)
    print("   RELAY // AUTONOMOUS BUSINESS OPERATIONS AGENT")
    print("   CALL-E Hackathon 2026 Engine")
    print("=" * 60)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    # 1. Start FastAPI Backend on port 8000
    print("[1/2] Launching FastAPI Backend on http://127.0.0.1:8000...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=root_dir)

    time.sleep(2)

    # 2. Start Next.js Frontend on port 3000
    print("[2/2] Launching Next.js Frontend on http://localhost:3000...")
    # Use npm.cmd on Windows
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir)

    print("\n✓ RELAY Full-Stack System Running:")
    print("  ► Frontend Dashboard:  http://localhost:3000")
    print("  ► Backend REST / WS:   http://127.0.0.1:8000")
    print("  ► API Swagger Docs:    http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to terminate both servers.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down RELAY servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
