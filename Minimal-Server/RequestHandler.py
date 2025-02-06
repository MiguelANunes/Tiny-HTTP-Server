import logging              # Biblioteca de criação de logs
from typing import Optional # Anotações de tipo
import Exceptions
# from Configuration import serverConfigValues # Configurações do Servidor

"""
Arquivo onde é definida a classe de requisições HTTP
TODO: Melhorar essa descrição
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
        TODO: Métodos para processar os cabeçalhos e métodos para processar o corpo
    """
    
    # Uma requisição HTTP tem três componentes
        # A primeira linha, cujo formato é
            # <METODO> <CAMINHO-RECURSO> <VERSÃO-PROTOCOLO>
        # Uma lista de cabeçalhos
        # Um corpo (opcional)
    def __init__(self, firstLine:str, headers:str, body:Optional[str], serverConfigValues) -> None:
        # Não lidarei com requisições que tem corpo aqui, então só copio para o objeto e é isso
        self.body = body
        
        # Recuperando as informações da primeira linha
        # A primeira linha da requisição sempre terá 3 componentes, separados por espaços
        # Portanto é seguro fazer essa operação
        # De qualquer forma, irei fazer uma validação no input
        try:
            self.method, self.path, self.version = firstLine.split() # Aqui estou assumindo que o whitespace no final da primeira linha já foi removido
        except ValueError:
            log.error(f"Erro ao interpretar primeira linha da requisição:\n{firstLine}")
            raise Exceptions.BadRequest("Requisição Mal Formada!" ,firstLine)

        # Verificando se o método utilizado é suportado
        if self.method not in serverConfigValues.implemmentedMethods:
            log.error(f"Erro, método requisitado não foi implementado:\n{self.method}")
            raise Exceptions.MethodNotImplemented("Método Não Implementado!", self.method)

        # Verificando se o caminho requisitado é válido
        # TODO: Fazer nova validação aqui para garantir que está requisitando um caminho que existe
        for path in serverConfigValues.forbiddenPaths:
            if path in self.path:
                log.error(f"Erro, requisitando recurso proibido:\n{self.path}")
                raise Exceptions.Forbidden("Recurso Proibido de ser Acessado!", self.path)

        for fileExt in serverConfigValues.forbiddenFiles:
            if self.path.endswith(fileExt):
                log.error(f"Erro, requisitando recurso proibido:\n{self.path}")
                raise Exceptions.Forbidden("Recurso Proibido de ser Acessado!", self.path)

        # Verificando se a versão do HTTP passada na requisição é válida
        if self.version != serverConfigValues.httpVersion:
            log.error(f"Erro, versão do protocolo HTTP não suportada:\n{self.version}")
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
                log.error(f"Erro ao interpretar cabeçalho:\n{header}")
                raise Exceptions.BadRequest("Requisição Mal Formatada!", header)
            
            self.headers[k] = v
    
    def __str__(self) -> str:
        """
        Método que retorna uma versão legível por humanos da requisição já processada
        """
        
        ret = self.method + " " + self.path + " " + self.version + "\n"
        
        for header, value in self.headers.items():
            ret += f"{header}: {value}\n"
        
        if self.body is not None:
            ret += self.body
        
        return ret