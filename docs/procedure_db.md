# Procédure : Redémarrage de la base PostgreSQL

## Contexte

Cette procédure s'applique aux serveurs PostgreSQL de production et de pré-production hébergés sur les VMs `db-prod-01` et `db-preprod-01`.

## Prérequis

- Accès SSH avec le compte `dsi-ops`
- Droits sudo sur le serveur cible
- Validation du changement via le ticket ServiceNow (catégorie : Infrastructure > Bases de données)

## Étapes

1. Se connecter au serveur :
   ```bash
   ssh dsi-ops@db-prod-01.internal
   ```

2. Vérifier l'état actuel du service :
   ```bash
   sudo systemctl status postgresql
   ```

3. Arrêter proprement PostgreSQL :
   ```bash
   sudo systemctl stop postgresql
   ```

4. Attendre 30 secondes, puis redémarrer :
   ```bash
   sudo systemctl start postgresql
   ```

5. Vérifier que le service est actif :
   ```bash
   sudo systemctl is-active postgresql
   ```

6. Contrôler les connexions applicatives :
   ```bash
   sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
   ```

## En cas d'échec

- Consulter les logs : `/var/log/postgresql/postgresql-15-main.log`
- Escalader au DBA de garde via PagerDuty (équipe `database-oncall`)
- Ne jamais forcer un `kill -9` sur le processus postgres sans accord du DBA

## Fenêtre de maintenance

Les redémarrages planifiés doivent être effectués entre **02h00 et 05h00 UTC**, sauf urgence validée par le RSSI.
