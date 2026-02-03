package main

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"inference_gateway/internal/clients"
	"inference_gateway/internal/config"
	"inference_gateway/internal/server"
	"inference_gateway/internal/telemetry"
)

func main() {
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	slog.SetDefault(logger)

	cfg, err := config.Load()
	if err != nil {
		logger.Error("failed to load config", "error", err)
		os.Exit(1)
	}

	appCtx, appCancel := context.WithCancel(context.Background())
	defer appCancel()

	shutdownOTEL, err := telemetry.SetupOTEL(appCtx, cfg, logger)
	if err != nil {
		logger.Error("failed to setup otel", "error", err)
		os.Exit(1)
	}
	defer func() {
		if err := shutdownOTEL(context.Background()); err != nil {
			logger.Error("failed to shutdown otel", "error", err)
		}
	}()

	abConfig, err := clients.NewS3Config(appCtx, cfg.S3Bucket, cfg.S3ConfigKey, logger)
	if err != nil {
		logger.Error("failed to create s3 config", "error", err)
		os.Exit(1)
	}

	tinybirdClient := clients.NewTinybirdClient(cfg.TinybirdURL, cfg.TinybirdKey, logger)
	modelClient := clients.NewModelClient(cfg.ModelBaseURL)

	handler := server.NewHandler(appCtx, logger, abConfig, tinybirdClient, modelClient)

	srv := &http.Server{
		Addr:         fmt.Sprintf(":%s", cfg.Port),
		Handler:      handler,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  10 * time.Second,
	}

	go func() {
		logger.Info("starting server", "port", cfg.Port, "env", cfg.Env)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logger.Error("failed to start server", "error", err)
			os.Exit(1)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("shutting down server")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("server forced to shutdown", "error", err)
	}

	appCancel()

	logger.Info("server shutdown complete")
}
