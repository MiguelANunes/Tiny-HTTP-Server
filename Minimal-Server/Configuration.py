import logging                   # Biblioteca de criação de logs
import tomllib                   # Para acessar arquivos do sistema
from typing import Optional, Any # Anotações de tipo
import sys

"""
Arquivo que vai carregar as configurações do servidor

Lê as configurações de um arquivo .toml (config.toml por padrão) e carrega elas em um dicionário, atributo da classe ServerConfig
Caso algum valor de configuração que era esperado não foi encontrado, printa um erro no terminal e adiciona um aviso no log

TODO: Adicionar uma configuração para fazer shutdown graciosamente (algo tipo receber requisição "GET GRACIOUSLYSHUTDOWN/PRETTYPLEASE")
"""

log = logging.getLogger("Main.Configuration")

criticalConfig = ["implemented_methods", "http_version", "port", "host", "server_name", "content_root"]

def load_data(configs:"dict[str,Any]", configName:str, fileContents:"dict[str,Any]", key1:str, key2:Optional[str]=None) -> None:
    """
    Função que carrega as configurações lidas de um arquivo .toml em um dicinário
    Recebe o dicionário a ser carregado, o nome da chave que deve ser carregada nesse dicionário,
        os conteúdos do arquivo .toml em um dict e duas chaves para esse dict, a segunda sendo opcional
    Copia os conteúdos de fileContents[key1] (ou fileContents[key1][key2]) para configs[configName]
    Caso ocorra um erro ao ler fileContents[key1] (ou fileContents[key1][key2]) anota no log e printa uma mensagem de aviso no terminal
    
    Recebe:
        [dict] configs:      Um dicionário contendo as configurações a serem populadas
        [str] configName:    O nome da configuração a ser recuperada
        [dict] fileContents: Os dados que serão lidos para popular as configurações
        [str] key1, key2:    Chaves para acessarem os dados em fileContents, key2 é um valor opcional
    
    Retorna:
        Nada
    """
    
    if key2 is not None:
        try:
            configs[configName] = fileContents[key1][key2]
        except KeyError:
            log.warning(f"Configuração necessária \"{key1}\"/\"{key2}\" ausente do arquivo de configurações")
    else:
        try:
            configs[configName] = fileContents[key1]
        except KeyError:
            if key1 in criticalConfig:
                log.critical(f"Configuração crítica \"{key1}\" ausente do arquivo de configurações")
                print(f"Configuração crítica \"{key1}\" ausente do arquivo de configurações!\nEncerrando execução!")
                sys.exit()
                
            log.warning(f"Configuração necessária \"{key1}\" ausente do arquivo de configurações")
                
    

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
        Define os nomes das configurações como serão buscadas no servidor
        Procura pelas configurações correspondentes no arquivo de configurações
        """
        
        # Validando nome do arquivo de configuração
        if cfgName is None:
            cfgName = "config.toml"
        
        self.configValue = dict()
        
        keys   = [
            "implemmentedMethods", "httpVersion", "port", "host", "serverName", "contentRoot",
            "forbiddenPaths", "forbiddenFiles", "allowedPaths", "allowedFiles"
        ]
        values = [
            "implemented_methods", "http_version", "port", "host", "server_name", "content_root",
            ("Forbidden", "paths"), ("Forbidden", "files"), ("Allowed", "paths"), ("Allowed", "files")
        ]
        
        # Abrindo o arquivo e recuperando as configurações
        with open(cfgName, mode="rb") as cfgFP:
            rawConfig = tomllib.load(cfgFP)
            
            # Recuperando Configurações
            for key, value in zip(keys, values):
                if type(value) is tuple:
                    load_data(self.configValue, key, rawConfig, value[0], value[1])
                else:
                    load_data(self.configValue, key, rawConfig, value)
                