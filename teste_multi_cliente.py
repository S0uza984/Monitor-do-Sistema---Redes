#!/usr/bin/env python3
"""
script para teste de conexoes entre cliente e servidor.
"""

import socket
import threading
import time
import sys

def cliente_teste(id_cliente, delay=0):
    """simula um cliente conectando ao servidor"""
    try:
        time.sleep(delay)  # delay entre conexoes
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 9999))
        
        print(f"Cliente {id_cliente}: Conectado!")
        
        # recebe resposta
        response = client.recv(1024).decode("utf-8")
        print(f"Cliente {id_cliente}: {response}")
        
        if "LIMITE DE CLIENTES ATINGIDO" in response:
            print(f"Cliente {id_cliente}: Rejeitado - limite atingido")
            client.close()
            return
        
        # recebe menu
        menu = client.recv(1024).decode("utf-8")
        print(f"Cliente {id_cliente}: Menu recebido")
        
        # testa comandos
        time.sleep(1)
        client.send("help".encode("utf-8"))
        
        time.sleep(2)
        client.send("cpu-3".encode("utf-8"))
        
        # aguarda
        time.sleep(5)
        
        # sai
        client.send("exit".encode("utf-8"))
        print(f"Cliente {id_cliente}: Desconectando...")
        
        client.close()
        
    except Exception as e:
        print(f"Cliente {id_cliente}: Erro - {e}")

def main():
    print("=== Teste do Sistema Multi-Cliente ===")
    print("Certifique-se de que o servidor está rodando!")
    print("Pressione Enter para começar o teste...")
    input()
    
    # cria clientes
    threads = []
    num_clientes = 7  # acima do limite
    
    for i in range(num_clientes):
        delay = i * 0.5  # delay entre clientes
        thread = threading.Thread(target=cliente_teste, args=(i+1, delay))
        threads.append(thread)
        thread.start()
    
    # aguarda threads
    for thread in threads:
        thread.join()
    
    print("\n=== Teste concluído ===")

if __name__ == "__main__":
    main()
