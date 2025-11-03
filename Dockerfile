# Étape 1: Choisir une image de base officielle et légère pour Python
FROM python:3.11-slim

# Étape 2: Définir le répertoire de travail dans le conteneur
# WORKDIR /

# Étape 3: Copier le fichier des dépendances et les installer
# On copie ce fichier en premier pour profiter du cache de Docker.
# Si requirements.txt ne change pas, Docker n'exécutera pas cette étape à chaque build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4: Copier tout le reste du code de l'application dans le conteneur
COPY . .

# Étape 5: Exposer le port sur lequel Gunicorn va écouter
# Votre gunicorn.conf.py spécifie le port 8000
EXPOSE 8000

# Étape 6: Définir la commande pour lancer l'application
# On utilise la configuration Gunicorn que vous avez déjà créée.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]