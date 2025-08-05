import multiprocessing

# Nombre de workers = (2 x nombre_de_CPU) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Nombre de threads par worker
threads = 2

# Adresse et port d'écoute
bind = '0.0.0.0:' + str(int(os.environ.get('PORT', 10000)))

# Timeout augmenté pour les requêtes longues
timeout = 120

# Nombre maximum de requêtes par worker avant redémarrage
max_requests = 5000
max_requests_jitter = 500

# Journalisation
accesslog = '-'  # Sortie vers stdout
errorlog = '-'   # Sortie vers stderr

# Redémarrage des workers de temps en temps pour éviter les fuites de mémoire
max_requests = 1000
max_requests_jitter = 50
