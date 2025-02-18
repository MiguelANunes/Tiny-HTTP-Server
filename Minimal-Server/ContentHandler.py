import logging                         # Biblioteca de criação de logs
import os                              # Para acessar arquivos do sistema
import gzip                            # Para compactar arquivos binários sendo transferidos
from Configuration import ServerConfig # Configurações do Servidor
from typing import Union               # Anotações de Tipo

"""
ContentHandler.py
Módulo que vai recuperar o conteúdo requisitado pelo cliente
Todo o conteúdo disponível para ser requisitado estará dentro da pasta definida no arquivo de configurações como raiz dos conteúdos
Apesar de verificar no módulo RequestHandler se os recursos requisitados existem, faço essas verificações aqui novamente por garantia
Recursos que são retornados ao cliente são de dois tipo, texto ou binário
Recursos de tipo texto são retornados dentro de uma string
Recursos de tipo binário são retornados dentro de um tipo bytes
Para determinar se um arquivo é texto ou binário, verifico qual é sua extensão
"""

log = logging.getLogger("Main.Server.Response.Content")

# Função anônima que verifica se um arquivo é um arquivo texto, se não for é um binário
isTextFile = lambda f: any([f.endswith(ext) for ext in [".html", ".css", ".scss", ".js", ".txt", ".json", ".csv", ".xml"]])

def get_directory_content(path:str, serverConfig:ServerConfig) -> list[str]:
    """
    Função que vai abrir a pasta indicada pelo caminho path e retornar todos os arquivos dentro dela
    Caso a pasta não seja encontrada, lança uma exceção para ser tratada na função que chamou essa
    
    Recebe:
        [str] filePath: Caminho para um arquivo na pasta Content/
        [ServerConfig] serverConfig: Configurações do servidor
    
    Retorna:
        Uma lista possívelmente vazia de strings com nomes de arquivos nessa pasta
    """

    # Arquivos da pasta
    files: list[str] = []

    # Se chamou essa função, estou supondo que o caminho passado não indica um arquivo e sim uma pasta
    # Mais ainda, vou supor que o caminho inclui a raiz da pasta de conteúdo
    # Logo, não farei validações além do try-except
    try:
        dirContents = os.listdir(path)
        for item in dirContents:
            for fileExt in serverConfig.configValue["allowedFiles"]:
                if item.endswith(fileExt):
                    files.append(item)
    except (OSError, FileNotFoundError) as err:
        # Não vou lidar com erros aqui, vou delegar isso para a função chamadora
        raise err

    if len(files) == 0:
        # Caso não tenha achado nenhum arquivo, jogo uma exceção
        raise FileNotFoundError

    return files

def get_binary_file_contents(filePath:str) -> bytes:
    """
    Função que vai receber um caminho para um arquivo dentro da pasta Content/ e vai retornar o 
        conteúdo desse arquivo em binário
    """

    try:
        with open(filePath, "rb") as fp:
            fileContents = gzip.compress(fp.read())
        return fileContents
    except (OSError, FileNotFoundError) as err:
        # Não vou lidar com erros aqui, vou delegar isso para a função chamadora
        raise err

def get_text_file_contents(filePath:str) -> str:
    """
    Função que vai receber um caminho para um arquivo dentro da pasta Content/ e vai retornar o 
        conteúdo desse arquivo em uma string
    """
    try:
        with open(filePath) as fp:
            fileContents = fp.read()
        return fileContents
    except(OSError, FileNotFoundError) as err:
        # Não vou lidar com erros aqui, vou delegar isso para a função chamadora
        raise err

