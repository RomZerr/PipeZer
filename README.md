# PipeZer 🎬

**PipeZer** est un outil de pipeline 3D professionnel développé pour optimiser la gestion de projets cinématographiques et d'animation 3D.

## 🚀 Fonctionnalités

- **Gestion de projets** : Structure automatique de dossiers pour assets, shots, ressources
- **Intégration Maya** : Scripts et outils pour Maya (export Alembic, USD, GPU Cache)
- **Intégration Houdini** : Support complet pour Houdini avec shelf et menus
- **Interface moderne** : UI intuitive avec thèmes sombres
- **Gestion des assets** : Création, organisation et suivi des assets 3D
- **Système de notifications** : Suivi des tâches et notifications en temps réel
- **Multi-projets** : Support de plusieurs projets simultanément

## 📋 Prérequis

- **Windows 10/11**
- **Python 3.9+** (inclus dans l'installateur)
- **Maya 2023+** (optionnel)
- **Houdini 19.5+** (optionnel)

## 🛠️ Installation

### Option 1 : Installateur (Recommandé)
1. Téléchargez `PipeZer_Install.exe`
2. Exécutez l'installateur
3. Choisissez le dossier d'installation
4. PipeZer sera installé avec tous les composants nécessaires

### Option 2 : Installation manuelle
```bash
git clone https://github.com/ton-username/PipeZer.git
cd PipeZer
pip install -r requirements.txt
python pipezer.py
```

## 🎯 Utilisation

1. **Lancement** : Exécutez `PipeZer.exe` ou `python pipezer.py`
2. **Sélection de projet** : Choisissez ou créez un nouveau projet
3. **Configuration** : PipeZer détecte automatiquement vos logiciels 3D
4. **Travail** : Utilisez l'interface pour gérer vos assets et shots

## 📁 Structure de projet

```
MonProjet/
├── 02_ressource/          # Ressources partagées
│   ├── Template_scenes/   # Scènes templates
│   └── Textures/         # Textures communes
├── 04_asset/             # Assets 3D
│   ├── character/        # Personnages
│   ├── prop/            # Accessoires
│   └── environnement/    # Environnements
├── 05_shot/             # Shots de production
│   ├── seq01/           # Séquence 01
│   └── seq02/           # Séquence 02
└── .pipezer_data/       # Données PipeZer
    ├── file_data.json   # Métadonnées fichiers
    ├── prefix.json      # Préfixes projet
    └── variants.json    # Variantes assets
```

## 🔧 Configuration

### Intégration Maya
PipeZer s'intègre automatiquement dans Maya via :
- **Shelf** : Boutons d'outils PipeZer
- **Menu** : Menu PipeZer dans la barre de menu
- **Scripts** : Scripts Python et MEL automatiques

### Intégration Houdini
- **Shelf** : Outils PipeZer dans le shelf
- **Menu** : Menu contextuel PipeZer
- **Scripts** : Scripts Python automatiques

## 🎨 Personnalisation

- **Thèmes** : Plusieurs thèmes disponibles (sombre, clair, personnalisé)
- **Styles** : Interface personnalisable
- **Préférences** : Configuration utilisateur sauvegardée

## 📝 Développement

### Structure du code
```
Packages/
├── apps/                 # Applications (Maya, Houdini, Standalone)
├── logic/               # Logique métier
├── ui/                  # Interface utilisateur
└── utils/               # Utilitaires et constantes
```

### Contribution
1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Romain Dubec** - Développeur Pipeline 3D

## 🤝 Support

Pour toute question ou problème :
- Ouvrez une [Issue](https://github.com/ton-username/PipeZer/issues)
- Contactez l'auteur

## 🔄 Changelog

### v1.0.0
- Version initiale
- Interface standalone complète
- Intégration Maya et Houdini
- Système de gestion de projets
- Support multi-projets
- Interface moderne et personnalisable

---

**PipeZer** - Simplifiez votre pipeline 3D ! 🎬✨
