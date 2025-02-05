from enum import Enum

"""
Arquivo que define exceções específicas sobre o protocolo HTTP

TODO: Melhorar essa descrição
TODO: Talvez seria uma boa ideia deixar os enumeradores em outro arquivo
"""

class ProblemComponent(Enum):
    """
    Enumerador que indica qual componente da mensagem causou um erro
    """
    METHOD = 1
    HEADER = 2
    BODY   = 3

class ImplementedMethods(Enum):
    """
    Enumerador que lista métodos que são implementados por esse servidorzinho
    Para processar novos métodos, basta adicionar eles nesse enum (e implementar o suporte)
    """
    GET     = "GET"
    HEAD    = "HEAD"
    OPTIONS = "OPTIONS"

    def __str__(self) -> str:
        return self.value

class HTTPVersion(Enum):
    """
    Enumerador que lista quais versões do HTTP são aceitas por esse servidorzinho
    """
    oneDotOne = "HTTP/1.1"

    def __str__(self) -> str:
        return self.value

class ForbiddenPaths(Enum):
    """
    Enumerador que lista caminhos proibidos de serem acessados por uma requisição
    """
    up         = ".."
    home       = "~"
    doubleDash = "//"

    def __str__(self) -> str:
        return self.value

class HTTPException(Exception):
    """
    Exceção base que é herdada por todas as exceções referentes ao HTTP
    Serve para separar as exceções do HTTP das exceções normais do Python
    """
    
    def __init__(self, message:str) -> None:
        super().__init__(message)
    

class BadRequest(HTTPException): # 400
    """
    Exceção que é lançada quando a requisição feita pelo cliente é mal formada ou não pode ser processada de alguma forma
    """
    
    def __init__(self, message:str, comp:ProblemComponent, badComp:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        self.component = comp    # Qual dos componentes que deu erro
        self.badComp   = badComp # O componente específico que estava errado
        
class Forbidden(HTTPException): # 403
    """
    Exceção que é lançada quando a requisição feita pelo cliente contém um caminho proibido de ser acessado
    """
    
    def __init__(self, message:str, requestedPath:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        self.requestedPath = requestedPath # O caminho que o cliente pediu
        
class ImTeapot(HTTPException): # 418
    """
    Exceção que é lançada quando não quero lidar com a requisição do cliente
    """
    
    def __init__(self, message:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        
class MethodNotImplemented(HTTPException): # 501
    """
    Exceção que é lançada quando a requisição possui um método não permitido por esse servidor
    """
    
    def __init__(self, message:str, method:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        self.method = method # Método não suportado que foi enviado na requisição
        
class VersionNotSupported(HTTPException): # 505
    """
    Exceção que é lançada quando a requisição pede uma versão HTTP que não é suportada
    """
    
    def __init__(self, message:str, version:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        self.version = version # Versão não suportada que foi enviado na requisição