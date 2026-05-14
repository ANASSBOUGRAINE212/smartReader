# Cahier des Charges - SmartReader

## 1. Présentation du Projet

### 1.1 Contexte
SmartReader est une solution d'assistance pour personnes aveugles et malvoyantes, permettant la lecture de documents, la navigation et l'interaction avec l'environnement via reconnaissance visuelle et synthèse vocale.

### 1.2 Objectifs
- Faciliter l'accès à l'information écrite pour les personnes aveugles
- Permettre une utilisation autonome sans assistance visuelle
- Offrir une solution portable et abordable
- Supporter plusieurs langues (Arabe, Français, Anglais, Darija)

### 1.3 Public Cible
- Personnes aveugles
- Personnes malvoyantes
- Personnes âgées avec déficience visuelle
- Établissements d'aide aux personnes handicapées visuelles

## 2. Architecture Technique

### 2.1 Composants Système

#### 2.1.1 Serveur Raspberry Pi
- **Matériel**: Raspberry Pi 4 (4GB RAM minimum)
- **Caméra**: Module caméra Pi ou webcam USB
- **Système**: Raspberry Pi OS
- **Langage**: Python 3.13
- **Framework**: Flask (API REST)

#### 2.1.2 Application Mobile
- **Plateforme**: React Native avec Expo
- **SDK**: Expo SDK 54
- **Langages**: TypeScript, JavaScript
- **Navigation**: Expo Router
- **État**: Zustand

#### 2.1.3 Communication
- **Protocole**: HTTP/REST API
- **WebSocket**: Socket.io (streaming audio)
- **Réseau**: WiFi local (mDNS)

### 2.2 Services Backend (Pi Server)

#### Service OCR (Reconnaissance de Texte)
- **Moteur**: Tesseract OCR
- **Langues supportées**: Arabe, Français, Anglais
- **Prétraitement**: OpenCV (deskew, contraste, débruitage)
- **Format sortie**: Texte brut avec métadonnées

#### Service TTS (Synthèse Vocale)
- **Moteur**: gTTS (Google Text-to-Speech)
- **Langues**: Arabe, Français, Anglais, Darija
- **Paramètres**: Vitesse (0.5x - 2.0x), Tonalité
- **Format**: MP3

#### Service de Traduction
- **API**: Google Translate
- **Paires supportées**: Toutes combinaisons entre langues supportées
- **Cache**: Historique des traductions

#### Service de Capture
- **Résolution**: 1280x720
- **Prévisualisation**: Fenêtre OpenCV native (10 secondes)
- **Sources**: Caméra Pi, Caméra téléphone
- **Prétraitement**: Automatique

#### Service d'Historique
- **Stockage**: JSON local
- **Données**: Texte, audio, métadonnées, traductions
- **Limite**: 100 entrées récentes
- **Export**: Possible

## 3. Fonctionnalités

### 3.1 Fonctionnalités Actuelles (Implémentées)

#### 3.1.1 Lecture de Documents
- **Capture via caméra Pi**: 
  - Prévisualisation 10 secondes
  - Capture automatique
  - OCR + TTS
- **Capture via téléphone**:
  - Photo depuis l'application
  - Upload vers Pi
  - Traitement identique
- **Sortie audio**:
  - Haut-parleur Pi
  - Haut-parleur téléphone
  - Bluetooth (futur)

#### 3.1.2 Commandes Vocales
- **Activation**: Bouton microphone
- **Commandes disponibles**:
  - "Scan" / "Capture" - Déclencher scan
  - "Repeat" / "Répéter" - Relire dernier scan
  - "Stop" / "Arrêter" - Arrêter lecture
  - "Faster" / "Plus vite" - Augmenter vitesse
  - "Slower" / "Plus lent" - Réduire vitesse
  - "Translate to [langue]" - Traduire
  - "Share" / "Partager" - Partager texte

#### 3.1.3 Multi-langue
- **Langues interface**: Arabe, Français, Anglais
- **Langues OCR**: Arabe, Français, Anglais
- **Langues TTS**: Arabe, Français, Anglais, Darija
- **Traduction**: Entre toutes langues

#### 3.1.4 Historique
- **Stockage**: Tous les scans
- **Métadonnées**: Date, langue, nombre paragraphes
- **Audio**: Conservé avec texte
- **Recherche**: Par date, langue
- **Suppression**: Individuelle ou globale

#### 3.1.5 Paramètres
- **Langue**: Sélection langue préférée
- **Vitesse parole**: 0.5x à 2.0x
- **Tonalité**: Basse, Normale, Haute
- **Mode lecture**: Continu, Paragraphe, Section
- **Sortie audio**: Pi, Téléphone, Bluetooth
- **Moteur OCR**: Tesseract, Cloud (futur)

### 3.2 Fonctionnalités Futures (Proposées)

