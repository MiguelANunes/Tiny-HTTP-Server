"""
Arquivo que define exceções específicas sobre o protocolo HTTP

Essas exceções específicas servem para melhor lidar com erros encontrados durante o processamento de requisições
Caso um erro ocorra durante o processamento de uma requisição, uma dessas exceções será lançada
Ao ser tratada, uma resposta de erro correspondente a exceção lançada será enviada ao cliente
"""

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
    
    def __init__(self, message:str, badComp:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        self.badComp   = badComp # O componente específico que estava errado
        
class Forbidden(HTTPException): # 403
    """
    Exceção que é lançada quando a requisição feita pelo cliente contém um recurso proibido de ser acessado
    """
    
    def __init__(self, message:str, requestedPath:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        self.requestedPath = requestedPath # O caminho que o cliente pediu

class NotFound(HTTPException): # 404
    """
    Exceção que é lançada quando a requisição feita pelo cliente contém um recurso não encontrado
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
        
class InternalError(HTTPException): # 500
    """
    Exceção que é lançada quando ocorre um erro no servidor
    """
    
    def __init__(self, message:str, method:str) -> None:
        super().__init__(message) # Mensagem da exceção
        
        self.method = method # Método não suportado que foi enviado na requisição
        
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