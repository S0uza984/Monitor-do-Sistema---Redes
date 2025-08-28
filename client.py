import socket
import threading
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9999))

def receive(stop_client):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                client.close()
                stop_client.set()
                break
            
            print(message)
            if "Saindo da conexão" in message:
                client.close()
                stop_client.set()
                break
            
        except:
            client.close()
            stop_client.set()
            break
        

def write(stop_client):
    while not stop_client.is_set():
        try:
            message = input("digite um comando:")
            client.send(message.encode("utf-8"))
            time.sleep(0.1)
            if message.strip().lower() == "exit":
                client.close()
                stop_client.set()
                break
            
        except Exception as e:
            print("Erro ao enviar mensagem:", e)
            client.close()
            stop_client.set()
            break



def Main():
    
    stop_client = threading.Event()
    
    receive_thread = threading.Thread(target=receive, args={stop_client,})
    receive_thread.start()

    write_thread = threading.Thread(target=write, args={stop_client,})
    write_thread.start()
    
Main()
    

