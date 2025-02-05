import sys # Para ter acesso ao argv
from typing import Optional # Anotações de tipo

"""
Função principal do servidor HTTP

Processa uma eventual porta passada por linha de comando e inicia o processo do servidor
"""

# TODO: Fazer mensagens de aviso decentes

import Server

def get_port() -> Optional[int]:
    """
    Função que procesa um possível valor de porta passado na linha de comando quando o programa foi executado
    
    Recebe:
        Nada
    
    Retorna:
        O número da porta (int) caso tenha passado uma porta válida
        None caso não tenha
    """
    
    # Primeiro, verifico se algum argumento de linha de comando foi passado
    if (len(sys.argv) != 2):
        # FIXME: Vou assumir que o único argumento possível é o número da porta
        return None
        
    # Se sim, vejo se passou um int válido para ser uma porta
    try:
        port = int(sys.argv[1])
    except ValueError:
        return None
    
    # Verificando se o numero passado está dentro do que é valido para um porta
    # Se for, retorno a porta
    if 0 < port < 32720:
        print(f"***Listening on port {port}***")
        return port
    
    # Se não, não retorna nada
    return None

if __name__ == "__main__":
    print("migs' HTTP Server in Python!")
    
    print("To set a port for the server to listen to, set it in the command line when starting the server")
    print("By default, the server will listen to port 9999")
    
    # Recuperando uma possível porta passada na linha de comando
    port = get_port()
    
    # Rodando o servidor com a porta fornecida
    Server.server(port)