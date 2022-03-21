### Initial conditions

1. Project's database (postgres-data dir) is not empty. You can run test_api for adding new data to database. 
2. You're in "separated-bot-schema-pakhomov" branch and in .../pp_telegram_bot directory. 

### Run applications
```
docker-compose -f docker-compose.dev.yml up --build
```
### Connect to a bot container and run migration
```
docker exec -it telegram_bot_dev bash
alembic upgrade head
```
### Connect to database using password: picpack123_iu_dev
```
psql -U picpack_iu_dev -h localhost -p 35432 -d picpack_iu_dev
```
### Check new tables in backend schema
```
\dt bot.*
```
### Create a database backup file using the password
```
cd scripts
pg_dump -U picpack_iu_dev -h localhost -p 35432 -d picpack_iu_dev > database_backup.dump
```
### Run data migration script using the password
```
psql -U picpack_iu_dev -h localhost -p 35432 -d picpack_iu_dev -f data_copy_query.sql
```

### If you got any errors in previous step run
```
psql -U picpack_iu_dev -h localhost -p 35432 -d picpack_iu_dev < database_backup.dump 
```

### Check data in new tables or run the tests