#### 3.2.1 Description de Scène (Priorité 1)
- **Objectif**: Décrire l'environnement visuel
- **Technologie**: IA de vision (YOLO, CLIP)
- **Détection**:
  - Objets (chaise, table, porte)
  - Personnes (nombre, position)
  - Obstacles (distance, direction)
  - Texte visible
- **Sortie**: Description audio naturelle
- **Mode**: Continu ou à la demande

#### 3.2.2 Identification Couleurs (Priorité 2)
- **Usage**: Vêtements, objets
- **Méthode**: Analyse RGB + IA
- **Sortie**: "Cette chemise est bleue"
- **Précision**: Couleurs principales + nuances

#### 3.2.3 Lecteur de Billets (Priorité 3)
- **Devises**: Euro, Dollar, Dirham
- **Méthode**: OCR + reconnaissance motifs
- **Sortie**: "Billet de 20 euros"
- **Sécurité**: Détection faux billets (futur)

#### 3.2.4 Scanner Code-barres (Priorité 4)
- **Types**: EAN, UPC, QR codes
- **Base données**: Produits alimentaires
- **Sortie**: Nom produit, prix, allergènes
- **Offline**: Cache produits courants

#### 3.2.5 Détecteur Lumière (Priorité 5)
- **Mesure**: Luminosité ambiante
- **Sortie**: "Lumière allumée/éteinte"
- **Usage**: Économie énergie, sécurité

#### 3.2.6 Détection Visages (Priorité 6)
- **Fonction**: Compter personnes
- **Sortie**: "2 personnes devant vous"
- **Distance**: Estimation approximative
- **Confidentialité**: Pas de reconnaissance identité

## 4. Spécifications Techniques Détaillées

### 4.1 API REST Endpoints

#### Capture
- `POST /api/capture` - Scan caméra Pi (avec prévisualisation)
- `POST /api/capture/upload` - Upload photo téléphone

#### Historique
- `GET /api/history` - Liste scans
- `GET /api/history/:id` - Détails scan
- `DELETE /api/history/:id` - Supprimer scan

#### Paramètres
- `GET /api/settings` - Récupérer paramètres
- `POST /api/settings` - Mettre à jour paramètres

#### Traduction
- `POST /api/translate` - Traduire texte

#### Audio
- `GET /api/audio/:filename` - Télécharger fichier audio
- `POST /api/stop` - Arrêter lecture

#### Caméra
- `POST /api/camera/preview/start` - Démarrer prévisualisation
- `POST /api/camera/preview/stop` - Arrêter prévisualisation
- `GET /api/camera/preview/status` - État prévisualisation

#### Santé
- `GET /api/health` - État serveur

### 4.2 Formats de Données

#### ScanResult
```json
{
  "id": "uuid",
  "text": "string",
  "audioUrl": "/api/audio/filename.mp3",
  "timestamp": "ISO8601",
  "language": "french|arabic|english|darija",
  "paragraphCount": 0
}
```

#### Settings
```json
{
  "language": "french|arabic|english|darija",
  "speechRate": 1.0,
  "speechPitch": "low|normal|high",
  "readingMode": "continuous|paragraph|section",
  "audioOutput": "pi-speaker|phone|bluetooth",
  "ocrEngine": "tesseract|cloud"
}
```

### 4.3 Performances

#### Temps de Réponse
- Capture image: < 1s
- OCR (page A4): 2-5s
- TTS génération: 1-3s
- Traduction: 1-2s
- Total scan complet: 5-10s

#### Qualité
- Précision OCR: > 95% (texte imprimé)
- Qualité audio: 128 kbps MP3
- Résolution caméra: 1280x720

## 5. Interface Utilisateur

### 5.1 Principes de Design
- **Audio-first**: Tout contrôlable sans voir écran
- **Feedback haptique**: Vibrations pour confirmations
- **Gros boutons**: Faciles à localiser au toucher
- **Contraste élevé**: Pour malvoyants
- **Navigation simple**: 3 onglets maximum

### 5.2 Écrans Principaux

#### Écran Accueil
- Bouton "Caméra Pi" (grand, bleu)
- Bouton "Caméra Téléphone" (grand, vert)
- Bouton "Commande Vocale" (microphone)
- Indicateur connexion
- Boutons Stop/Repeat

#### Écran Historique
- Liste scans récents
- Lecture au tap
- Suppression par swipe
- Filtres par langue/date

#### Écran Paramètres
- Langue interface
- Vitesse parole
- Sortie audio
- Connexion Pi
- À propos

### 5.3 Accessibilité
- **VoiceOver/TalkBack**: Support complet
- **Labels**: Tous éléments étiquetés
- **Ordre navigation**: Logique
- **Annonces**: Changements d'état vocalisés

## 6. Déploiement

### 6.1 Installation Pi Server

