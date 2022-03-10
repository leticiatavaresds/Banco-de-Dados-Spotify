from urllib import response
import pymysql.cursors
import pandas as pd
import scipy.spatial
from flask import Flask, render_template, request
from base64 import b64encode
import config


connection = pymysql.connect(
    host=config.DATABASE_HOST,
    port=config.DATABASE_PORT,
    user=config.DATABASE_USER,
    password=config.DATABASE_PASSWORD,
    database=config.DATABASE_NAME,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
app = Flask(__name__,template_folder="templates")  

cidade = ""
tipo = ""
localidade = ""
db_cursor = connection.cursor()
db_cursor.execute('SELECT * FROM musica')
table_rows = db_cursor.fetchall()
df_table_songs = pd.DataFrame(table_rows)
ButtonPressed = 0    


@app.route("/", methods=['GET', 'POST'])

def musics( ):

    def recomendacao(explicita, gostos, top):

        global df_table_songs
        
        if explicita == "on":
            df_songs = df_table_songs[df_table_songs['Explicita'] == 0].reset_index(drop = True)
        else:
            df_songs = df_table_songs.copy()

        df_teste = df_songs[['Danceabilidade','Energia', 'Volume', 'Valencia']]

        df_gosto = pd.DataFrame(data = [gostos], columns = ['Danceabilidade','Energia', 'Volume', 'Valencia'])
        

        result = scipy.spatial.distance.cdist(df_teste, df_gosto, metric = "euclidean").sum(axis = 1).tolist()
        df_teste["Distance"] = result
        
        
        musicas = df_teste.sort_values(by = "Distance", ascending = True).head(top).index
        df_recomendations = df_songs[df_songs.index.isin(musicas)].reset_index(drop = True)
        Songs_IDs = df_recomendations.ID

        return Songs_IDs


    

    with connection.cursor() as cursor:

        cursor.execute('SELECT Nome FROM Cidade ORDER BY Nome ASC;') 
        cidades = cursor.fetchall()        

        cursor.execute('SELECT DISTINCT(Nome) FROM Estado ORDER BY Nome ASC;') 
        estados = cursor.fetchall() 

        cursor.execute('SELECT DISTINCT(Regiao) FROM Estado ORDER BY Regiao ASC;') 
        regioes = cursor.fetchall()  

        images = []
        sql = "SELECT * FROM musica WHERE ID = '' ;"
        cursor.execute(sql)        
        result = cursor.fetchall()

        if request.args.get("searchSpecial"):

            danceability = float(request.args["RangeDance"])
            energy = float(request.args["RangeEnergy"])
            loudness = float(request.args["RangeVocal"])
            valence = float(request.args["RangeHappy"])
            likely = [danceability, energy, loudness, valence]
                            
            try:
                explicit = request.args["CheckExplicit"]
            except:
                explicit = "off"
            
            ids = recomendacao(explicit, likely, 20)
            id_songs = "(" + ", ".join(["'" + id_song + "'" for id_song in ids]) + ")"

            sql = """
                SELECT musica.Nome AS MusicaNome, 
                        musica.ID AS ID, 
                        artista.Nome AS ArtistaNome,
                        Imagem_capa AS Imagem_capa                
                FROM musica 
                INNER JOIN album
                ON musica.ID_Album = album.ID     
                INNER JOIN artista_albums
                ON album.ID = artista_albums.ID_Album
                INNER JOIN artista
                ON artista_albums.ID_Artista = artista.ID                        
                WHERE musica.ID IN {id_songs}
                ORDER BY musica.Nome ASC
                """.format(id_songs = id_songs)

            cursor.execute(sql)        
            result_query = cursor.fetchall()
            
            result = []
            for id_song in (ids):
                result.append([song for song in result_query if song['ID'] == id_song][0])


            df_table_songs = pd.DataFrame(result, columns = ["Nome", "ID", "Popularidade", "Imagem_capa"])

            images = []
            for image in df_table_songs["Imagem_capa"].values:
                images.append(b64encode(image).decode("utf-8"))
            image = images[0]

            return render_template("musicas.html", musicas = result, search = request.args.get("search"),
                        cidades = cidades, images = images, estados = estados)


        if request.args.get("search"):


            search = request.args["search"].strip()  
            type = request.args["suggestion-options"]          
            
            
            if type == "artist":

                singers = search.split(";") 
                
                # 5 - Consulta com agragacao (AVG)

                if (len(singers) == 1):

                    sql = """
                        SELECT AVG(Danceabilidade), AVG(Energia), AVG(Valencia), AVG(Volume)                         
                        FROM musica
                        INNER JOIN album
                        ON musica.ID_Album = album.ID
                        INNER JOIN artista_albums
                        ON album.ID = artista_albums.ID_Album
                        INNER JOIN artista
                        ON artista_albums.ID_Artista = artista.ID
                        WHERE LOWER(artista.Nome) LIKE LOWER("{}")
                        GROUP BY artista.ID;
                        """.format(search)

                    cursor.execute(sql)    
                    table_rows = cursor.fetchall() 

                if(len(singers) == 2):

                    singer1 = singers[0].strip() 
                    singer2 = singers[1].strip() 
                   
                    # ConSsulta com uniao
                    sql = """WITH
                        Cantor_1 AS (
                            SELECT Danceabilidade, Energia, Valencia, Volume
                            FROM musica
                            INNER JOIN album
                            ON musica.ID_Album = album.ID
                            INNER JOIN artista_albums
                            ON album.ID = artista_albums.ID_Album
                            INNER JOIN artista
                            ON artista_albums.ID_Artista = artista.ID
                            WHERE LOWER(artista.Nome) LIKE LOWER("{singer1}")
                            GROUP BY artista.ID
                        ),
                        Cantor_2 AS (
                            SELECT Danceabilidade, Energia, Valencia, Volume
                            FROM musica
                            INNER JOIN album
                            ON musica.ID_Album = album.ID
                            INNER JOIN artista_albums
                            ON album.ID = artista_albums.ID_Album
                            INNER JOIN artista
                            ON artista_albums.ID_Artista = artista.ID
                            WHERE LOWER(artista.Nome) LIKE LOWER("{singer2}")
                            GROUP BY artista.ID
                        ),
                        uniao AS (
                            SELECT * FROM Cantor_1
                            UNION ALL
                            SELECT * FROM Cantor_2
                        )
                        SELECT AVG(Danceabilidade) AS avg_Danceabilidade, AVG(Energia) AS avg_Energia, AVG(Valencia) AS avg_Valencia, AVG(Volume) AS avg_Volume
                        FROM uniao;""".format(singer1 = singer1, singer2 = singer2)
                    
                    cursor.execute(sql)    
                    table_rows = cursor.fetchall() 

                if(len(table_rows)):
                    
                    medias = list(table_rows[0].values())

                    ids = recomendacao("off", medias, 20)
                    id_songs = "(" + ", ".join(["'" + id_song + "'" for id_song in ids]) + ")"

                    # Consulta envolvendo conjunto (interseccao)
                    sql = """
                    SELECT musica.Nome AS MusicaNome, 
                            musica.ID AS ID, 
                            artista.Nome AS ArtistaNome,
                            Imagem_capa AS Imagem_capa                
                    FROM musica 
                    INNER JOIN album
                    ON musica.ID_Album = album.ID     
                    INNER JOIN artista_albums
                    ON album.ID = artista_albums.ID_Album
                    INNER JOIN artista
                    ON artista_albums.ID_Artista = artista.ID                        
                    WHERE musica.ID IN {id_songs}
                    ORDER BY musica.Nome ASC
                    """.format(id_songs = id_songs)

                    cursor.execute(sql)        
                    result_query = cursor.fetchall()
                    
                    result = []
                    for id_song in (ids):
                        result.append([song for song in result_query if song['ID'] == id_song][0])


                    df_table_songs = pd.DataFrame(result, columns = ["Nome", "ID", "Popularidade", "Imagem_capa"])

                    images = []
                    for image in df_table_songs["Imagem_capa"].values:
                        images.append(b64encode(image).decode("utf-8"))
                    image = images[0]

            search = "%{}%".format(search)

            if type == "song":


                # 1 - Colsulta projecao e selecao
                sql = """
                    SELECT Danceabilidade, Energia, Valencia, Volume                         
                    FROM musica
                    WHERE LOWER(musica.Nome) LIKE LOWER("{}");
                    """.format(search)

                cursor.execute(sql)    
                table_rows = cursor.fetchall()
                df_table_songs = pd.DataFrame(table_rows)   

                if(len(df_table_songs)):
                    medias = df_table_songs.mean().tolist()
                    ids = recomendacao("off", medias, 20)
                    id_songs = "(" + ", ".join(["'" + id_song + "'" for id_song in ids]) + ")"

                    query_music = """ WHERE musica.ID IN {} """.format(id_songs)

                    sql = """
                        SELECT musica.Nome AS MusicaNome, 
                               musica.ID AS ID, 
                               artista.Nome AS ArtistaNome,
                               Imagem_capa AS Imagem_capa                
                        FROM musica 
                        INNER JOIN album
                        ON musica.ID_Album = album.ID     
                        INNER JOIN artista_albums
                        ON album.ID = artista_albums.ID_Album
                        INNER JOIN artista
                        ON artista_albums.ID_Artista = artista.ID                        
                        {}
                        ORDER BY musica.Nome ASC
                        """.format(query_music)

                    cursor.execute(sql)        
                    result_query = cursor.fetchall()
                    
                    result = []
                    for id_song in (ids):
                        result.append([song for song in result_query if song['ID'] == id_song][0])

                    df_table_songs = pd.DataFrame(result, columns = ["Nome", "ID", "Popularidade", "Imagem_capa"])

                    images = []
                    for image in df_table_songs["Imagem_capa"].values:
                        images.append(b64encode(image).decode("utf-8"))
                    image = images[0]

            
            if type == "album":

                # Juncao de APENAS 2 relacoes
                # 5 - Consulta com agragacao (AVG)
                sql = """
                    SELECT AVG(Danceabilidade), AVG(Energia), AVG(Valencia), AVG(Volume)                       
                    FROM musica
                    INNER JOIN album
                    ON musica.ID_Album = album.ID
                    WHERE LOWER(album.Nome) LIKE LOWER("{}")
                    GROUP BY album.ID;
                    """.format(search)

                cursor.execute(sql)    
                table_rows = cursor.fetchall()

                if(len(table_rows)):

                    medias = list(table_rows[0].values())


                    ids = recomendacao("off", medias, 20)
                    id_songs = "(" + ", ".join(["'" + id_song + "'" for id_song in ids]) + ")"

                    # Consulta com juncao externa com duas Apenas duas relacoes
                    sql = """
                            WITH
                                artista_albuns AS (
                                    SELECT album.ID AS ID_Album, 
                                    artista.ID AS ID_artistas, 
                                    artista.Nome, 
                                    Imagem_capa 
                                    FROM album
                                    INNER JOIN artista_albums
                                    ON album.ID = artista_albums.ID_Album
                                    INNER JOIN artista
                                    ON artista_albums.ID_Artista = artista.ID
                                )

                                SELECT musica.Nome AS MusicaNome, 
                                    musica.ID AS ID, 
                                    artista_albuns.Nome AS ArtistaNome,
                                    Imagem_capa AS Imagem_capa
                                FROM musica 
                                LEFT OUTER JOIN artista_albuns
                                    ON musica.ID_Album = artista_albuns.ID_Album
                                WHERE musica.ID IN {id_songs}
                                ORDER BY musica.Nome ASC;""".format(id_songs = id_songs)

                    cursor.execute(sql)        
                    result_query = cursor.fetchall()
                    
                    result = []

                    for id_song in (ids):
                        result.append([song for song in result_query if song['ID'] == id_song][0])
                    df_table_songs = pd.DataFrame(result, columns = ["Nome", "ID", "Popularidade", "Imagem_capa"])

                    images = []
                    for image in df_table_songs["Imagem_capa"].values:
                        images.append(b64encode(image).decode("utf-8"))
                    image = images[0]
            
            if type == "cidade":

                # 5 - Consulta com agragacao (AVG)
                sql = """
                    SELECT AVG(Danceabilidade), AVG(Energia), AVG(Valencia), AVG(Volume)                        
                    FROM musica
                    INNER JOIN ranking_musicas
                        ON musica.ID = ranking_musicas.ID_musica
                    INNER JOIN ranking
                        ON ranking.ID = ranking_musicas.ID_Ranking
                    INNER JOIN cidade
                        ON cidade.ID = ranking.Codigo_Cidade
                    WHERE LOWER(cidade.nome) LIKE LOWER("{}")
                    GROUP BY cidade.ID;                    
                    """.format(search)

                cursor.execute(sql)    
                table_rows = cursor.fetchall()
                
                if(len(table_rows)):

                    # 5 - TO-DO - Passar pra sql para consulta de agregacao
                    medias = list(table_rows[0].values())



                    ids = recomendacao("off", medias, 20)
                    id_songs = "(" + ", ".join(["'" + id_song + "'" for id_song in ids]) + ")"

                    sql = """
                    SELECT musica.Nome AS MusicaNome, 
                            musica.ID AS ID, 
                            artista.Nome AS ArtistaNome,
                            Imagem_capa AS Imagem_capa                
                    FROM musica 
                    INNER JOIN album
                    ON musica.ID_Album = album.ID     
                    INNER JOIN artista_albums
                    ON album.ID = artista_albums.ID_Album
                    INNER JOIN artista
                    ON artista_albums.ID_Artista = artista.ID                        
                    WHERE musica.ID IN {id_songs}
                    ORDER BY musica.Nome ASC
                    """.format(id_songs = id_songs)

                    cursor.execute(sql)        
                    result_query = cursor.fetchall()
                    
                    result = []
                    for id_song in (ids):
                        result.append([song for song in result_query if song['ID'] == id_song][0])


                    df_table_songs = pd.DataFrame(result, columns = ["Nome", "ID", "Popularidade", "Imagem_capa"])

                    images = []
                    for image in df_table_songs["Imagem_capa"].values:
                        images.append(b64encode(image).decode("utf-8"))
                    image = images[0]

    return render_template("musicas.html", musicas = result, search = request.args.get("search"),
                            cidades = cidades, images = images, regioes = regioes, estados = estados)
                            
                            
@app.route("/ranking_tipo", methods=['GET', 'POST'])

def PlayTypes():

    global cidade, localidade

    with connection.cursor() as cursor:

        cursor.execute('SELECT Nome FROM Cidade ORDER BY Nome ASC;') 
        cidades = cursor.fetchall()

        cursor.execute('SELECT DISTINCT(Nome) FROM Estado ORDER BY Nome ASC;') 
        estados = cursor.fetchall() 

        cursor.execute('SELECT DISTINCT(Regiao) FROM Estado ORDER BY Regiao ASC;') 
        regioes = cursor.fetchall()   

        try:
            city = request.args["cidadeSel"]
            cidade = city

            if "estado" in cidade:
                localidade = "estado"
            
            elif "regiao" in cidade:
                localidade = "regiao"

            else:
                localidade = "cidade"

            cidade = cidade.split("_")[1]
        

        except:
            pass

        
    
    return render_template("people.html", cidades = cidades, cidadeSel = cidade, regioes = regioes, 
    estados = estados, localidade = localidade)

@app.route("/ranking", methods=['GET', 'POST'])

def ShowRanking():
        
    global cidade, tipo

    try:
            tipo = request.args["action"]
            tipo = tipo.replace("Ranking ", "")
        
    except:
            pass

    

    with connection.cursor() as cursor:

        cursor.execute('SELECT Nome FROM Cidade ORDER BY Nome ASC;') 
        cidades = cursor.fetchall()

        cursor.execute('SELECT DISTINCT(Nome) FROM Estado ORDER BY Nome ASC;') 
        estados = cursor.fetchall() 

        cursor.execute('SELECT DISTINCT(Regiao) FROM Estado ORDER BY Regiao ASC;')  
        regioes = cursor.fetchall() 
        
        if localidade == "cidade":
        
            try:
                semana = request.args["semana"]          

                # Consulta aninhada  
                sql = """            
                WITH ID_songs AS (
                    SELECT ID_musica, Posicao, ranking_musicas.Data 
                    FROM ranking
                    INNER JOIN cidade
                        ON ranking.Codigo_Cidade = cidade.ID
                    INNER JOIN ranking_musicas
                        ON ranking_musicas.ID_Ranking = ranking.ID
                    WHERE ranking_musicas.Data = "{semana}"
                        AND cidade.nome = "{cidade}"
                        AND ranking.Tipo = "{tipo}") 
                
                SELECT ID_songs.Posicao , musica.Nome AS MusicaNome, 
                                    musica.ID AS ID, 
                                    artista.Nome AS ArtistaNome,
                                    Imagem_capa AS Imagem_capa,
                                    ID_songs.Data
                FROM ID_songs 
                INNER JOIN musica
                    ON musica.ID = ID_songs.ID_musica 
                INNER JOIN album
                    ON musica.ID_Album = album.ID     
                INNER JOIN artista_albums
                    ON album.ID = artista_albums.ID_Album
                INNER JOIN artista
                    ON artista_albums.ID_Artista = artista.ID  
                ORDER BY Posicao ASC;
                """.format(cidade = cidade, tipo = tipo, semana = semana)
                
            except:

                # Consulta aninhada            
                sql = """
                    WITH Rankig_Escolhido AS (
                            SELECT ranking.ID, Data                
                            FROM ranking
                            INNER JOIN cidade
                            ON ranking.Codigo_Cidade = cidade.ID
                            INNER JOIN ranking_musicas
                            ON ranking_musicas.ID_Ranking = ranking.ID
                            WHERE cidade.nome = "{cidade}"
                            AND ranking.Tipo = "{tipo}"
                            ORDER BY DATA DESC
                            LIMIT 1),
                            ID_songs AS (
                                SELECT ID_musica, Posicao, ranking_musicas.Data FROM Rankig_Escolhido
                                INNER JOIN ranking_musicas
                                ON (ranking_musicas.Data = Rankig_Escolhido.data AND ranking_musicas.ID_Ranking = Rankig_Escolhido.ID)
                            ) 
                            SELECT ID_songs.Posicao , musica.Nome AS MusicaNome, 
                                    musica.ID AS ID, 
                                    artista.Nome AS ArtistaNome,
                                    Imagem_capa AS Imagem_capa,
                                    ID_songs.Data
                            FROM ID_songs 
                                INNER JOIN musica
                                ON musica.ID = ID_songs.ID_musica 
                                INNER JOIN album
                                ON musica.ID_Album = album.ID     
                                INNER JOIN artista_albums
                                ON album.ID = artista_albums.ID_Album
                                INNER JOIN artista
                                ON artista_albums.ID_Artista = artista.ID  
                                ORDER BY Posicao ASC;
                            """.format(cidade = cidade, tipo = tipo)

        elif localidade == "estado":

            try:
                semana = request.args["semana"]

            except:
                sql = """
                    SELECT MAX(Data)
                    FROM ranking
                    INNER JOIN cidade
                        ON ranking.Codigo_Cidade = cidade.ID
                    INNER JOIN estado
                        ON estado.Nome = cidade.Estado
                    INNER JOIN ranking_musicas
                        ON ranking_musicas.ID_Ranking = ranking.ID
                    WHERE estado.Nome = "{estado}";
                    """.format(estado = cidade)

                
                cursor.execute(sql)      

                result_query = cursor.fetchall()
                semana = result_query[0]['MAX(Data)']
                       

            # Consulta aninhada  
            sql = """            
            WITH ID_songs AS(
                SELECT ID_musica, COUNT(*), MAX(Posicao), ranking_musicas.Data,
                        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC, MAX(Posicao) ASC) AS Posicao
                FROM ranking
                INNER JOIN cidade
                    ON ranking.Codigo_Cidade = cidade.ID
                INNER JOIN estado
                    ON estado.Nome = cidade.Estado
                INNER JOIN ranking_musicas
                    ON ranking_musicas.ID_Ranking = ranking.ID
                WHERE ranking_musicas.Data = "{semana}"
                    AND estado.Nome = "{cidade}"
                    AND ranking.Tipo = "{tipo}"
                GROUP BY ID_musica
                LIMIT 100)  
            SELECT ID_songs.Posicao , musica.Nome AS MusicaNome, 
                                musica.ID AS ID, 
                                artista.Nome AS ArtistaNome,
                                Imagem_capa AS Imagem_capa,
                                ID_songs.Data
            FROM ID_songs 
            INNER JOIN musica
                ON musica.ID = ID_songs.ID_musica 
            INNER JOIN album
                ON musica.ID_Album = album.ID     
            INNER JOIN artista_albums
                ON album.ID = artista_albums.ID_Album
            INNER JOIN artista
                ON artista_albums.ID_Artista = artista.ID 
            GROUP BY ID
            ORDER BY Posicao ASC;
            """.format(cidade = cidade, tipo = tipo, semana = semana)

                

        elif localidade == "regiao":
        
            try:
                semana = request.args["semana"]

            except:
                sql = """
                    SELECT MAX(Data)
                    FROM ranking
                    INNER JOIN cidade
                        ON ranking.Codigo_Cidade = cidade.ID
                    INNER JOIN estado
                        ON estado.Nome = cidade.Estado
                    INNER JOIN ranking_musicas
                        ON ranking_musicas.ID_Ranking = ranking.ID
                    WHERE estado.Regiao = "{regiao}";
                    """.format(regiao = cidade)

                cursor.execute(sql)        
                result_query = cursor.fetchall()
                semana = result_query[0]['MAX(Data)']
                       

            # Consulta aninhada  
            sql = """            
            WITH ID_songs AS(
                SELECT ID_musica, COUNT(*), MAX(Posicao), ranking_musicas.Data,
                        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC, MAX(Posicao) ASC) AS Posicao
                FROM ranking
                INNER JOIN cidade
                    ON ranking.Codigo_Cidade = cidade.ID
                INNER JOIN estado
                    ON estado.Nome = cidade.Estado
                INNER JOIN ranking_musicas
                    ON ranking_musicas.ID_Ranking = ranking.ID
                WHERE ranking_musicas.Data = "{semana}"
                    AND estado.Regiao = "{cidade}"
                    AND ranking.Tipo = "{tipo}"
                GROUP BY ID_musica
                LIMIT 100)  
            SELECT ID_songs.Posicao , musica.Nome AS MusicaNome, 
                                musica.ID AS ID, 
                                artista.Nome AS ArtistaNome,
                                Imagem_capa AS Imagem_capa,
                                ID_songs.Data
            FROM ID_songs 
            INNER JOIN musica
                ON musica.ID = ID_songs.ID_musica 
            INNER JOIN album
                ON musica.ID_Album = album.ID     
            INNER JOIN artista_albums
                ON album.ID = artista_albums.ID_Album
            INNER JOIN artista
                ON artista_albums.ID_Artista = artista.ID 
            GROUP BY ID
            ORDER BY Posicao ASC;
            """.format(cidade = cidade, tipo = tipo, semana = semana)
                
           
       
        cursor.execute(sql)        
        result = cursor.fetchall()
        
        df_table_songs = pd.DataFrame(result, columns = ["Posicao", "Nome", "ID", "ArtistaNome", "Imagem_capa", "Data"])
        
        if len(df_table_songs):
            images = []
            for image in df_table_songs["Imagem_capa"].values:
                images.append(b64encode(image).decode("utf-8"))

    return render_template("Ranking.html", musicas = result, cidades = cidades, images = images, 
    cidade = cidade, estados = estados, regioes = regioes)


if __name__ == "__main__":
    app.run(debug=config.DEGUB)
