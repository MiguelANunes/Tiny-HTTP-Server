import logging # Biblioteca de criação de logs
import os      # Para acessar arquivos do sistema
from Configuration import ServerConfig # Configurações do Servidor

"""
Arquivo que vai lidar com todas as operações sobre arquivos presentes na pasta Content/

TODO: Caso esteja pegando algo que não é texto, tenho que abrir no modo de leitura de binário
"""

log = logging.getLogger("Main.Server.Response.Content")

def get_file_contents(filePath:str, serverConfigValues:ServerConfig) -> str:
    """
    Função que vai receber um caminho para um arquivo dentro da pasta Content/ e vai retornar o 
        conteúdo do arquivo desse arquivo em uma string
    
    Recebe:
        [str] filePath: Caminho para um arquivo na pasta Content/
    
    Retorna:
        String contendo o conteúdo do arquivo em filePath
    """
    
    log.info(f"Procurando o recurso {filePath}")
    
    # Caso tenha pedido a raiz do site (../Content/) retorno o arquivo index.html que está lá
    if filePath == "../Content/":
        filePath += "index.html"
    
    # Começo verificando se o caminho passado termina com algum formato aceito
    for fileExt in serverConfigValues.allowedFiles:
        if filePath.endswith(fileExt):
            # Se sim, leio esse arquivo e já retorno ele
            with open(filePath) as f:
                fileContents = f.read()
            return fileContents
    
    # Se não, procuro por arquivos aceitos na pasta atual
    dirContents = os.listdir(filePath)
    files       = []
    for item in dirContents:
        for fileExt in serverConfigValues.allowedFiles:
            if item.endswith(fileExt):
                files.append(item)
    
    if len(files) == 1:
        # Caso tenha apenas um arquivo recupero o conteúdo dele em uma string e retorno essa string
        with open(filePath+files[0]) as f:
            fileContents = f.read()
        return fileContents
    
    # Caso não tenha, testo se tem um index.html
    if "index.html" in files:
        # Se sim, abro ele
        with open(filePath+files[files.index("index.html")]) as f:
            fileContents = f.read()
        return fileContents
    
    # Caso não tenha um index.html, retorna o primeiro arquivo da lista
    with open(filePath+files[0]) as f:
        fileContents = f.read()
    return fileContents