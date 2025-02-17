import sys                  # Para ter acesso ao argv
import logging              # Biblioteca de criação de logs
from typing import Optional # Anotações de tipo
import Server               # Minha implementação do servidor
import Configuration        # Configurações do Servidor

"""
**** migs' Minimal HTTP Server ****

Um mini servidor HTTP estático que processa requisições GET, HEAD e OPTIONS no localhost:9999 (porta padrão, outras podem ser informadas)

Retorna o conteúdo da pasta Content/ (por padrão as páginas do meu blog pessoal (miguelanunes.github.io)) para as requisições GET
Retorna apenas o cabeçalho das requisições GET para as requisições HEAD
Retorna {"accepted_methods": ["GET", "HEAD", "OPTIONS"]} para as requisições OPTIONS
"""

# TODO: Implementar uma requisição que desliga o servidor graciosamente
# TODO: Implementar decorators em algumas validações e verificações

# Configurando o sistema de logging da biblioteca logging
log = logging.getLogger("Main")
logging.basicConfig(filename="server.log", level=logging.DEBUG, filemode="w")
logging.Formatter("(%(asctime)s) [%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
# TODO: Arrumar formatação das msgs de log

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
    if (len(sys.argv) < 2):
        return None
        
    # Se sim, vejo se passou um int válido para ser uma porta
    try:
        port = int(sys.argv[1])
    except ValueError:
        return None
    
    # Verificando se o numero passado está dentro do que é valido para um porta
    # Se for, retorno a porta
    if 0 < port < 32720:
        log.info(f"Servidor usando a porta {port}")
        return port
    
    # Se não, não retorna nada
    return None

def get_cfg() -> Optional[str]:
    """
    Função que procesa um possível nome de arquivo de configuração passado na linha de comando quando o programa foi executado
    
    Recebe:
        Nada
    
    Retorna:
        O nome do arquivo cfg (str) caso tenha passado um nome válido
        None caso não tenha
    """
    
    # Primeiro, verifico se algum argumento de linha de comando foi passado
    if (len(sys.argv) < 3):
        return None
        
    # Se sim, vejo se passou um int válido para ser uma porta
    try:
        cfg = str(sys.argv[2])
    except ValueError:
        return None
    
    # Verificando se o numero passado está dentro do que é valido para um porta
    # Se for, retorno a porta
    if cfg.endswith(".toml"):
        log.info(f"Lendo arquivo de configuração {cfg}")
        return cfg
    
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
    
    # TODO: Colocar esses informes em outro lugar
    # print("Para definir a porta que o servidor irá usar para receber requisições, forneça ela na linha de comando quando iniciar o servidor")
    # print("\tPor exemplo, 'python Main.py 12345'")
    # print("Por padrão, o servidor usará a porta 9999")
    
    # Recuperando uma possível porta passada na linha de comando
    port = get_port()
    
    try:
        assert sys.version_info >= (3, 11)
    except AssertionError:
        print("É necessário executar o servidor com Python versão 3.11 ou mais recente!")
        return
    
    # Inicializando as configurações
    cfg = get_cfg()
    serverConfig = Configuration.ServerConfig(cfg)
    
    try:
        # Rodando o servidor com a porta fornecida
        Server.server(serverConfig, port)
    except KeyboardInterrupt:
        log.critical("Execução do servidor interrompida pelo teclado!")
        print("\nExecução Interrompida! Tentando encerrar graciosamente!")
    
    # Fechando o logger depois de fechar o servidor
    logging.shutdown()

if __name__ == "__main__":
    main()