def get_file_contents(filePath:str) -> Union[str, bytes]:
    """
    Função que vai receber um caminho para um arquivo dentro da pasta Content/ e vai retornar o 
        conteúdo desse arquivo: 
            Em uma string caso seja um arquivo texto
            Em bytes caso ele seja um arquivo binário
    Essa função deve ser usada apenas para recuperar arquivos são arquivos texto
    
    Recebe:
        [str] filePath: Caminho para um arquivo na pasta Content/
    
    Retorna:
        String com o conteúdo do arquivo em filePath
        OU
        Bytes com o conteúdo do arquivo em filePath
    """
    
    # Se chamou essa função, estou supondo que filePath é um caminho válido para um arquivo
    # Mais ainda, vou supor que o caminho inclui a raiz da pasta de conteúdo
    # Logo, não farei validações (além do try-except dentro das funções)
    
    if isTextFile(filePath):
        log.info(f"Procurando arquivo texto {filePath}")
        return get_text_file_contents(filePath)
    else:
        log.info(f"Procurando arquivo binário {filePath}")
        return get_binary_file_contents(filePath)

def get_sizeof_resource(resourcePath:str, serverConfig:ServerConfig) -> int:
    """
    Função que vai receber um caminho para um recurso dentro da pasta Content/ e vai retornar o 
        tamanho desse recurso
    Nessa função assumo que já foi verificado se o recurso pode ser acessado
    
    Recebe:
        [str] resourcePath: Caminho para um arquivo na pasta Content/
        [ServerConfig] serverConfig: Dados de configuração do servidor
    
    Retorna:
        Int indicando o tamanho do recurso em bytes
    """
    
    # TODO: Aqui só copiei a função get_resource abaixo, pensar se tem uma maneira melhor de fazer isso
    
    # Primeiro verifico se o caminho é uma pasta
    if not resourcePath.endswith("/"):
        # Se não, pego o tamanho desse arquivo
        return os.path.getsize(resourcePath)
    
    # Se sim, recupero os conteúdos dessa pasta numa lista
    try:
        files = get_directory_content(resourcePath, serverConfig)
    except (OSError, FileNotFoundError) as err:
        raise err
    
    if len(files) == 1:
        # Caso tenha apenas um arquivo retorno o tamanho dele
        return os.path.getsize(files[0])
    
    for file in files:
        # Caso tenha múltiplos arquivos, verifico se tem um arquivo chamado "index.html" e retorno seu tamanho
        if "index.html" in file:
            return os.path.getsize(files[files.index("index.html")])
    
    # Caso não tenha um index.html, retorna o tamanho do primeiro arquivo da lista
    log.warning(f"A pasta {resourcePath} contém múltiplos arquivos, nenhum dos quais se chama index.html, estou recuperando o primeiro arquivo encontrado.")
    return os.path.getsize(files[0])

def get_resource(resourcePath:str, serverConfig:ServerConfig) -> Union[str, bytes]:
    """
    Função que vai receber um caminho para um recurso dentro da pasta Content/ e vai retornar o 
        conteúdo desse recurso
    Nessa função assumo que já foi verificado se o recurso pode ser acessado
    
    Recebe:
        [str] resourcePath: Caminho para um arquivo na pasta Content/
        [ServerConfig] serverConfig: Dados de configuração do servidor
    
    Retorna:
        String contendo o conteúdo do arquivo em resourcePath
        OU
        Bytes contendo o conteúdo do arquivo binário em resourcePath
    """
    
    log.info(f"Procurando o recurso {resourcePath}")
    
    # Primeiro verifico se o caminho é uma pasta
    if not resourcePath.endswith("/"):
        # Se não, verifico que tipo de arquivo ele é e leio ele
        return get_file_contents(resourcePath)
    
    # Se sim, recupero os conteúdos dessa pasta numa lista
    try:
        files = get_directory_content(resourcePath, serverConfig)
    except (OSError, FileNotFoundError) as err:
        raise err
    
    if len(files) == 1:
        # Caso tenha apenas um arquivo recupero o conteúdo dele e retorno isso
        return get_file_contents(resourcePath + files[0])
    
    for file in files:
        # Caso tenha múltiplos arquivos, verifico se tem um arquivo chamado "index.html" e retorno seu conteúdo
        if "index.html" in file:
            return get_file_contents(resourcePath + files[files.index("index.html")])
    
    # Caso não tenha um index.html, retorna o primeiro arquivo da lista
    log.warning(f"A pasta {resourcePath} contém múltiplos arquivos, nenhum dos quais se chama index.html, estou recuperando o primeiro arquivo encontrado.")
    return get_file_contents(resourcePath + files[0])