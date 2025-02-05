# migs' HTTP Servers

Nesse repositório tenho a implementação de dois servidores HTTP simples.

O `Minimal-Server` é uma implementação minimal em Python, ou seja, ele irá suportar apenas os métodos GET e HEAD (os outros são processados porém retornam 405 Method Not Allowed) e consegue lidar com apenas uma conexão de cada vez.

O `Parallel-Server` é uma implementação em C++ que irá suportar pelo menos os mesmos métodos que o servidor minimal, porém irá lidar com conexões de forma paralela, permitindo multiplas conexões ao mesmo tempo.
