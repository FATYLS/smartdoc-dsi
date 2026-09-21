# Politique de sécurité DSI — Mots de passe et clés API

## Mots de passe

### Exigences minimales

- Longueur minimum : **14 caractères**
- Composition : majuscules, minuscules, chiffres et au moins un caractère spécial
- Interdiction de réutiliser les **5 derniers mots de passe**
- Rotation obligatoire tous les **90 jours** pour les comptes privilégiés

### Comptes privilégiés

Les comptes admin (root, dsi-ops, db-admin) doivent utiliser une authentification MFA (YubiKey ou TOTP via Duo).

### Stockage

- Interdiction de stocker les mots de passe en clair dans un fichier, un ticket ou un chat
- Utiliser le coffre-fort **HashiCorp Vault** (namespace `dsi-prod`) pour tout secret partagé

## Clés API

### Création

1. Créer une demande dans ServiceNow (type : Accès > Clé API)
2. Définir un périmètre minimal (principe du moindre privilège)
3. Associer la clé à un owner nominatif et une date d'expiration (max **180 jours**)

### Rotation et révocation

- Rotation automatique à J-15 via le pipeline CI `api-key-rotation`
- Révocation immédiate en cas de fuite suspectée : contacter `security@dsi.internal`
- Journaliser toute utilisation dans Splunk (index `api-audit`)

### Bonnes pratiques

- Ne jamais committer de clé API dans Git (scan automatique via GitLeaks)
- Utiliser des variables d'environnement ou Vault pour l'injection en runtime
- Préférer OAuth2 / tokens courts aux clés statiques longue durée

## Incident de sécurité

En cas de compromission avérée :

1. Révoquer immédiatement les credentials concernés
2. Ouvrir un incident P1 dans ServiceNow
3. Prévenir le RSSI et l'équipe SOC dans les **15 minutes**
