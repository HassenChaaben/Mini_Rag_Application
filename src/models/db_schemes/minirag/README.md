## Run Alembic Migrations 

### Configurations 

```bash
cp alembic.ini.example alembic.ini
```
- update the `alembic.ini` with your database credentials (`sqlalchemy.url`) 

### (Optional) Create new migration

```bash
alembic revision --autogenerate -m "your_message"
```

### Upgrade the database
 
```bash
alembic upgrade head
```