#### Prérequis
- Raspberry Pi 4 (4GB RAM)
- Carte SD 32GB minimum
- Caméra Pi ou USB
- Connexion WiFi

#### Installation
```bash
# Cloner repository
git clone https://github.com/user/smartreader.git
cd smartreader/pi-server

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Configurer
cp config.example.json config.json
nano config.json

# Lancer
python src/main.py
```

### 6.2 Installation Application Mobile

#### Développement
```bash
cd smartreader-mobile-clean
npm install
npx expo start
```

#### Production
```bash
# Android
npx expo run:android

# iOS
npx expo run:ios

# Build EAS
eas build --platform android
```

### 6.3 Configuration Réseau
- **mDNS**: `smartreader.local` ou `eldercare-pi.local`
- **Port**: 5000
- **Firewall**: Autoriser port 5000
- **WiFi**: Même réseau Pi et téléphone

## 7. Tests et Qualité

### 7.1 Tests Unitaires
- Services backend: pytest
- Composants React: Jest
- Couverture cible: > 80%

### 7.2 Tests d'Intégration
- API endpoints: Postman/curl
- Flux complets: Cypress
- Performance: Load testing

### 7.3 Tests Utilisateurs
- Personnes aveugles réelles
- Scénarios d'usage quotidien
- Feedback accessibilité
- Temps d'apprentissage

## 8. Maintenance et Évolution

### 8.1 Maintenance
- Mises à jour sécurité: Mensuelles
- Corrections bugs: Sous 48h (critiques)
- Backup données: Automatique quotidien
- Logs: Rotation 30 jours

### 8.2 Évolution
- Nouvelles langues: Trimestriel
- Nouvelles fonctionnalités: Selon roadmap
- Améliorations IA: Continu
- Optimisations: Selon besoins

## 9. Contraintes et Risques

### 9.1 Contraintes Techniques
- Dépendance réseau WiFi
- Puissance limitée Raspberry Pi
- Qualité caméra variable
- Latence OCR/TTS

### 9.2 Risques
- **Panne réseau**: Mode offline limité
- **Batterie Pi**: Alimentation requise
- **Précision OCR**: Dépend qualité document
- **Vie privée**: Données sensibles

### 9.3 Mitigation
- Cache local pour offline
- Batterie externe Pi
- Prétraitement image amélioré
- Chiffrement données

## 10. Budget et Ressources

### 10.1 Matériel (par unité)
- Raspberry Pi 4 (4GB): 55€
- Caméra Pi: 25€
- Carte SD 32GB: 10€
- Boîtier: 15€
- Alimentation: 10€
- **Total**: ~115€

### 10.2 Logiciel
- Développement: Open source
- APIs: Gratuit (limites usage)
- Hébergement: Local (Pi)
- **Total**: 0€ (hors développement)

### 10.3 Développement
- Backend Python: 40h
- Frontend React Native: 60h
- Tests et debug: 30h
- Documentation: 20h
- **Total**: 150h

## 11. Livrables

### 11.1 Code Source
- Repository Git complet
- Documentation code
- Tests unitaires
- Scripts déploiement

### 11.2 Documentation
- Guide installation
- Guide utilisateur
- Guide développeur
- Cahier des charges (ce document)

### 11.3 Application
- APK Android
- IPA iOS (si applicable)
- Image SD Raspberry Pi
- Fichiers configuration

## 12. Support et Formation

### 12.1 Documentation Utilisateur
- Guide démarrage rapide
- Tutoriels vidéo (audio-décrits)
- FAQ
- Dépannage

### 12.2 Formation
- Session initiale: 2h
- Support téléphonique
- Mises à jour régulières
- Communauté utilisateurs

## 13. Conformité et Légal

### 13.1 Accessibilité
- WCAG 2.1 niveau AA
- Section 508 (US)
- EN 301 549 (EU)

### 13.2 Données Personnelles
- RGPD compliant
- Données locales (Pi)
- Pas de cloud par défaut
- Consentement utilisateur

### 13.3 Licence
- Code: MIT ou GPL
- Documentation: CC BY-SA
- Marque: À définir

## 14. Roadmap

### Phase 1 (Actuelle) - ✅ Complète
- Lecture documents
- Multi-langue
- Commandes vocales
- Historique
- Application mobile

### Phase 2 (Court terme - 3 mois)
- Description scène
- Identification couleurs
- Lecteur billets
- Optimisations performance

### Phase 3 (Moyen terme - 6 mois)
- Scanner code-barres
- Détection visages
- Mode navigation
- Intégration smart home

### Phase 4 (Long terme - 12 mois)
- IA avancée
- Mode hors-ligne complet
- Reconnaissance objets 3D
- Plateforme cloud (optionnel)

---

**Version**: 1.0  
**Date**: 9 Mai 2026  
**Auteur**: Équipe SmartReader  
**Statut**: Document vivant
