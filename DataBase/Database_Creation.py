# pip install mysql-connector-python

import pandas as pd
import numpy as np
import pymysql.cursors
import requests
import config


# ## Reading Data

url = "https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Data/IBGE_cidades.csv"
df_Charts_Cities = pd.read_csv(url, index_col=False, delimiter = ',')
df_Charts_Cities.rename(columns={"Track_id": "Song_id"}, inplace= True)
df_Charts_Cities.rename(columns={"City": "Chart"}, inplace= True)

df_Charts_Cities["ID_Chart"] = df_Charts_Cities.Chart.str.lower().str.replace(" ", "_").str.replace("local_pulse", "lp")
df_Charts_Cities["ID_Chart"] = df_Charts_Cities.ID_Chart.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode("utf-8")

df_Charts_Cities["Type"]= np.where(df_Charts_Cities['Chart'].str.contains('Local Pulse'), "Local Pulse", "Normal")
df_Charts_Cities["Cidade"] = df_Charts_Cities.Chart.str.replace("Local Pulse ", "")

url = "https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Data/data_songs.csv"
df_Songs = pd.read_csv(url, index_col=False, delimiter = ',')

url = "https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Data/dados_spotify_cidades.csv"
df_Cities = pd.read_csv(url, index_col=False, delimiter = ',')

df_Charts_Songs = pd.merge(df_Charts_Cities, df_Songs, on = 'Song_id')
df_Charts_Songs = pd.merge(df_Charts_Songs, df_Cities, on = 'Cidade')


# ## Creating Dataframes

# Chart Table
df_table_chart = df_Charts_Songs[['ID_Chart', 'Código_Cidade', 'Type']].drop_duplicates().reset_index(drop = True)

df_table_chart.rename(columns={"ID_Chart": "ID",
                               "Type": "Tipo"}, inplace= True)

# Cities Table
df_table_cities = df_Cities[['Código_Cidade', 'Cidade', 'Estado']]


# States Table
df_table_states = df_Cities[['Estado', 'Regiao']].drop_duplicates().reset_index(drop = True)


# Chart songs Table
df_table_chart_songs = df_Charts_Songs[['ID_Chart', 'Date', 'Song_id', 'Position']].reset_index(drop = True)
df_table_chart_songs.rename(columns={"ID_Chart": "ID_Ranking",
                               "Date": "Data",
                               "Song_id": "ID_Musica",
                               "Position": "Posição",}, inplace= True)


## Album Songs Table
df_table_songs = df_Charts_Songs[['Song_id', 'Album_id', 'Song_Name', 'Song_Explicit', 'Song_popularity',
                                       'Song_danceability','Song_energy', 'Song_loudness',
                                        'Song_valence', 'Song_track_number'
                                       ]].drop_duplicates().reset_index(drop = True)

df_table_songs.rename(columns={"Song_id": "ID",
                               "Album_id": "ID_Album",
                               "Song_Name": "Nome",
                               "Song_Explicit": "Explicita",
                               "Song_popularity": "Popularidade",
                               "Song_danceability": "Danceabilidade",
                               "Song_energy": "Energia",
                               "Song_loudness": "Volume",
                               "Song_valence": "Valencia",
                               "Song_track_number": "Faixa"}, inplace= True)


## Album Table
df_table_albums = df_Charts_Songs[['Album_id', 'Album_name', 'Album_release','Album_image']].drop_duplicates().reset_index(drop = True)
df_table_albums.rename(columns={"Album_id": "ID",
                               "Album_name": "Nome",
                               "Album_release": "Data",
                               "Album_image": "Imagem_capa"}, inplace= True)

## Artist Albums Table
df_table_artist_albums = df_Charts_Songs[['Artist_id', 'Album_id']].drop_duplicates().reset_index(drop = True)
df_table_artist_albums.rename(columns={"Album_id": "ID_Album",
                          "Artist_id": "ID_Artista"}, inplace= True)

## Artist Table
df_table_artists = df_Charts_Songs[['Artist_id', 'Artist_name', 'Artist_followers', 
                                    'Artist_popularity']].drop_duplicates('Artist_id').reset_index(drop = True)

df_table_artists.rename(columns={"Artist_id": "ID",
                               "Artist_name": "Nome",
                               "Artist_followers": "Seguidores",
                               "Artist_popularity": "Popularidade"}, inplace= True)

## Artist Genders

artist_genders = []
df_artistis_genders = df_Charts_Songs[['Artist_id', 'Artist_genres']].drop_duplicates().reset_index(drop = True)

for i in range(len(df_artistis_genders)):
    
    list_genders = df_Charts_Songs["Artist_genres"][i].replace("[", "").replace("]", "").replace("'", "").split(", ")
    
    
    for gender in list_genders:
        artist_genders.append((df_artistis_genders["Artist_id"][i], gender))
        
df_table_artist_genders = pd.DataFrame(artist_genders, columns=['Artist_id', 'Gender'])
df_table_artist_genders.rename(columns={"Artist_id": "ID_Artista",
                                    "Gender": "Genero",}, inplace= True)


