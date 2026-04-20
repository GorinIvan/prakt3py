import socket
import threading

clients = []  # список dict: {"sock": socket, "addr": (ip, port), "name": str}
client_lock = threading.Lock()


def safe_send(sock: socket.socket, text: str) -> bool:
    """Отправка строки; возвращает False если отправить не удалось."""
    try:
        sock.sendall(text.encode("utf-8"))
        return True
    except:
        return False


def broadcast(text: str, exclude_sock: socket.socket | None = None):
    """Отправить всем клиентам, кроме exclude_sock (если задан)."""
    dead_socks = []

    with client_lock:
        for c in clients:
            sock = c["sock"]
            if exclude_sock is not None and sock == exclude_sock:
                continue
            ok = safe_send(sock, text)
            if not ok:
                dead_socks.append(sock)
                
        if dead_socks:
            clients[:] = [c for c in clients if c["sock"] not in dead_socks]
            for s in dead_socks:
                try:
                    s.close()
                except:
                    pass


def handle_client(client_socket: socket.socket, client_address):
    name = f"{client_address[0]}:{client_address[1]}"

    safe_send(client_socket, f"Добро пожаловать в чат! Вы: {name}\n")
    
    broadcast(f"[SYSTEM] {name} вошёл в чат\n", exclude_sock=client_socket)

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode("utf-8", errors="replace").strip()
            if not message:
                continue

            if message.lower() in ("/quit", "/exit"):
                break

            print(f"От {name}: {message}")

            broadcast(f"{name}: {message}\n", exclude_sock=client_socket)

    except ConnectionResetError:
        pass
    except Exception:
        pass
    finally:
        with client_lock:
            clients[:] = [c for c in clients if c["sock"] != client_socket]

        try:
            client_socket.close()
        except:
            pass

        print(f"Клиент отключился {name}")
        broadcast(f"[SYSTEM] {name} покинул чат\n", exclude_sock=None)


def run_chat_server(host="127.0.0.1", port=5001):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f"Сервер ждёт подключения на {host}:{port}...")

    while True:
        client_socket, client_address = server.accept()

        with client_lock:
            clients.append({"sock": client_socket, "addr": client_address, "name": f"{client_address[0]}:{client_address[1]}"})

        print(f"Клиент {client_address} подключен")
        threading.Thread(
            target=handle_client,
            args=(client_socket, client_address),
            daemon=True
        ).start()


if __name__ == "__main__":
    run_chat_server()
