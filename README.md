# eFootKings 2026 🇨🇮

Site web complet pour le tournoi eFootball Mobile 2026 - eFootKings 2026.

## 🎮 Fonctionnalités

- **Page d'accueil** : Présentation du tournoi, règles, images
- **Inscription** : Formulaire avec upload de screenshot de paiement
- **Bracket** : Affichage du bracket complet pour 8 joueurs
- **Dashboard Admin** : Gestion des joueurs et des scores

## 🚀 Installation locale

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python app.py
```

L'application sera accessible sur `http://localhost:5000`

## 🔐 Accès Admin

- **URL** : `/admin/login`
- **Username** : `admin`
- **Password** : `admin123`

⚠️ **Important** : Changez le mot de passe en production !

## 📦 Déploiement sur Vercel

1. Installer Vercel CLI :
```bash
npm i -g vercel
```

2. Se connecter à Vercel :
```bash
vercel login
```

3. Déployer :
```bash
vercel
```

4. Pour tester en local avec Vercel :
```bash
vercel dev
```

## 📁 Structure du projet

```
kingsefootball2026/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── vercel.json           # Configuration Vercel
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── bracket.html
│   ├── admin_login.html
│   └── admin_dashboard.html
├── static/               # Fichiers statiques
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── data/                 # Données JSON (créé automatiquement)
│   ├── players.json
│   ├── bracket.json
│   └── admin.json
└── uploads/              # Screenshots de paiement (créé automatiquement)
```

## 🎨 Technologies utilisées

- **Flask** : Framework web Python
- **Bootstrap 5** : Framework CSS
- **Font Awesome** : Icônes
- **Google Fonts (Poppins)** : Police de caractères
- **Animate.css** : Animations

## 📝 Notes

- Les données sont stockées dans des fichiers JSON
- Les screenshots sont sauvegardés dans le dossier `uploads/`
- Le tournoi est limité à 8 joueurs maximum
- Le bracket est généré automatiquement quand 8 joueurs sont validés

## 🔒 Sécurité

- Changez le `SECRET_KEY` dans `app.py` et `vercel.json` en production
- Changez les identifiants admin dans `data/admin.json` après la première connexion
- Les mots de passe sont hashés avec Werkzeug

## 📞 Contact

Numéro Mobile Money pour les paiements : **+225 0500 44 82 08**

---

Développé avec ❤️ pour la communauté eFootball Mobile

