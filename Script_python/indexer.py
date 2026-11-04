# indexer.py — charge les fichiers Markdown, 
# les découpe en chunks et génère leur représentation vectorielle (embeddings),
# puis les stocke dans ChromaDB



#--------------------------------------------------------
# importation de bibliotheque
#--------------------------------------------------------
from dotenv import load_dotenv # pour lire le fichier .env
from openai import OpenAI
import os
import chromadb

#--------------------------------------------------------
# dossier où se trouve ce fichier Python
dossier = os.path.dirname(__file__) 


#--------------------------------------------------------
# creation d'un client chroma db pour pouvoir ce connecter a la base de donné
chemin_db = os.path.join(os.path.dirname(dossier), "db")
chroma_client = chromadb.PersistentClient(path=chemin_db)


# creation de la collection pour stocker les données
collection = chroma_client.get_or_create_collection(name = "Collection_Nevezia")
#--------------------------------------------------------


#--------------------------------------------------------
# appeler la fonction pour charger les variables
load_dotenv(os.path.join(dossier, "api_rag.env"))

#  récupérer la clé api d'OpenAI dans une variable
api_key_openAI = os.getenv("OPENAI_API_KEY")


# creer le client a partie de la cle api
client = OpenAI(api_key = api_key_openAI)


#--------------------------------------------------------

#--------------------------------------------------------
# MODULE 1 : LECTURE D'UN FICHIER
#--------------------------------------------------------


chemin_fichier_md = os.path.join(os.path.dirname(dossier), "documents")

fichiers = [f for f in os.listdir(chemin_fichier_md) if f.endswith(".md")]


documents = [] # contiendra le texte brut de chaque fichier

for fichier in fichiers:
    chemin = os.path.join(chemin_fichier_md, fichier) # chemin complet vers le fichier
    with open(chemin, "r", encoding="utf-8") as f:
        contenu = f.read() # lit tout le fichier d'un coup
    documents.append((fichier, contenu)) # ajoute le texte à la liste

print(f"{len(documents)} documents chargés")

#--------------------------------------------------------
# MODULE 2 : découpage en chunks
#--------------------------------------------------------


chunks = []

for document in documents: # boucle d'element sur elements, afin de chunker sur les 3 documents
    sections = document[1].split("## ") # sépare le texte du document en liste de mots
    source = document[0] # document[0] correspond au source

    for section in sections : 
        dic = {}
        dic["texte"] = section # ajoute du contenu dans le dictionnaire tous les 200 mots
        dic["source"] = source # ajoute des sources 

        chunks.append(dic) # ajout du dictionnaire dans la liste de chunks pour savoir combien de chunks sont crée
print(f"{len(chunks)} chunks générés")

#--------------------------------------------------------
# MODULE 3 Embeddings
#--------------------------------------------------------
"""
Un embedding c'est quoi concrètement : tu envoies une chaîne de texte à une API, 
elle te renvoie une liste de nombres (ex: [0.12, -0.34, 0.87, ...]). 
Ces nombres représentent le "sens" du texte dans un espace mathématique. 
Deux textes similaires auront des vecteurs proches.
"""

for chunk in chunks: 
    reponse = client.embeddings.create(input = chunk["texte"],model = "text-embedding-3-small") # appelle de l'api pour le texte de chaque chunk
    chunk["embedding"] = reponse.data[0].embedding # ajoute de la reponse de l'api 
                                                   #qui est l'embedding dans la liste de chaque chunk

    
# MODULE 4 Chrome DB

# ajout des chunks dans la collection chroma db, en ajoutant, un id, les documents, et les embeddings, et le nom du document (sources)
for index, chunk in enumerate(chunks) :
    collection.upsert(
        ids = str(index),
        documents = chunk["texte"],
        embeddings= chunk["embedding"],
        metadatas= {"source" : chunk["source"]}  # sources des fichiers pour comparer avec le bot si le fichiers existe deja dans la bdd
    )





