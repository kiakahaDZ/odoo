# Docker Setup for Odoo Clinic System

This guide will help you run your Odoo clinic system using Docker containers, eliminating the need for manual setup on your machine.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Quick Start

1. **Clone or navigate to your project directory**
   ```bash
   cd /path/to/your/odoo/project
   ```

2. **Build and start the containers**
   ```bash
   docker-compose up --build -d
   ```

3. **Wait for initialization**
   ```bash
   docker-compose ps
   ```

4. **Access Odoo**
   - Open your browser and navigate to: `http://localhost:8069`
   - Use the default admin credentials:
     - Username: `admin`
     - Password: `admin`

## Configuration

### Environment Variables

The system uses environment variables defined in the `.env` file:

- `DB_HOST`: Database host (default: `db`)
- `DB_PORT`: Database port (default: `5432`)
- `DB_USER`: Database username (default: `odoo`)
- `DB_PASSWORD`: Database password (default: `987654321aA`)
- `DB_NAME`: Database name (default: `odoo_clean`)
- `ODOO_ADMIN_PASSWORD`: Odoo admin password (default: `admin`)
- `ODOO_HTTP_PORT`: Odoo HTTP port (default: `8069`)

### Customization

To modify the configuration:

1. Edit the `.env` file to change environment variables
2. Edit `odoo.conf` for Odoo-specific settings
3. Edit `docker-compose.yml` for service configurations

## Available Services

### Database Service (`db`)
- PostgreSQL 15 database
- Automatically configured with environment variables
- Data persists in Docker volume

### Odoo Service (`odoo`)
- Odoo 17.0 application
- Connected to the database service
- Custom modules from `addons/` directory
- Data persists in Docker volume

## Commands

### Start the system
```bash
docker-compose up -d
```

### Stop the system
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### View status
```bash
docker-compose ps
```

### Restart services
```bash
docker-compose restart
```

### Remove containers and volumes
```bash
docker-compose down -v
```

## Development

### Adding Custom Modules

1. Place your custom modules in the `addons/` directory
2. The Docker build process will automatically include them
3. Restart the Odoo service after adding new modules

### Debug Mode

To run Odoo in debug mode:

1. Edit the `docker-compose.yml` file
2. Add the following to the odoo service environment:
   ```yaml
   environment:
     - DEBUG=1
   ```

### Access Shell

To access the Odoo container shell:

```bash
docker-compose exec odoo bash
```

## Data Persistence

- Database data is stored in the `postgres_data` Docker volume
- Odoo filestore and configuration are stored in the `odoo_data` Docker volume
- These volumes persist even when containers are removed and recreated

## Troubleshooting

### Database Connection Issues

1. Check if the database container is running:
   ```bash
   docker-compose ps db
   ```

2. View database logs:
   ```bash
   docker-compose logs db
   ```

3. Ensure the database has enough time to initialize before Odoo starts

### Port Conflicts

If port 8069 is already in use:

1. Change the port in `.env`:
   ```
   ODOO_HTTP_PORT=8070
   ```

2. Update the port mapping in `docker-compose.yml`:
   ```yaml
   ports:
     - "8070:8069"
   ```

### Module Installation Issues

1. Check Odoo logs:
   ```bash
   docker-compose logs odoo
   ```

2. Verify module syntax and dependencies
3. Ensure proper file permissions in the `addons/` directory

## Backup and Restore

### Backup

1. Backup the database:
   ```bash
   docker-compose exec db pg_dump -U odoo odoo_clean > backup.sql
   ```

2. Backup the filestore:
   ```bash
   docker cp odoo:/var/lib/odoo/filestore ./filestore_backup
   ```

### Restore

1. Stop the services:
   ```bash
   docker-compose down
   ```

2. Restore the database:
   ```bash
   docker-compose exec -T db psql -U odoo odoo_clean < backup.sql
   ```

3. Restore the filestore:
   ```bash
   docker cp ./filestore_backup odoo:/var/lib/odoo/filestore
   ```

4. Start the services:
   ```bash
   docker-compose up -d
   ```

## Performance Optimization

### Resource Limits

Edit `docker-compose.yml` to add resource limits:

```yaml
services:
  db:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
  odoo:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

### Caching

Add caching layers for better performance:

```yaml
services:
  odoo:
    volumes:
      - ./cache:/tmp/cache
```

## Security

### Change Default Passwords

1. Update the `ODOO_ADMIN_PASSWORD` in `.env`
2. Update the `admin_passwd` in `odoo.conf`
3. Rebuild and restart the containers

### Network Security

For production use, consider:

1. Using a reverse proxy (nginx, traefik)
2. Enabling SSL/TLS
3. Restricting database access
4. Using environment-specific configurations

## Support

For issues related to:

- **Docker setup**: Check Docker and Docker Compose documentation
- **Odoo functionality**: Check Odoo documentation
- **Custom modules**: Review module code and dependencies

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all services in background |
| `docker-compose down` | Stop all services |
| `docker-compose logs -f` | Follow logs |
| `docker-compose ps` | Show service status |
| `docker-compose exec odoo bash` | Access Odoo container shell |