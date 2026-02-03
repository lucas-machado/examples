package server

import (
	"context"
	"inference_gateway/internal/clients"
	"log/slog"
	"net/http"
)

type Handler struct {
	logger         *slog.Logger
	abConfig       *clients.S3Config
	tinybirdClient *clients.TinybirdClient
	modelClient    *clients.ModelClient
}

func NewHandler(ctx context.Context, logger *slog.Logger, abConfig *clients.S3Config, tinybirdClient *clients.TinybirdClient, modelClient *clients.ModelClient) http.Handler {
	return Handler{
		logger:         logger,
		abConfig:       abConfig,
		tinybirdClient: tinybirdClient,
		modelClient:    modelClient,
	}
}

func (h Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	h.logger.Info("serving request", "method", r.Method, "path", r.URL.Path)
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Hello, World!"))
}
