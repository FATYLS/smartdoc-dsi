# Procédure : Déblocage d'un accès VPN

## Contexte

Les collaborateurs accèdent au réseau interne via le VPN **FortiClient** (profil `DSI-CORP`). Un accès bloqué peut résulter d'un mot de passe expiré, d'un certificat révoqué ou d'une suspension automatique après 3 tentatives échouées.

## Diagnostic initial

1. Vérifier l'identifiant Active Directory de l'utilisateur
2. Consulter le statut du compte dans l'AD (`dsquery user`)
3. Vérifier les logs FortiGate : `Log & Report > VPN Events`

## Déblocage standard (compte verrouillé)

1. Ouvrir le ticket ServiceNow avec la catégorie **Réseau > VPN**
2. Déverrouiller le compte AD :
   ```powershell
   Unlock-ADAccount -Identity prenom.nom
   ```
3. Demander à l'utilisateur de réinitialiser son mot de passe via le portail SSO
4. Tester la connexion VPN avec le profil `DSI-CORP`

## Déblocage certificat expiré

1. Révoquer l'ancien certificat dans la CA interne
2. Générer un nouveau certificat via le portail `https://pki.dsi.internal`
3. Réinstaller le profil FortiClient avec le nouveau certificat

## Cas nécessitant une validation RSSI

- Accès depuis une IP non reconnue (géolocalisation inhabituelle)
- Demande de déblocage en dehors des heures ouvrées sans astreinte
- Compte appartenant à un profil à accès restreint (DBA, admin infra)

Dans ces cas, obtenir l'accord écrit du RSSI avant toute action.

## SLA

- Déblocage standard : **2 heures ouvrées**
- Urgent (astreinte) : **30 minutes**

Contact astreinte réseau : `network-oncall@dsi.internal` ou +33 1 00 00 00 01
