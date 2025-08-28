import socket
from datetime import datetime
import threading
import psutil


def send_message(client,msg):
    try:
        client.send(msg.encode("utf-8"))
    except:
        pass
    
def monitor_cpu(client,periodo,stop_cpu):
    while not stop_cpu.is_set():
        if stop_cpu.wait(periodo):
            break
        try:
            uso_cpu = psutil.cpu_percent(interval=None)
            client.send(f"Uso de CPU: {uso_cpu}%.".encode("utf-8"))
        except Exception:
            break
        
        
        
def monitor_memoria(client,periodo, stop_memoria):
    while not stop_memoria.is_set():
        if stop_memoria.wait(periodo):
            break
        try:
            uso_memoria = psutil.virtual_memory().percent
            client.send(f"Uso de memória em: {uso_memoria}%".encode("utf-8"))
        except Exception:
            break
    
    
        
def handle_client(client,addr,menu):
    
    stop_cpu = threading.Event()
    stop_mem = threading.Event()
    
    monitor_da_cpu = None
    monitor_da_memoria = None
    
    while True:
        try:
            msg_monitoramento = client.recv(1024).decode("utf-8").strip()
            
            if not msg_monitoramento:
                print(f"Monitor no ip: {str(addr)}, desconectado")
                break
            
            msg_lower = msg_monitoramento.lower()
            
            if msg_lower == "exit":
                print(f"Monitor no ip: {str(addr)}, desconectado")
                send_message(client,"Desconectando seu monitor do servidor")
                stop_cpu.set()
                stop_mem.set()
                break 
            
            if msg_lower == "quit":
                if monitor_da_cpu and monitor_da_cpu.is_alive() or monitor_da_memoria and monitor_da_memoria.is_alive():
                    stop_cpu.set()
                    stop_mem.set()
                    
                    stop_cpu = threading.Event()
                    stop_mem = threading.Event()
                    send_message(client,"Todos os monitores foram parados")
                else:
                    send_message(client,"Não há monitores a serem parados")
                continue
                
            if msg_lower == "help":
                send_message(client,menu)
                continue
            
            try:
                partes = msg_lower.split("-",1)
                comando = partes[0].strip()
                comando2 = partes[1].strip()
            except Exception as e:
                send_message(client,"Comando inválido. Use CPU-<segundos>, MEM-<segundos>, QUIT-<mem/memoria ou CPU> ou EXIT")
                continue
            
            if comando == "quit":
                    
                if comando2 in ("mem","memória"):
                    if monitor_da_memoria and monitor_da_memoria.is_alive():
                        stop_mem.set()
                    
                        stop_mem = threading.Event()
                        send_message(client,"Monitor da memoria parado")
                    else:
                        send_message(client,"Não há monitor de memoria a ser parado")
                elif comando2 == "cpu":
                    if monitor_da_cpu and monitor_da_cpu.is_alive():
                        stop_cpu.set()
                    
                        stop_cpu = threading.Event()
                        send_message(client,"Monitor da cpu parado")
                    else:
                        send_message(client,"Não há monitor de cpu a ser parado")
                else:
                    send_message(client,"Comando inválido. Use CPU-<segundos>, MEM-<segundos>, QUIT-<mem/memoria ou CPU> ou EXIT")    
            elif comando == "cpu":
                comando2 = int(comando2)
                if monitor_da_cpu and monitor_da_cpu.is_alive():
                    stop_cpu.set() 
                    
                stop_cpu = threading.Event()
                
                try:
                    client.send(f"Iniciando monitor da CPU a cada {comando2}s".encode("utf-8"))
                except Exception:
                    pass
                
                monitor_da_cpu = threading.Thread(target=monitor_cpu, args=(client,comando2,stop_cpu),  daemon= True)
                monitor_da_cpu.start() 
                
            elif comando in ("mem","memória"):
                comando2 = int(comando2)
                if monitor_da_memoria and monitor_da_memoria.is_alive():
                    stop_mem.set() 
                    
                stop_mem = threading.Event()
                
                try:
                    client.send(f"Iniciando monitor da MEMÓRIA a cada {comando2}s".encode("utf-8"))
                except Exception:
                    pass
                
                monitor_da_memoria = threading.Thread(target=monitor_memoria, args=(client,comando2,stop_mem), daemon=True)
                monitor_da_memoria.start()
            else:
                send_message(client,"Comando inválido. Use CPU-<segundos>, MEM-<segundos>, QUIT-<mem/memoria ou CPU> ou EXIT")
        except Exception as e:
            print("Ocorreu um erro:",e)
            client.close()
            break
    
    
    client.close()
    
        
            
            
def receive(server):
    while True:
        try:
            client, addr = server.accept()
            horario = datetime.now().strftime("<%H:%M:%S>")
            client.send(f"{horario}: CONECTADO".encode("utf-8"))
            menu = f"""
                Menu de Monitores Disponíveis:
                - Help                      : Reenvia as informações de cada comando
                - CPU-<segundos>            : Monitora o uso da CPU a cada <segundos>
                - MEMORIA-<segundos>        : Monitora o uso da memória a cada <segundos>
                - QUIT                      : Para todos os monitoramentos
                - QUIT-<mem/memoria ou cpu> : Para um monitoramento específico 
                - EXIT                      : Encerra a conexão
                Exemplo de uso: CPU-5
                """
            client.send(menu.encode("utf-8"))
            print(f"Conectado {str(addr)}")
            conexao_client_thread = threading.Thread(target=handle_client, args=(client,addr,menu))
            conexao_client_thread.start()
            
        except Exception as e:
            print("Ocorreu um erro no servido:",e)
            server.close()
            break
        
    server.close()
    
    

def Main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    
    print(f"Servidor iniciado com sucesso!")
    
    receive(server)
    
Main()
