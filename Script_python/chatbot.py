#--------------------------------------------------------
# IMPORTATIONS
#--------------------------------------------------------
from dotenv import load_dotenv # pour lire le fichier .env
from openai import OpenAI
import os
import chromadb
import anthropic

#--------------------------------------------------------
# CONFIGURATION — CHEMINS ET DOSSIERS
#--------------------------------------------------------
dossier        = os.path.dirname(__file__)
chemin_db      = os.path.join(os.path.dirname(dossier), "db")
chemin_docs    = os.path.join(os.path.dirname(dossier), "documents")
chemin_indexer = os.path.join(dossier, "indexer.py")


#--------------------------------------------------------
# CONFIGURATION — CHROMADB
#--------------------------------------------------------
# creation d'un client chromadb pour pouvoir se connecter a la base de données
chroma_client = chromadb.PersistentClient(path=chemin_db)

# creation de la collection pour stocker les données
collection = chroma_client.get_or_create_collection(name="Collection_documents")


#--------------------------------------------------------
# CONFIGURATION 
#--------------------------------------------------------
# appeler la fonction pour charger les variables
load_dotenv(os.path.join(dossier, "api_rag.env"))

# récupérer les cle api dans une variable

api_key_openAI = os.getenv("OPENAI_API_KEY") # cle api de openAi

api_key_anth = os.getenv("ANTHROPIC_API_KEY") # cle api d'anthropic
 
# creer le client a partie de la cle api
client_embedding = OpenAI(api_key = api_key_openAI)

# creer le client anthropic 
client = anthropic.Anthropic(api_key = api_key_anth)

#--------------------------------------------------------
# INDEXATION AUTOMATIQUE
# Si un fichier .md n'est pas encore dans la base,
# on relance indexer.py avant de démarrer le chatbot.
#--------------------------------------------------------

# liste de comprehension, on parcours chaque fichier du dossier, avec f for f,
# puis on garde seulement ce qui finissent par md avec if...
fichiers_md = [f for f in os.listdir(chemin_docs) if f.endswith(".md")]

# recuperer les metadonnees dans la collection
# puis on dedoublonne les noms des fichiers, car ils sont cités à chaque chunk d'un fichier
sources_indexees = set(s["source"] for s in collection.get()["metadatas"])

# boucle sur fichiers pour relancer l'indexeur si un document a été ajouté mais pas encore indexé
for fichier in fichiers_md:
    if fichier not in sources_indexees:
        os.system(f'python "{chemin_indexer}"')
        break


#--------------------------------------------------------
# INITIALISATION DE LA CONVERSATION
#--------------------------------------------------------
print(" ======================================")
print(" ====== CONVERSATION AVEC LE LLM ====== ")
print(" ====================================== \n")

messages = []


#--------------------------------------------------------
# BOUCLE PRINCIPALE — CHATBOT
#--------------------------------------------------------
while True:

    # message qui s'affiche pour poser la question
    question = input("Votre question : ")

    if question.strip() in ["exit", "sortie", "fin"]:
        print("Fin de la conversation.")
        break

    else:
        # requete de recherche dans la collection, en utilisant l'api d'openai pour les embeddings
        reponse_query = client_embedding.embeddings.create(
            input=question,
            model="text-embedding-3-small"
        )
        results = collection.query(
            query_embeddings=reponse_query.data[0].embedding,
            n_results=13
        )

        # contexte pour le LLM
        contexte     = "\n".join(results["documents"][0])
        question_contexte = f"Contexte:\n{contexte}\n\nQuestion: {question}"

        # ajout de la question de l'utilisateur pour la memoire
        messages.append({"role": "user", "content": question_contexte })

       
        # parcour du flux d'evenement avec une boucle
        with client.messages.stream(
                model="claude-sonnet-4-6", 
                messages = messages,
                max_tokens = 1024,
                system="Tu es l'assistant d'Evan. Réponds uniquement en français") as stream:
            
            for text in stream.text_stream:
                print(text, end="", flush=True)
                # end="" : par défaut print ajoute un retour à la ligne \n après chaque appel
                # # flush=True : force l'affichage immédiat dans le terminal 
                # # Sans ça, Python peut mettre en buffer les caractères et les afficher par paquets

                
        # reponse de l'agent
        reponse_agent = stream.get_final_message().content[0].text

        # reponse de l'agent stockee dans la liste des messages
        messages.append({"role": "assistant", "content": reponse_agent})
        print("\n")

        # affichage des chunks utilises par l'agent pour repondre aux questions
        #print(" ==== Sources utilisées ===")
        #for index, mot in enumerate(results["documents"][0]):
        #  print(f"{index} : {mot[:100]}" + "\n")
