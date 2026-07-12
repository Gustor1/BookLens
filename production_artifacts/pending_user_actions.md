# Actions utilisateur en attente - Lancement MediaLens V2

Suivez ces étapes pour démarrer localement la version 2.0 de MediaLens :

## 1. Installation des dépendances Python

Dans votre terminal, activez votre environnement virtuel python (ou créez-en un à la racine) et installez les packages pour FastAPI :

```bash
# Créez l'environnement virtuel si besoin
python -m venv .venv

# Activez l'environnement
# Sur Windows (PowerShell) :
.venv\Scripts\activate
# Sur macOS/Linux :
source .venv/bin/activate

# Installez les dépendances du backend et du projet existant
pip install -r app_build/requirements.txt
pip install -r backend_api/requirements.txt
```

## 2. Démarrage du Backend FastAPI

Lancez le serveur API sur le port `8000` :

```bash
cd backend_api
uvicorn app.main:app --reload --port 8000
```
Le serveur chargera le modèle ML existant et se connectera à ChromaDB. Vous pouvez tester le statut sur : [http://localhost:8000/api/health](http://localhost:8000/api/health).

## 3. Démarrage du Frontend Next.js

Dans un second terminal, démarrez le serveur Next.js sur le port `3000` :

```bash
cd frontend
# Configurez l'adresse de l'API locale
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local

# Démarrez
npm run dev
```

Ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur pour profiter de l'expérience culturelle immersive.
