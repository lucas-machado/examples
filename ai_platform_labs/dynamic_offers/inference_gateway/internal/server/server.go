package server

import (
	"context"
	"encoding/json"
	"log/slog"
	"math/rand"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"

	"inference_gateway/internal/clients"
)

type Handler struct {
	logger         *slog.Logger
	abConfig       *clients.S3Config
	tinybirdClient *clients.TinybirdClient
	modelClient    *clients.ModelClient
	router         chi.Router
}

func NewHandler(ctx context.Context, logger *slog.Logger, abConfig *clients.S3Config, tinybirdClient *clients.TinybirdClient, modelClient *clients.ModelClient) http.Handler {
	h := &Handler{
		logger:         logger,
		abConfig:       abConfig,
		tinybirdClient: tinybirdClient,
		modelClient:    modelClient,
	}

	r := chi.NewRouter()

	// Middlewares básicos
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(60 * time.Second))

	// Rotas
	r.Get("/health", h.handleHealth)
	r.Post("/predict", h.handlePredict)

	h.router = r
	return h
}

func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	h.router.ServeHTTP(w, r)
}

func (h *Handler) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

type PredictRequest struct {
	GameID string `json:"game_id"`
	UserID string `json:"user_id"`
}

func (h *Handler) handlePredict(w http.ResponseWriter, r *http.Request) {
	var req PredictRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.logger.Error("failed to decode request", "error", err)
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}

	if req.GameID == "" || req.UserID == "" {
		http.Error(w, "game_id and user_id are required", http.StatusBadRequest)
		return
	}

	// 1. Obter Features do Tinybird
	features, err := h.tinybirdClient.GetFeatures(r.Context(), req.GameID, req.UserID)
	if err != nil {
		h.logger.Error("failed to get features", "error", err, "user_id", req.UserID)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	// 2. Selecionar Modelo (A/B Test)
	modelName := h.selectModel()
	h.logger.Info("model selected", "model", modelName, "user_id", req.UserID)

	// 3. Chamar Modelo de Inferência
	prediction, err := h.modelClient.Recommend(r.Context(), modelName, features)
	if err != nil {
		h.logger.Error("failed to get recommendation", "error", err, "model", modelName)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	// 4. Retornar Resposta
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(prediction); err != nil {
		h.logger.Error("failed to encode response", "error", err)
	}
}

// selectModel escolhe um modelo aleatoriamente baseado nos pesos configurados
func (h *Handler) selectModel() string {
	config := h.abConfig.GetConfig()
	if len(config.Weights) == 0 {
		return "training"
	}

	// Lógica simples de Weighted Random Choice
	totalWeight := 0
	for _, w := range config.Weights {
		totalWeight += w
	}

	r := rand.Intn(totalWeight)
	current := 0
	for model, w := range config.Weights {
		current += w
		if r < current {
			return model
		}
	}

	// Fallback (não deve acontecer se a lógica acima estiver correta)
	for model := range config.Weights {
		return model
	}
	return "training"
}
