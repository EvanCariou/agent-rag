import gradio as gr
import anthropic
import chromadb
import os
from openai import OpenAI
from dotenv import load_dotenv # pour lire le fichier .env
from tavily import TavilyClient
from pypdf import PdfReader

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
 
api_key_tavily = os.getenv("TVILY_API_KEY") # cle api  tavily

# creer le client a partir de la cle api
client_embedding = OpenAI(api_key = api_key_openAI)

# creer le client anthropic 
client = anthropic.Anthropic(api_key = api_key_anth)

client_tavily = TavilyClient(api_key= api_key_tavily)


messages = []


# recherche de la fonction



def telecharger_fichier(question, fichier) :
    if fichier is not None : 
        if fichier.endswith(".pdf") :
            reader = PdfReader(fichier)
            pdf = [f.extract_text() for f in reader.pages]
            contenu_pdf = "\n".join(pdf)
            return contenu_pdf 
        else :
            with open(fichier, "r", encoding="utf-8") as f:
                contenu = f.read()
            return contenu
    else : 
        return ""


def generer_chatbot_reponse(question ,historique, fichier):

    resultat_web = client_tavily.search(query=question, max_results=3)

    reponse_web = [r["content"] for r in resultat_web["results"]]
    
    reponse_query = client_embedding.embeddings.create(
            input=question, 
            model="text-embedding-3-small"
        )
    results = collection.query(
            query_embeddings=reponse_query.data[0].embedding,
            n_results=13
        )
    

        # contexte pour le LLM
    contexte_fichier = telecharger_fichier(question, fichier)
    contexte_web = "\n".join(reponse_web)
    contexte_interne = "\n".join(results["documents"][0])
    question_contexte = f"Contexte interne:\n{contexte_interne}\n\n Résultats web:\n{contexte_web}\n\nQuestion: {question} \n\n Fichier{contexte_fichier}"

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

    return reponse_agent








css = """
body, .gradio-container { background-color: #0F172A !important; color: #E2E8F0 !important; }
footer { display: none !important; }
"""

with gr.Blocks(css=css, title="Assistant IA") as interface:
    gr.Markdown("# Assistant IA\nBase de connaissance interne")
    gr.ChatInterface(fn=generer_chatbot_reponse, additional_inputs=gr.File())

interface.launch()

