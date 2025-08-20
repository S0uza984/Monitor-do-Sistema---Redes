import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9999))

def receive():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
            if "Saindo da conexão" in message:
                client.close()
                break
        except Exception as e:
            print("Ocorreu um erro.",e)
            client.close()
            break

def write():
    while True:
        try:
            message = input("")
            client.send(message.encode("utf-8"))
        except:
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
