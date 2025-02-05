import sys # Para ter acesso ao argv
from typing import Optional # Anotações de tipo

"""
**** migs' Minimal HTTP Server ****

Um micro servidor HTTP estático que processa requisições GET, HEAD e OPTIONS no localhost:9999 (porta padrão, outras podem ser informadas)

Retorna o conteúdo da pasta Content/ (por padrão as páginas do meu blog pessoal (miguelanunes.github.io)) para as requisições GET
Retorna apenas o cabeçalho das requisições GET para as requisições HEAD
Retorna {"accepted_methods": ["GET", "HEAD", "OPTIONS"]} para as requisições OPTIONS
"""

# TODO: Fazer mensagens de aviso decentes
# TODO: Fazer um sistema para criar logs

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
        print(f"\n\t>>>USANDO A PORTA {port}<<<\n")
        return port
    
    # Se não, não retorna nada
    return None

def main() -> None:
    """
    Função principal, que inicia o processo do servidor
    
    Recebe:
        Nada
        
    Retorna:
        Nada
    """
    
    print("migs' HTTP Server")
    
    print("Para definir a porta que o servidor irá usar para receber requisições, forneça ela na linha de comando quando iniciar o servidor")
    print("\tPor exemplo, 'python Main.py 12345'")
    print("Por padrão, o servidor usará a porta 9999")
    
    # Recuperando uma possível porta passada na linha de comando
    port = get_port()
    
    # Rodando o servidor com a porta fornecida
    Server.server(port)

if __name__ == "__main__":
    main()