# ## Creating DataBase
conn = pymysql.connect(
                host=config.DATABASE_HOST,
                port=config.DATABASE_PORT,
                user=config.DATABASE_USER,
                password=config.DATABASE_PASSWORD,
                database=config.DATABASE_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

cursor = conn.cursor()


# ## Creating Tables

database = config.DATABASE_NAME
cursor.execute("DROP DATABASE IF EXISTS {database};".format(database = database))
cursor.execute("CREATE DATABASE {database};".format(database = database))
print("Base de dados '{}' criada com sucesso.".format(database))

cursor.execute("USE {database};".format(database = database))


# #### Ranking Table

table = "Ranking"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}(ID varchar(255) NOT NULL PRIMARY KEY,
                                        Codigo_Cidade int NOT NULL,
                                        Tipo varchar(255) NOT NULL)""".format(table = table))
for i,row in df_table_chart.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()

print("Tabela '{}' criada com sucesso.".format(table))


# #### Artist Table

table = "Artista"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID VARCHAR(255) NOT NULL PRIMARY KEY,
                                        Nome VARCHAR(255) NOT NULL,
                                        Seguidores INT NOT NULL,
                                        Popularidade INT NOT NULL)""".format(table = table))

for i,row in df_table_artists.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()

print("Tabela '{}' criada com sucesso.".format(table))


# #### Album Table


table = "Album"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID VARCHAR(255) NOT NULL PRIMARY KEY,
                                        Nome VARCHAR(255) NOT NULL,   
                                        Data DATE,
                                        Imagem_capa MEDIUMBLOB NOT NULL)""".format(table = table))

remain = len(df_table_albums) - 1
for i,row in df_table_albums.iterrows():
    
    url = row[3]    
    img_bytes = requests.get(url).content
    data = row[0:3].tolist()
    data.append(img_bytes)
         
    try: 
        int(row[2])
        sql = "INSERT INTO {database}.{table} VALUES (%s,%s,NULL,%s)".format(database = database,table = table)
        data.remove(row[2])   
        cursor.execute(sql, tuple(data))
        
    except :
        sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s,%s)".format(database = database,table = table)
        cursor.execute(sql, tuple(data))    
    
    print("Criando a tabela {}. Linhas  %s restantes     ".format(table, remain), end = "\r", flush = True)
    remain -= 1
        
    conn.commit()

print("Tabela '{}' criada com sucesso.                ".format(table))


# #### Song Table


df_table_songs.Explicita = df_table_songs.Explicita.astype(int)

table = "Musica"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID VARCHAR(255) NOT NULL PRIMARY KEY,
                                        ID_Album VARCHAR(255) NOT NULL,
                                        Nome VARCHAR(255) NOT NULL,
                                        Faixa INT NOT NULL,
                                        Explicita TINYINT NOT NULL,
                                        Popularidade INT NOT NULL,
                                        Danceabilidade FLOAT(3) NOT NULL,
                                        Energia FLOAT(3) NOT NULL,
                                        Volume FLOAT(3) NOT NULL,
                                        Valencia FLOAT(3) NOT NULL,
                                        FOREIGN KEY (ID_Album) REFERENCES Album(ID))""".format(table = table))
for i,row in df_table_songs.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))


# #### City Table


table = "cidade"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID INT NOT NULL PRIMARY KEY,
                                        Nome VARCHAR(255) NOT NULL,
                                        Estado VARCHAR(255) NOT NULL)""".format(table = table))
for i,row in df_table_cities.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))


# #### State Table 

table = "Estado"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( Nome VARCHAR(255) NOT NULL,
                                        Regiao VARCHAR(255) NOT NULL)""".format(table = table))
for i,row in df_table_states.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))


# #### Gender Table

table = "Genero"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID_Artista VARCHAR(255) NOT NULL,
                                        Genero VARCHAR(255),
                                        FOREIGN KEY (ID_Artista) REFERENCES Artista(ID))""".format(table = table))

for i,row in df_table_artist_genders.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))


# #### Artist's Albums

table = "Artista_Albums"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID_Artista VARCHAR(255) NOT NULL,
                                        ID_Album VARCHAR(255) NOT NULL,
                                        FOREIGN KEY (ID_Artista) REFERENCES Artista(ID),
                                        FOREIGN KEY (ID_Album) REFERENCES Album(ID))""".format(table = table))

for i,row in df_table_artist_albums.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))


# #### Ranking's Songs


table = "Ranking_Musicas"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID_Ranking VARCHAR(255) NOT NULL,
                                        Data DATE NOT NULL,
                                        ID_Musica VARCHAR(255) NOT NULL,                                        
                                        Posicao INT NOT NULL,
                                        FOREIGN KEY (ID_Ranking) REFERENCES Ranking(ID),
                                        FOREIGN KEY (ID_Musica) REFERENCES Musica(ID))""".format(table = table))

remain = len(df_table_chart_songs) - 1
for i,row in df_table_chart_songs.iterrows():
    
    

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit() 

    
    print("Criando a tabela {}. Linhas  %s restantes     ".format(table, remain), end = "\r", flush = True)
    
    remain -= 1 

print("Tabela '{}' criada com sucesso.                          ".format(table))
print("Base de dados '{}' alimentada com sucesso.".format(database))

