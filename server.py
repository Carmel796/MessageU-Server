import socket, threading
from handlers.connection import handle_request

DEFAULT_PORT = 1357
HOST = "127.0.0.1"

def read_port(path="myport.info", default=DEFAULT_PORT) -> int:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        port = int(raw)
        if not (1 <= port <= 65535):
            raise ValueError("port out of range")  # triggers fallback below
        return port
    except FileNotFoundError:
        print(f"{path} not found; using default port {default}")
    except ValueError:
        print(f"Invalid port in {path}; using default port {default}")
    return default

def main():
    port = read_port()
    print(f"Starting server on port {port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.bind((HOST, port))
        srv.listen()

        while True:
            conn, addr = srv.accept()
            print(f"New connection received")
            t = threading.Thread(target=handle_request, args=(conn, addr))
            t.start()


if __name__ == "__main__":
    main()