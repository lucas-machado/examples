package server

import (
	"context"
	"inference_gateway/internal/clients"
	"log/slog"
	"net/http"
)

type Handler struct {
	logger   *slog.Logger
	abConfig *clients.S3Config
}

func NewHandler(ctx context.Context, logger *slog.Logger, abConfig *clients.S3Config) http.Handler {
	return nil
}
