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
                print("Conexão perdida com o servidor.")
                client.close()
                stop_client.set()
                break
            
            print(message)
            
            # verifica limite
            if "LIMITE DE CLIENTES ATINGIDO" in message:
                print("Servidor rejeitou a conexão - limite de clientes atingido.")
                client.close()
                stop_client.set()
                break
            
            # verifica desconexao
            if "Desconectando seu monitor do servidor" in message:
                print("Servidor confirmou a desconexão.")
                client.close()
                stop_client.set()
                break
            
        except Exception as e:
            print("Erro na conexão:", e)
            client.close()
            stop_client.set()
            break
        

def write(stop_client):
    while not stop_client.is_set():
        try:
            message = input("Digite um comando (ou 'exit' para desconectar): ")
            client.send(message.encode("utf-8"))
            time.sleep(0.1)
            if message.strip().lower() == "exit":
                print("Solicitando desconexão...")
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
    
    receive_thread = threading.Thread(target=receive, args=(stop_client,))
    receive_thread.start()

    write_thread = threading.Thread(target=write, args=(stop_client,))
    write_thread.start()
    
Main()
    

