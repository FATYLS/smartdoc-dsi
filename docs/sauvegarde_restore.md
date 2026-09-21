# Procédure : Sauvegarde et restauration des données

## Politique de sauvegarde

| Système        | Fréquence      | Rétention | Emplacement        |
|----------------|----------------|-----------|--------------------|
| PostgreSQL     | Quotidienne    | 30 jours  | S3 `dsi-backups-db` |
| Fichiers partagés | Hebdomadaire | 90 jours  | NAS `backup-nas-01` |
| Configurations | Quotidienne    | 365 jours | Git + Vault        |

## Restauration PostgreSQL (point-in-time)

1. Identifier le timestamp cible dans le ticket d'incident
2. Récupérer le dump depuis S3 :
   ```bash
   aws s3 cp s3://dsi-backups-db/postgresql/YYYY-MM-DD/ ./restore/
   ```
3. Créer une instance de restauration sur `db-restore-01` (jamais en prod directe)
4. Restaurer :
   ```bash
   pg_restore -d postgres_restore -U postgres backup.dump
   ```
5. Valider l'intégrité avec l'équipe métier avant bascule

## Tests de restauration

- Test complet obligatoire **chaque trimestre**
- Résultat documenté dans Confluence (espace `DSI-DR`)
- Alerte si le test échoue deux trimestres consécutifs

## Contacts

- Équipe backup : `backup@dsi.internal`
- DBA de garde : PagerDuty `database-oncall`
