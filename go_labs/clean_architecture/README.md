# Clean Architecture Go Project

This project demonstrates clean architecture principles in Go with PostgreSQL.

## Setup

1. **Start the PostgreSQL database:**
   ```bash
   make db-up
   ```

2. **Run the application:**
   ```bash
   make run
   ```

## Available Commands

- `make db-up` - Start PostgreSQL database
- `make db-down` - Stop PostgreSQL database
- `make db-logs` - View database logs
- `make db-status` - Check database status
- `make db-connect` - Connect to database with psql
- `make run` - Run the application
- `make clean` - Stop and remove database volumes
- `make setup` - Start database and wait for it to be ready

## Database Configuration

- **Host:** localhost:5432
- **Database:** db
- **User:** user
- **Password:** pass

The database schema is automatically created when the container starts up.