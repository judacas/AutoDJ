# Database Setup Notes

## Local PostgreSQL Setup

### Prerequisites
- PostgreSQL installed locally
- Access to postgres superuser password via `$Env:PGSU_PASSWORD` environment variable

### Setup Commands
```bash
# Create the database
psql "host=localhost port=5432 dbname=postgres user=postgres password=$Env:PGSU_PASSWORD" -c "CREATE DATABASE autodj;"

# Create the application user
psql "host=localhost port=5432 dbname=postgres user=postgres password=$Env:PGSU_PASSWORD" -c "CREATE USER autodj WITH PASSWORD '{{AUTODJ_DB_PASSWORD}}';"

# Make autodj the owner of the database
psql "host=localhost port=5432 dbname=postgres user=postgres password=$Env:PGSU_PASSWORD" -c "ALTER DATABASE autodj OWNER TO autodj;"
```

### Why This Works Locally
- Direct access to PostgreSQL server
- Full control over user creation and permissions
- Can use superuser privileges to grant ownership
- Environment variables accessible for password management

## Azure Managed PostgreSQL Setup

### Key Differences from Local Setup

#### 1. **No Direct Superuser Access**
- Azure PostgreSQL doesn't provide superuser access
- Cannot run `ALTER DATABASE autodj OWNER TO autodj`
- Must use Azure-specific permission management

#### 2. **Azure CLI/Portal Management**
Instead of direct psql commands, you'd use:

```bash
# Create database (via Azure CLI)
az postgres db create --resource-group <resource-group> --server-name <server-name> --name autodj

# Create user (via Azure CLI) 
az postgres server ad-admin create --resource-group <resource-group> --server-name <server-name> --display-name autodj --object-id <object-id>

# Or via Azure Portal: Server → Connection security → Azure Active Directory authentication
```

#### 3. **Permission Management**
```sql
-- Connect as the server admin user (not superuser)
-- Grant permissions instead of changing ownership
GRANT ALL PRIVILEGES ON DATABASE autodj TO autodj;
GRANT ALL PRIVILEGES ON SCHEMA public TO autodj;
GRANT CREATE ON SCHEMA public TO autodj;
GRANT USAGE ON SCHEMA public TO autodj;
```

#### 4. **Connection String Changes**
- Local: `postgresql+psycopg2://autodj:password@localhost:5432/autodj`
- Azure: `postgresql+psycopg2://autodj:password@<server-name>.postgres.database.azure.com:5432/autodj?sslmode=require`

#### 5. **Container Deployment Considerations**
For containerized deployment:

```yaml
# docker-compose.yml or Kubernetes config
environment:
  - AUTODJ_DATABASE_URL=postgresql+psycopg2://autodj:${AUTODJ_DB_PASSWORD}@<azure-server>.postgres.database.azure.com:5432/autodj?sslmode=require
```

### Azure Setup Steps Summary
1. **Create Azure PostgreSQL server** (via Portal/CLI)
2. **Create database** `autodj` (via Portal/CLI)
3. **Create application user** `autodj` (via Portal/CLI)
4. **Grant permissions** (via psql connection to Azure server)
5. **Configure firewall rules** for your application's IP
6. **Update connection string** with Azure server details
7. **Enable SSL** (required for Azure)

### Key Takeaway
Local setup gives you full control with superuser privileges, while Azure managed services require using Azure's permission model and cannot grant database ownership to non-admin users.
