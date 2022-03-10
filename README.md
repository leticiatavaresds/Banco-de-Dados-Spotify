# Trabalho_Final_BD_Spotify


É necessário ter o mysql instalado e executando, onde é recomendado [criar uma virtual-env em python](https://docs.python.org/pt-br/3/library/venv.html) para instalar 
o projeto para que não haja o risco de conflitos entre as bibliotecas. O projeto foi feito em python3 e caso não o tenha instalado, é necessário instalá-lo antes de seguir para os próximos passos.

Com o python instalado, deve-se instalar as bibliotecas utilizadas especificadas no documento "requirements.txt", a instalação pode ser feita por:
```sh
$ pip3 install -r requirements.txt
```
Após isso é necessário mudar as configurações do arquivo `config.yaml` para seu nome de usuário e senha do mysql. O usuário geralmente é "root".

OBS: Se você estiver usando um `host`ou uma porta diferente do padrão, apenas adicione junto com os outros campos um campo `host: "meu_novo_host"`e `port: XXXX`substituindo os valores pelos seus.


Com os parâmetros certos preenchidos, primeiro deve-se executar o arquivo py que cria o banco de dados em seu servidor. Para isso execute o arquivo com "Database_creation.py"
que pode ser executado rodando 
```sh
$ python Database_Creation.py
```
na pasta do arquivo.

Com a base criada, basta apenas rodar o projeto com:
```sh
$ python app.py
```
A aplicação ficará então disponível no endereço endicado no cmd.
