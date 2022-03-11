#!/usr/bin/env python
# coding: utf-8

# In[34]:


import pandas as pd
import numpy as np
import pymysql.cursors
import requests
import config


# ## Reading Data

# In[3]:


url = "https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Data/dados_spotify_cidades.csv"
df_Charts_Cities = pd.read_csv(url, index_col=False, delimiter = ',')
df_Charts_Cities.rename(columns={"Track_id": "Song_id"}, inplace= True)
df_Charts_Cities.rename(columns={"City": "Chart"}, inplace= True)

df_Charts_Cities["ID_Chart"] = df_Charts_Cities.Chart.str.lower().str.replace(" ", "_").str.replace("local_pulse", "lp")
df_Charts_Cities["ID_Chart"] = df_Charts_Cities.ID_Chart.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode("utf-8")

df_Charts_Cities["Type"]= np.where(df_Charts_Cities['Chart'].str.contains('Local Pulse'), "Local Pulse", "Normal")
df_Charts_Cities["Cidade"] = df_Charts_Cities.Chart.str.replace("Local Pulse ", "")

url = "https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Data/data_songs.csv"
df_Songs = pd.read_csv(url, index_col=False, delimiter = ',')


url = "https://raw.githubusercontent.com/leticiatavaresds/Banco-de-Dados-Spotify/main/Data/IBGE_cidades.csv"
df_Cities = pd.read_csv(url, index_col=False, delimiter = ',')

df_Charts_Songs = pd.merge(df_Charts_Cities,df_Songs, on = 'Song_id')
df_Charts_Songs = pd.merge(df_Charts_Songs,df_Cities[["Cidade", "Código_Cidade"]], on = 'Cidade')


# ## Creating Dataframes

# In[4]:


# Chart Table
df_table_chart = df_Charts_Songs[['ID_Chart', 'Código_Cidade', 'Type']].drop_duplicates().reset_index(drop = True)
df_table_chart.rename(columns={"ID_Chart": "ID",
                               "Type": "Tipo"}, inplace= True)

df_table_chart.head(3)


# In[5]:


# Cities Table
df_table_cities = df_Cities[['Código_Cidade', 'Cidade', 'Estado']]
df_table_cities.head(4)


# In[6]:


# States Table
df_table_states = df_Cities[['Estado', 'Regiao']].drop_duplicates().reset_index(drop = True)
df_table_states.head(4)


# In[7]:


# Chart songs Table
df_table_chart_songs = df_Charts_Songs[['ID_Chart', 'Date', 'Song_id', 'Position']].reset_index(drop = True)
df_table_chart_songs.rename(columns={"ID_Chart": "ID_Ranking",
                               "Date": "Data",
                               "Song_id": "ID_Musica",
                               "Position": "Posição",}, inplace= True)
df_table_chart_songs.head(3)


# In[8]:


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

df_table_songs.head(4)


# In[9]:


## Album Table
df_table_albums = df_Charts_Songs[['Album_id', 'Album_name', 'Album_release','Album_image']].drop_duplicates().reset_index(drop = True)
df_table_albums.rename(columns={"Album_id": "ID",
                               "Album_name": "Nome",
                               "Album_release": "Data",
                               "Album_image": "Imagem_capa"}, inplace= True)
df_table_albums.head(4)


# In[10]:


## Artist Albums Table
df_table_artist_albums = df_Charts_Songs[['Artist_id', 'Album_id']].drop_duplicates().reset_index(drop = True)
df_table_artist_albums.rename(columns={"Album_id": "ID_Album",
                          "Artist_id": "ID_Artista"}, inplace= True)
df_table_artist_albums.head(4)


# In[11]:


## Artist Table
df_table_artists = df_Charts_Songs[['Artist_id', 'Artist_name', 'Artist_followers', 
                                    'Artist_popularity']].drop_duplicates("Artist_id").reset_index(drop = True)

df_table_artists.rename(columns={"Artist_id": "ID",
                               "Artist_name": "Nome",
                               "Artist_followers": "Seguidores",
                               "Artist_popularity": "Popularidade"}, inplace= True)
df_table_artists.head(4)


# In[12]:


## Artist Images

artist_images = []
df_artistis_images = df_Charts_Songs[['Artist_id', 'Artist_images']].drop_duplicates().reset_index(drop = True)

for i in range(len(df_artistis_images)):
    
    list_images = df_Charts_Songs["Artist_images"][i].replace("(", "").replace(")", "").replace("'", "").split(", ")
    
    
    for image in list_images:
        artist_images.append((df_artistis_images["Artist_id"][i], image))
        
df_table_artist_images = pd.DataFrame(artist_images, columns=['Artist_id', 'Image'])
df_table_artist_images.rename(columns={"Artist_id": "ID_Artista",
                                    "Image": "Imagem",}, inplace= True)
df_table_artist_images.head(4)


# In[13]:


## Genders

artist_genders = []
df_artistis_genders = df_Charts_Songs[['Artist_id', 'Artist_genres']].drop_duplicates().reset_index(drop = True)

for i in range(len(df_artistis_genders)):
    
    list_genders = df_Charts_Songs["Artist_genres"][i].replace("[", "").replace("]", "").replace("'", "").split(", ")
    
    
    for gender in list_genders:
        artist_genders.append((gender.replace(" ","_"), gender.title()))
        
df_table_genders = pd.DataFrame(artist_genders, columns=['Gender_id', 'Gender'])
df_table_genders.rename(columns={"Gender_id": "ID_Genero",
                                    "Gender": "Genero",}, inplace= True)

