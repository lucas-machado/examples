package main

import (
	"clean_architecture/internal/infrastructure"
	"clean_architecture/internal/infrastructure/db"
	"clean_architecture/internal/infrastructure/notification"
	"clean_architecture/internal/usecase"
	"context"
	"database/sql"
	"log"
	"time"

	_ "github.com/lib/pq"
)

func main() {
	log.Println("Starting API")

	// 1. Abrir conexão com DB
	dbConn, err := sql.Open("postgres", "postgres://user:pass@localhost:5432/db?sslmode=disable")
	if err != nil {
		log.Fatalf("failed to open database connection: %v", err)
	}
	defer dbConn.Close()

	// Test the connection
	if err := dbConn.Ping(); err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	notifier := notification.NewPushNotifier("api_key")
	repo := db.NewPostgresVideoRepository(dbConn)
	bridge := infrastructure.NewVideoProcessorBridge(notifier, repo)

	usecase := usecase.NewProcessVideoUsecase(bridge)

	ctx, cancel := context.WithTimeout(context.Background(), 6*time.Second)
	defer cancel()

	if err := usecase.Execute(ctx, "Test", "test.mp4"); err != nil {
		log.Fatalf("failed to process video: %v", err)
	}
}
