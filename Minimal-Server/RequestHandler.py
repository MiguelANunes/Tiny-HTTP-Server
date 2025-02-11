import logging                         # Módulo de criação de logs
import Exceptions                      # Módulo de Execessões do Servidor
import os                              # Para verificar se o recurso requisitado existe
from typing import Optional            # Anotações de tipo
from Configuration import ServerConfig # Módulo de configurações do Servidor

"""
RequestHandler.py
Nesse módulo são definidas e processadas as requisições enviadas pelo cliente
O construtor da classe recebe os componentes da requisião em formato string e verifica se a requisição é válida
Não verifico se o arquivo requisitado
"""

log = logging.getLogger("Main.Server.Request")

class Request:
    
    """
    Classe que representa uma requisição HTTP
    No seu construtor recebe os componentes da requisição -- primeira linha, cabeçalhos e corpo -- como strings
    No caso do cabeçalho, uma string que pode conter várias substrings, cada uma delimitada por "\r\n" ou "\n"
    
    O construtor dessa classe processa essas strings para obter as informações necessárias para responder a requisição,
        levantando exceções quando necessário
        
    Atributos da Classe:
        [str]            method:  O método HTTP na requisição
        [str]            path:    Caminho do recurso requisitado
        [str]            version: A versão do protocolo HTTP da requisição
        [dict(str, str)] headers: Os cabeçalhos presentes na requisição
        [str]            body:    O corpo da requisição
        
    Métodos da Classe:
        __init__: Construtor da classe
        __str__: Retorna uma versão legível por humanos de um objeto dessa classe
    """
    
    # Uma requisição HTTP tem três componentes
        # A primeira linha, cujo formato é
            # <METODO> <CAMINHO-RECURSO> <VERSÃO-PROTOCOLO>
        # Uma lista de cabeçalhos
        # Um corpo (opcional)
    def __init__(self, firstLine:str, headers:str, body:Optional[str], serverConfig: ServerConfig, id:int) -> None:
        # Não lidarei com requisições que tem corpo aqui, então só copio para o objeto e é isso
        self.body = body
        
        # Identificando a requisição
        self.id = id
        
        # Recuperando as informações da primeira linha
        # A primeira linha da requisição sempre terá 3 componentes, separados por espaços
        # Portanto é seguro fazer essa operação
        # De qualquer forma, irei fazer uma validação no input
        try:
            self.method, self.path, self.version = firstLine.split() # Aqui estou assumindo que o whitespace no final da primeira linha já foi removido
        except ValueError:
            log.error(f"Erro ao interpretar primeira linha da requisição:{firstLine}")
            raise Exceptions.BadRequest("Requisição Mal Formada!" ,firstLine)

        # Verificando se o método utilizado é suportado
        if self.method not in serverConfig.configValue["implemmentedMethods"]:
            log.error(f"Erro, método requisitado não foi implementado:{self.method}")
            raise Exceptions.MethodNotImplemented("Método Não Implementado!", self.method)

        # Verificando se o recurso requisitado não é proibido
        for path in serverConfig.configValue["forbiddenPaths"]:
            if path in self.path:
                log.error(f"Erro, requisitando recurso proibido:{self.path}")
                raise Exceptions.Forbidden("Recurso Proibido de ser Acessado!", self.path)
        
        # Verificando se o recurso requisitado é permitido
        for path in serverConfig.configValue["allowedPaths"]:
            if path not in serverConfig.configValue["contentRoot"] + self.path:
                log.error(f"Erro, requisitando recurso que não está na lista de recursos permitidos:{serverConfig.configValue['contentRoot'] + self.path}")
                raise Exceptions.Forbidden("Requisitando Recurso não Permitido!", serverConfig.configValue['contentRoot'] + self.path)
        
        # Verificando se o recurso requisitado não é de um tipo proibido
        for fileExt in serverConfig.configValue["forbiddenFiles"]:
            if self.path.endswith(fileExt):
                log.error(f"Erro, requisitando recurso proibido:{self.path}")
                raise Exceptions.Forbidden("Recurso Proibido de ser Acessado!", self.path)

        # Verificando se o tipo de recurso requisitado é permitido
        for fileExt in serverConfig.configValue["allowedFiles"]:
            if not self.path.endswith(fileExt):
                log.error(f"Erro, requisitando recurso que não está na lista de recursos permitidos:{self.path}")
                raise Exceptions.Forbidden("Requisitando Recurso não Permitido!", self.path)

        # Verificando se o recurso requisitado existe
        if not os.path.exists(serverConfig.configValue['contentRoot'] + self.path):
            log.error(f"Erro, requisitando recurso que não existe:{serverConfig.configValue['contentRoot'] + self.path}")
            raise Exceptions.Forbidden("Recurso Proibido de ser Acessado!", self.path)

        # Verificando se a versão do HTTP passada na requisição é válida
        if self.version != serverConfig.configValue["httpVersion"]:
            log.error(f"Erro, versão do protocolo HTTP não suportada:{self.version}")
            raise Exceptions.VersionNotSupported("Versão do Protocolo HTTP Não Suportada", self.version)

        # Recuperando os headers da requisição
        # Os headers tem formato "header: value"
        # Cada header está em uma única linha
        # Portanto, basta iterar pelas linhas da string recebida no construtor e colocar cada par em um dict
        self.headers = dict()
        for header in headers.splitlines():
            if header == "": # Isso me deu muita dor de cabeça
                continue
            try:
                k, v = header.split(":", 1) # Separando a string em cada ":" e apenas uma vez, para evitar que argumentos que tenha ":" sejam separados tbm
            except ValueError:
                # sanity
                log.error(f"Erro ao interpretar cabeçalho:{header}")
                raise Exceptions.BadRequest("Requisição Mal Formatada!", header)
            
            self.headers[k] = v
    
    def __str__(self) -> str:
        ret = self.method + " " + self.path + " " + self.version + "\n"
        
        for header, value in self.headers.items():
            ret += f"{header}: {value}\n"
        
        if self.body is not None:
            ret += self.body
        
        ret += f"ID: {self.id}\n"
        
        return ret