df_table_genders = df_table_genders.drop_duplicates().reset_index(drop = True)
df_table_genders.head(4)


# In[14]:


## Artist Genders

artist_genders = []
df_artistis_genders = df_Charts_Songs[['Artist_id', 'Artist_genres']].drop_duplicates().reset_index(drop = True)

for i in range(len(df_artistis_genders)):
    
    list_genders = df_Charts_Songs["Artist_genres"][i].replace("[", "").replace("]", "").replace("'", "").split(", ")
    
    
    for gender in list_genders:
        artist_genders.append((df_artistis_genders["Artist_id"][i], gender.replace(" ","_")))
        
df_table_artist_genders = pd.DataFrame(artist_genders, columns=['Artist_id', 'Gender_id']).drop_duplicates().reset_index(drop = True)
df_table_artist_genders.rename(columns={"Artist_id": "ID_Artista",
                                    "Gender": "Genero",}, inplace= True)
df_table_artist_genders.head(4)


# ## Creating DataBase

# In[15]:


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


# In[16]:


database = config.DATABASE_NAME


# In[17]:


cursor = conn.cursor()


# ## Creating Tables

# In[18]:


cursor.execute("DROP DATABASE IF EXISTS {database};".format(database = database))
cursor.execute("CREATE DATABASE {database};".format(database = database))
print("Base de dados '{}' criada com sucesso.".format(database))
cursor.execute("USE {database};".format(database = database))


# #### Ranking Table

# In[19]:


table = "Ranking"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}(ID varchar(255) NOT NULL,
                                        Codigo_Cidade int NOT NULL,
                                        Tipo varchar(255) NOT NULL,
                                        PRIMARY KEY (ID, Codigo_Cidade))""".format(table = table))
for i,row in df_table_chart.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))
    


# #### Artist Table

# In[20]:


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

# In[21]:


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
    
    print("Criando a tabela {}. Linhas  {} restantes     ".format(table, remain), end = "\r", flush = True)
    remain -= 1
        
    conn.commit()
print("Tabela '{}' criada com sucesso.                ".format(table))


# #### Song Table

# In[22]:


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

# In[23]:


table = "cidade"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID INT NOT NULL,
                                        Nome VARCHAR(255) NOT NULL,
                                        Estado VARCHAR(255) NOT NULL,
                                        PRIMARY KEY (ID, Estado))""".format(table = table))
for i,row in df_table_cities.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))


# #### State Table

# In[24]:


table = "Estado"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( Nome VARCHAR(255) NOT NULL PRIMARY KEY,
                                        Regiao VARCHAR(255) NOT NULL)""".format(table = table))
for i,row in df_table_states.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()    
    
    
print("Tabela '{}' criada com sucesso.".format(table))


# #### Images Table 

# In[25]:


table = "Artista_Imagens"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID_Artista VARCHAR(255) NOT NULL,
                                        Imagem VARCHAR(255) NOT NULL,
                                        FOREIGN KEY (ID_Artista) REFERENCES Artista(ID),
                                        PRIMARY KEY (ID_Artista, Imagem))""".format(table = table))

remain = len(df_table_albums) - 1
for i,row in df_table_artist_images.iterrows():
    
#     url = row[1]    
#     img_bytes = requests.get(url).content
#     data = [row[0]]
#     data.append(img_bytes)

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
    remain -= 1
    
    
print("Tabela '{}' criada com sucesso.".format(table))


# #### Gender

# In[26]:


table = "Genero"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID VARCHAR(255) PRIMARY KEY,
                                        Genero VARCHAR(255) NOT NULL)""".format(table = table))

for i,row in df_table_genders.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))
    


# #### Artists Gender Table

# In[27]:


df_table_songs.Explicita = df_table_songs.Explicita.astype(int)

table = "Artista_Generos"

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID_Artista VARCHAR(255) NOT NULL,
                                        ID_Genero VARCHAR(255),
                                        FOREIGN KEY (ID_Artista) REFERENCES Artista(ID),
                                        FOREIGN KEY (ID_Genero) REFERENCES Genero(ID),
                                        PRIMARY KEY (ID_Artista, ID_Genero))""".format(table = table))

for i,row in df_table_artist_genders.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()


# #### Artist's Albums

# In[28]:


table = "Artista_Albums"
print("Criando a tabela '{}'...                 ".format(table), flush=True, end="\r")

cursor.execute('DROP TABLE IF EXISTS {table};'.format(table = table))

cursor.execute("""CREATE TABLE {table}( ID_Artista VARCHAR(255) NOT NULL,
                                        ID_Album VARCHAR(255) NOT NULL,
                                        FOREIGN KEY (ID_Artista) REFERENCES Artista(ID),
                                        FOREIGN KEY (ID_Album) REFERENCES Album(ID),
                                        PRIMARY KEY (ID_Artista, ID_Album))""".format(table = table))

for i,row in df_table_artist_albums.iterrows():

    sql = "INSERT INTO {database}.{table} VALUES (%s,%s)".format(database = database,table = table)
    cursor.execute(sql, tuple(row))
    conn.commit()
print("Tabela '{}' criada com sucesso.".format(table))


# #### Ranking's Songs

# In[29]:


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

    
    print("Criando a tabela {}. Linhas  {} restantes     ".format(table, remain), end = "\r", flush = True)    
    remain -= 1 
    
print("Tabela '{}' criada com sucesso.                          ".format(table))
print("Base de dados '{}' alimentada com sucesso.".format(database))

