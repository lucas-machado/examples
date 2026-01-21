.PHONY: db-up db-down db-logs db-status db-connect run clean

# Start PostgreSQL database
db-up:
	docker-compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 5

# Stop PostgreSQL database
db-down:
	docker-compose down

# Show database logs
db-logs:
	docker-compose logs -f postgres

# Check database status
db-status:
	docker-compose ps

# Connect to database with psql
db-connect:
	PGPASSWORD=pass psql -h localhost -p 5432 -U user -d db

# Run the application
run:
	go run cmd/api/main.go

# Clean up (stop and remove volumes)
clean:
	docker-compose down -v

# Full setup: start DB, wait, then run app
setup: db-up
	@echo "Database is ready! Now run 'make run' to start the application."