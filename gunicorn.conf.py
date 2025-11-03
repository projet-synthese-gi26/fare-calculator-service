import os

# Nombre de workers (processus) recommandé
workers = int(os.environ.get('GUNICORN_WORKERS', 4))

# Timeout en secondes
timeout = 120

# --- MODIFICATION CLÉ ---
# Récupérer le port depuis la variable d'environnement PORT fournie par Render.
# Si la variable n'existe pas (pour le développement local), utiliser 8000 par défaut.
port = os.environ.get('PORT', 8000)

# Construire la directive bind dynamiquement
bind = f"0.0.0.0:{port}"
# --- FIN DE LA MODIFICATION ---

# Activer les logs
accesslog = '-'
errorlog = '-'

# Mode de travail recommandé
worker_class = 'sync'

# Nombre maximum de requêtes par worker avant redémarrage
max_requests = 1000
max_requests_jitter = 50

# Préchargement de l'application
preload_app = True