import socket
import threading


def receive_messages(client_socket: socket.socket, stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[!] Сервер закрыл соединение.")
                stop_event.set()
                break

            print(data.decode("utf-8", errors="replace"), end="")

        except OSError:
            # сокет закрыт
            stop_event.set()
            break
        except Exception:
            print("\n[!] Ошибка при получении данных.")
            stop_event.set()
            break


def run_client(host="127.0.0.1", port=5001):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((host, port))
        print(f"Подключено к серверу {host}:{port}")
        print("Пишите сообщения. Для выхода: /exit\n")

        stop_event = threading.Event()

        t = threading.Thread(target=receive_messages, args=(client_socket, stop_event), daemon=True)
        t.start()

        while not stop_event.is_set():
            try:
                msg = input()
            except (EOFError, KeyboardInterrupt):
                msg = "/exit"

            if not msg:
                continue

            try:
                client_socket.sendall((msg + "\n").encode("utf-8"))
            except Exception:
                print("[!] Не удалось отправить сообщение (соединение потеряно).")
                stop_event.set()
                break

            if msg.lower() in ("/exit", "/quit"):
                stop_event.set()
                break

    except ConnectionRefusedError:
        print(f"Ошибка: сервер не запущен на {host}:{port}")
    finally:
        try:
            client_socket.close()
        except:
            pass
        print("Клиент завершил работу.")


if __name__ == "__main__":
    run_client()