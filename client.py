import socket
import threading
import time
import sys

def receive(client,stop_client):
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
            print("Erro na conexão: não foi possivel se conectar ao servidor, ou a conexão foi encerrada")
            client.close()
            stop_client.set()
            break
        

def write(client,stop_client):
    time.sleep(0.5)  # Espera um momento para garantir que a thread de recepção esteja pronta
    while not stop_client.is_set():
        try:
            message = input()
            client.send(message.encode("utf-8"))
            time.sleep(0.1)
            if message.strip().lower() == "exit":
                client.close()
                stop_client.set()
                break
        
        except KeyboardInterrupt:
            print("\nMonitor desligado por interrupção\n")
        except Exception:
            print("Erro ao enviar mensagem: a conexão com o servidor foi perdida")
            client.close()
            stop_client.set()
            break
    


def Main():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stop_client = threading.Event()
    
    try:
        client.connect(('127.0.0.1', 9999))


        receive_thread = threading.Thread(target=receive, args=(client, stop_client))
        receive_thread.start()

        write_thread = threading.Thread(target=write, args=(client, stop_client))
        write_thread.start()

        while receive_thread.is_alive() or write_thread.is_alive():
            receive_thread.join(1)
            write_thread.join(1)
        
    except KeyboardInterrupt:
        print("\nMonitor encerrado por interrupção\n")

        stop_client.set()

        receive_thread.join()
        write_thread.join()

    except Exception:
        print(f"\nErro ao tentar se conectar ao servidor\n")
        return

if __name__ == "__main__":
    Main()
    

