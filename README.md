# Banco de dados e Aplicação Web Spotify

![GitHub repo size](https://img.shields.io/github/repo-size/leticiatavaresds/Banco-de-Dados-Spotify?color=a21360&style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/leticiatavaresds/Banco-de-Dados-Spotify?color=a21360&style=for-the-badge)
![Made With](https://img.shields.io/badge/Made%20With-Python;%20HTML;%20CSS-lightgrey?color=a21360&style=for-the-badge)
![GitHub repo file count](https://img.shields.io/github/directory-file-count/leticiatavaresds/Banco-de-Dados-Spotify?color=a21360&style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/leticiatavaresds/Banco-de-Dados-Spotify?color=a21360&style=for-the-badge)

## Índice

- [Introdução](#introdução)
- [Dados](#dados)
  - [Obtenção dos Dados](#obtenção-dos-dados)
  - [Cruzamento dos dados](#cruzamento-dos-dados)
- [Modelagem](#modelagem)
  - [Modelagem Conceitual](#modelagem-conceitual)
  - [Modelagem Relacional](#modelagem-relacional)
- [Banco de Dados](#banco-de-dados)
- [Aplicação Web](#aplicação-web)
  - [Funcionalidades](#funcionalidades)
- [Execução](#execução)
- [Licença](#licença)

# Introdução

O escopo do projeto é dividido em três partes. Primeiramente, são capturados dados, via
scripts na linguagem python, do IBGE e das plataformas Spotify e Spotify Charts. Após
obtenção, tratamento e cruzamento dos dados, é então construído, em linguagem
MySQL, um banco de dados seguindo uma modelagem dimensional Entidade
Relacionamento. Por fim, é criado uma aplicação Web integrada ao banco utilizando as
linguagens ```Python```, ```MySQL```, ```HTML```, ```CSS``` e ```JavaScript```.

[⬆ Voltar ao topo](#banco-de-dados-e-aplicação-web-spotify)<br>

# Dados
Com o objetivo de construir um banco de dados com músicas presentes em rankings nacionais do Spotify, a primeira fonte foi o (Spotify Charts)[https://charts.spotify.com/home], um site feito por fãs que apresenta ranking de músicas mais tocadas no Spotify por região ou por gênero, no qual conseguimos dados dos rankings divididos por cidades do Brasil. Com isso, capturou-se microdados das músicas presentes nesses rankings utilizando como fonte API's fornecidas pela (Plataforma de Desenvolvimento do Spotify)[https://developer.spotify.com/]. Por fim, foram capturados, através de uma (API disponibilizada pelo IBGE)[https://servicodados.ibge.gov.br/api/docs/localidades], dados sobre a região de cada cidade que contém ranking para complementar as informações uti.

## Obtenção dos dados
Foi utilizado um Jupyter Notebook com linguagem Python com a biblioteca Selenium, realizando web scraping, para capturar dados do site Spotify Charts referentes a
rankings por semana de cada cidade brasileira presente no site, incluindo os identificadores do Spotify de cada música.
Com esses identificadores, a captação dos microdados das músicas na plataforma Spotify se dá também por Jupyter Notebook com linguagem Python que se
comunica com a plataforma via requests às APIs disponibilizadas, passando como parâmetro inicial os identificadores. Dessa fonte, conseguimos diversos atributos das
músicas, álbuns e artistas e, desses, foram selecionados os mais relevantes ao projeto para integrar a modelagem.
Os microdados do IBGE também foram obtidos da mesma forma que os do Spotify, via requests à API disponibilizada pelo instituto, capturando os microdados
apenas das cidades obtidas do Spotify Charts.

## Cruzamento dos dados
Com todos os dados capturados e salvos em arquivos .CSV, as tabelas são lidas por um Jupyter Notebook com linguagem Python, utilizando a biblioteca pandas, e o
cruzamento é feito. Assim, os dados dos rankings retirados do Spotify Charts são cruzados com os retirados do Spotify, através do ID da música. Por fim, cruza-se esse resultado com os dados do IBGE, onde a chave utilizada para o cruzamento é o nome da cidade presente nos dados do spotify charts.  Nesse último passo foi necessário também uma conferência manual, já que há cidades com nomes iguais.

[⬆ Voltar ao topo](#banco-de-dados-e-aplicação-web-spotify)<br>

# Modelagem
A partir do momento que os dados foram obtidos, entramos na fase da modelagem. Para isso, foi definido as entidades e depois as relações entre elas.

## Modelagem Conceitual

Considerando que a ideia envolvia a recomendação de músicas, a primeira e principal entidade modelada foi a de Música. A ela, então, foi atriuido um ID que
a identifica, depois o seu Nome, Duração e Popularidade e, então, as propriedades da música - Explícito, Volume, Dançabilidade, Energia e Valência - que são utilizados no cálculo de recomendação das músicas.

Com a Música criada, chegamos às tabelas de Álbum, com um identificador, nome, data e a imagem da capa; o Artista, com identificador, nome, número de seguidores,
popularidade e gêneros musicais e o Ranking, com identificador e a localidade, dividida em Cidade, Estado e Região.

No caso dos gêneros musicais do Artista, primeiro foi pensado modelar como um atributo multivalorado, para que a modelagem apresentasse um atributito desse tipo. Contudo, foi possível adquirir mais de uma imagem por artista e assim o atributo multivalorado Imagem para artista foi criado, o que possibilitou ao gênero ser uma nova entidade com cardinalidade (1,n), já que um gênero só está na nossa base se possui pelo menos um artista o apresenta. Já pensando na presença de um atributo composto, foi utlizado a localidade dos Rankings.

Depois que todas as entidades foram concluídas, foram formadas as relações entre elas. Assim, foi definida a relação Contém entre Ranking e Música, com
cardinalidade (1,n) em ambos os lados, pois cada ranking contém pelo menos uma música e nosso banco só contém dados de músicas que estão presentes em pelo menos
um ranking, e que possui os atributos Posição (posição da música no ranking) e Data (indicando em qual ranking, separado em semanas, encontra-se uma dada música).

Além disso, temos a relação Tem entre Álbum e Música, onde cada música está em um único álbum, enquanto álbuns podem possuir várias músicas; a relação possui o atributo Faixa, que indica qual a faixa que a música ocupa no álbum. Por fim, temos o  elacionamento Performa entre Álbum e Artista, que também possui cardinalidade (1,n) em ambos os lados, já que o álbum pode ser de um mais artistas e nosso banco só contém artista que está relacionado a pelo menos um álbum, podendo ter vários.

<img align="center" width="700" src="https://github.com/leticiatavaresds/Banco-de-Dados-Spotify/blob/main/Modelagem/Modelo%20Conceitual.png"/>


## Modelagem Relacional

Com a modelagem conceitual concluída, foi usada a função de conversão do brModelo para criar uma versão inicial e, a partir daí, foram tulizadas as regras de conversão para fazer quaisquer modificações necessárias. Neste passo, então, as relações Performa e Contém, além do atributo Gênero de Artista foram transformados em tabelas separadas, utilizando chaves estrangeiras para se relacionar com as entidades de origem. Enquanto isso, a relação Tem foi substituída pela adição, na tabela Música, de uma chave estrangeira para o ID de Álbum, além do atributo Faixa.

<img align="center" width="700" src="https://github.com/leticiatavaresds/Banco-de-Dados-Spotify/blob/main/Modelagem/Modelo%20L%C3%B3gico.png"/>


[⬆ Voltar ao topo](#banco-de-dados-e-aplicação-web-spotify)<br>

# Banco de Dados

Para a criação do banco de dados relacional deste trabalho foi utilizado o sistema de gerenciamento MySQL, que possui uma biblioteca para comunicação com Python. Para alimentar o banco de dados com as tabelas criadas pela modelagem relacional, foi utilizado o script “Database_Creation.py” em Python que utiliza a biblioteca “pymysql” para realizar a comunicação com o banco e a biblioteca pandas para ler os arquivos com os dados. Após tratamento dos dados (como, por exemplo, obter a imagem pelo link e depois convertê-la em binário, renomeação de atributos e exclusão de algumas colunas dispensadas), o banco é alimentado com os dataframes de cada tabela. 

A descrição de cada atributo selecionado para popular o banco de dados pode ser encontrada no (Dicionário de Dados)[https://github.com/leticiatavaresds/Banco-de-Dados-Spotify/blob/main/Data/Dicion%C3%A1rio%20Vari%C3%A1veis%20utilizadas.pdf].

[⬆ Voltar ao topo](#banco-de-dados-e-aplicação-web-spotify)<br>

# Aplicação Web

Por último, foi criada uma aplicação Web simples para que o usuário possa realizar consultas à base criada. A aplicação foi desenvolvida utilizando a linguagem Python e SQL com as bibliotecas Flask e MySQL para o backend e as linguagens HTML, CSS e JavaScript para o front. O intuito da aplicação é recomendar músicas com base na entrada que o usuário der, além de possibilitar que o usuário visualize os rankings das músicas mais ouvidas por cidade, estado ou região brasileira.

## Funcionalidades

A aplicação apresenta duas funcionalidades principais: a primeira é a recomendação de músicas, onde o usuário pode entrar com o nome completo ou parcial de um cantor, álbum, música ou cidade, sendo necessário escolher por qual parâmetro será realizada a recomendação, caso o termo buscado esteja presente na base na categoria selecionada no caso positivo, são retornadas vinte músicas que o algoritmo ingênuo considerou mais semelhantes, comparando as propriedades volume, dançabilidade, energia e valência.

Na funcionalidade de recomendação, caso a entrada seja uma música, a aplicação busca as propriedades da faixa dada e os passa para o algoritmo que calcula a
distância entre a música e todas as outras presentes na base, retornando as vinte com menor distância. Caso seja artista, álbum ou cidade, a aplicação busca por todas as faixas que apresentam o valor dado no tipo especificado, calcula a média de cada propriedade, para então passar essas médias como entrada para algoritmo. Então, se o usuário der um nome de um álbum por exemplo, primeiro serão resgatadas todas as músicas que pertencem ao álbum, depois é feito uma média das músicas para cada propriedade e essas médias que são passadas para o algoritmo que retornará as faixas  om menores distâncias. A busca por artista tem um diferencial em que pode-se entrar com um ou dois artistas separados por “;”. Nesse caso, primeiro junta-se todas as músicas pertencentes aos artistas dados para então calcular-se a média.

Há ainda a possibilidade de uma busca personalizada para recomendação, onde o usuário pode especificar através de uma entrada por slider qual o nível de volume,
dançabilidade, energia e valência que ele deseja nas músicas, onde a aplicação pega essas entradas, converte para parâmetros equivalentes às medidas das propriedades da música e os passa para o algoritmo. Sendo possível ainda nessa opção selecionar o critério das músicas não serem explícitas.

Já a segunda funcionalidade se resume em apresentar o ranking semanal das músicas mais populares por cidades brasileiras, estado ou região, sendo que o spotify,
atualmente, só fornece esse ranking para as cidades: Belo Horizonte, Belém, Brasília, Campinas, Campo Grande, Cuiabá, Curitiba, Florianópolis, Fortaleza, Goiânia, Manaus, Porto Alegre, Recife, Rio de Janeiro, Salvador, São Paulo e Uberlândia. Há ainda a opção de visualizar o ranking “Local Pulse”.

Para os rankings das cidades, a aplicação apenas busca as músicas e suas respectivas posições para o tipo de ranking escolhido na cidade e semana especificadas,
retornando suas informações incluindo a imagem da capa do álbum recuperada do banco de dados e um player fornecido pelo Spotify para se tocar um pedaço da música
ou ela completa caso o usuário esteja logado no serviço no mesmo navegador.

Já para estado e região, como o Spotify Charts não fornece o número de reproduções de cada músicas, apenas suas posições, a aplicação busca os rankings das
cidades pertencentes à localidade e faz um rankeamento personalizado, classificando de acordo com a quantidade de cidades em que a música entrou no ranking e as posições mais altas ocupadas nesses rankings para desempate.

Como a base de dados é bem pequena com relação ao número de músicas e o algoritmo para recomendação elaborado é bastante ingênuo, considerando ainda poucos
parâmetros e condições, as recomendações não são assertivas no momento, mas conseguimos elaborar as funcionalidades que idealizamos e a aplicação pode vir a ser
usada para futuras implementações e melhorias.

Abaixo se encontram alguns prints da aplicação.



<table>
  <tr>
    <td>Página Inicial:</td>
    <td>Página com uma Recomendação:</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Web%20Application/Prints/Pagina%20inicial.png" width=500></td>
    <td><img src="https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Web%20Application/Prints/Recomenda%C3%A7%C3%A3o.png" width=500>      </td>
  </tr>
  
  <tr>
    <td>Página com Ranking de uma Região:</td>
    <td>Opção Busca Personalizada:</td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Web%20Application/Prints/Ranking.png" width=500></td>
    <td><img src="https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Web%20Application/Prints/Busca%20Personalizada.png" width=500>      </td>
  </tr>
</table>


[⬆ Voltar ao topo](#banco-de-dados-e-aplicação-web-spotify)<br>

# Execução

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

[⬆ Voltar ao topo](#banco-de-dados-e-aplicação-web-spotify)<br>

# Licença

The MIT License (MIT) 2022 - Letícia Tavares. Leia o arquivo [LICENSE.md](https://github.com/leticiatavaresds/Banco-de-Dados-Spotify/blob/master/LICENSE.md) para mais detalhes.

[⬆ Voltar ao topo](#banco-de-dados-e-aplicação-web-spotify)<br>
