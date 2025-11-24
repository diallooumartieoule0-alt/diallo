# OUMarTips — Football prediction bot

Petit projet Python: ingestion de CSV publics, baseline Poisson, et un bot Telegram fournissant des prédictions de matchs.

**Quickstart**
- **Install:** `python -m pip install -r requirements.txt`
- **Train (local):** `python train/train_poisson.py`
- **Run bot (local):**
  - Set environment variables `TELEGRAM_TOKEN` and optional `TELEGRAM_MODEL_PATH`.
  - `python bot/telegram_bot.py`

**Déploiement (Docker + GitHub Actions)**

Ce dépôt contient un `Dockerfile` et une Action GitHub `/.github/workflows/deploy_bot.yml` qui construisent l'image et peuvent:
- pousser l'image sur Docker Hub (si les secrets Docker Hub sont fournis),
- et/ou déployer via SSH sur un hôte distant (si les secrets SSH sont fournis).

Étapes rapides pour déployer:

1. Construire et tester l'image localement:

```powershell
docker build -t local/diallo:latest .
docker run -e TELEGRAM_TOKEN='your_token' -e TELEGRAM_MODEL_PATH='/app/models/poisson_baseline.joblib' local/diallo:latest
```

2. (Optionnel) Pousser l'image vers Docker Hub via GitHub Actions:
- Ajoutez les secrets du repo GitHub: `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN`.
- Poussez sur `main`; l'Action construira et poussera l'image vers `DOCKERHUB_USERNAME/diallo:latest`.

3. (Optionnel) Déploiement SSH automatique:
- Ajoutez ces secrets dans `Settings → Secrets` du repo:
  - `SSH_PRIVATE_KEY` : contenu de la clé privée (PEM)
  - `SSH_HOST` : host ou IP de la machine distante
  - `SSH_USER` : utilisateur SSH
  - `TELEGRAM_TOKEN` : token du bot Telegram (utilisé pour démarrer le container)
  - `TELEGRAM_MODEL_PATH` (optionnel) : chemin au modèle sur la machine distante
  - Optionnel: `REMOTE_DOCKER_IMAGE` et `REMOTE_DOCKER_CONTAINER_NAME`

L'Action `deploy_bot.yml` va alors effectuer `docker pull` (image définie par le secret `REMOTE_DOCKER_IMAGE` ou par le nom construit à partir de `DOCKERHUB_USERNAME`), puis `docker rm -f` et `docker run -d` pour relancer le container distant en fournissant `TELEGRAM_TOKEN` et `TELEGRAM_MODEL_PATH`.

Sécurité & recommandations
- Utilisez `ssh-keygen -t ed25519` pour créer une clé dédiée au déploiement et ajoutez la clé publique dans `~/.ssh/authorized_keys` sur l'hôte distant.
- Ne stockez jamais de tokens en clair dans le repo; utilisez toujours les GitHub Secrets.
- Pour des déploiements plus robustes, utilisez `docker-compose` ou un orchestrateur (systemd, swarm, k8s) côté serveur; je peux générer un `docker-compose.yml` si vous le souhaitez.

Si vous voulez, je peux maintenant:
- ajouter un `docker-compose.yml` et modifier l'Action pour l'utiliser côté distant, ou
- adapter la workflow pour publier sur GitHub Container Registry (GHCR) au lieu de Docker Hub.
