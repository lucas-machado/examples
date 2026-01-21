package db

import (
	"clean_architecture/internal/domain"
	"context"
	"database/sql"
	"fmt"
)

type PostgresVideoRepository struct {
	db *sql.DB
}

func NewPostgresVideoRepository(db *sql.DB) domain.VideoRepository {
	return &PostgresVideoRepository{db: db}
}

func (r *PostgresVideoRepository) Save(ctx context.Context, video *domain.Video) error {
	query := `INSERT INTO videos (title, path) VALUES ($1, $2)`

	_, err := r.db.ExecContext(ctx, query, video.Title, video.Path)
	if err != nil {
		return fmt.Errorf("failed to save video: %w", err)
	}

	return nil
}

func (r *PostgresVideoRepository) FindById(ctx context.Context, id string) (*domain.Video, error) {
	// TODO: Implement
	return nil, nil
}
