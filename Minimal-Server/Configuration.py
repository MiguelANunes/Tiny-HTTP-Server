import logging              # Biblioteca de criação de logs
import tomllib              # Para acessar arquivos do sistema
import sys                  # Para ter acesso ao argv
from typing import Optional # Anotações de tipo

"""
Arquivo que vai carregar as configurações do servidor

TODO: Melhorar essa descrição
"""

log = logging.getLogger("Main.Configuration")

class ServerConfig():
    """
    Classe que armazena os dados de configuração do servidor
    Dados são lidos do arquivo config.toml
    Caso esse arquivo não for encontrado, levanta um erro
    """
    
    def __init__(self, cfgName:Optional[str]=None) -> None:
        """
        Construtor da classe de configuração
        
        Recebe um argumento opcional que é o nome do arquivo de configuração
        
        TODO: Melhorar essa documentação
        """
        
        # Validando nome do arquivo de configuração
        if cfgName is None:
            cfgName = "config.toml"
        
        # Abrindo o arquivo e recuperando as configurações
        with open(cfgName, mode="rb") as cfgFP:
            rawConfig = tomllib.load(cfgFP)
            
            # Recuperando Configurações
            
            # TODO: Fazer validações aqui para garantir que esses campos sempre serão carregados
            
            # Configurações básicas
            self.implemmentedMethods = rawConfig["implemented_methods"]
            self.httpVersion         = rawConfig["http_version"]
            self.port                = rawConfig["port"]
            self.host                = rawConfig["host"]
            self.serverName          = rawConfig["server_name"]
            
            # Caminhos e Arquivos Proibidos
            self.forbiddenPaths = rawConfig["Forbidden"]["paths"]
            self.forbiddenFiles = rawConfig["Forbidden"]["files"]
            
            # Caminhos e Arquivos Permitidos
            self.allowedPaths = rawConfig["Allowed"]["paths"]
            self.allowedFiles = rawConfig["Allowed"]["files"]
    
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
            
def init_config() -> ServerConfig:
    """
    TODO: Documentar essa função
    """
    # Recuperando um possível nome de arquivo de configuração passado na linha de comando
    cfg = get_cfg()
    
    config = ServerConfig(cfg)
    
    return config