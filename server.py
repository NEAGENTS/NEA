import socket
import sys
import traceback
import io
import threading
import signal

# Constants
MAX_DATA_SIZE = 4096  # Maximum size for incoming data to prevent abuse
NEA_NAME = "NEA (Network Evolved Agents)"
NEA_VERSION = "1.0.0"

def execute_code(code):
    """Execute the given Python code in a controlled environment and capture output."""
    # Separate execution context for each call
    exec_globals = {}
    exec_locals = {}

    stdout = io.StringIO()
    stderr = io.StringIO()

    # Redirect stdout and stderr to capture the output
    sys.stdout = stdout
    sys.stderr = stderr

    try:
        exec(code, exec_globals, exec_locals)
    except Exception:
        # Capture exception traceback
        traceback.print_exc(file=stderr)
    finally:
        # Restore original stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Return combined output and error messages
    return stdout.getvalue() + stderr.getvalue()


def handle_client(conn, addr):
    """Handle communication with a connected client."""
    print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(MAX_DATA_SIZE)
            if not data:
                break

            code = data.decode('utf-8').strip()
            
            if code.upper() == "NEA:INFO":
                # Provide NEA information
                output = f"{NEA_NAME}\nVersion: {NEA_VERSION}\nStatus: Online\n"
            else:
                # Execute user-provided code
                output = execute_code(code)

            conn.sendall(output.encode('utf-8'))
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection with {addr} closed.")


def start_server(host='0.0.0.0', port=65432):
    """Start the NEA server."""
    def signal_handler(sig, frame):
        print("\nShutting down NEA server...")
        sys.exit(0)

    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print(f"Starting {NEA_NAME}...")
    print(f"Version: {NEA_VERSION}")
    print(f"Listening on {host}:{port}\n")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"{NEA_NAME} is now online. Waiting for connections...\n")

        while True:
            try:
                conn, addr = server_socket.accept()
                # Handle client in a separate thread
                client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
            except Exception as e:
                print(f"Server error: {e}")


if __name__ == "__main__":
    start_server()
