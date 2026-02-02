package clients

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"sync/atomic"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"go.opentelemetry.io/otel"
)

type ABTestConfig struct {
	Weights map[string]int `json:"weights"`
}

type S3Config struct {
	client        *s3.Client
	s3Bucket      string
	s3Key         string
	logger        *slog.Logger
	currentConfig atomic.Value
}

func NewS3Config(ctx context.Context, bucket, key string, logger *slog.Logger) (*S3Config, error) {
	sdkConfig, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to load default config: %w", err)
	}

	c := &S3Config{
		client:   s3.NewFromConfig(sdkConfig),
		s3Bucket: bucket,
		s3Key:    key,
		logger:   logger,
	}

	if err := c.refresh(ctx); err != nil {
		return nil, fmt.Errorf("failed to refresh config: %w", err)
	}

	go c.start(ctx, 10*time.Second)

	return c, nil
}

func (c *S3Config) GetConfig() ABTestConfig {
	return c.currentConfig.Load().(ABTestConfig)
}

func (c *S3Config) start(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			if err := c.refresh(ctx); err != nil {
				c.logger.Error("failed to refresh config", "error", err)
			}
		}
	}
}

func (c *S3Config) refresh(ctx context.Context) error {
	ctx, span := otel.Tracer("s3-client").Start(ctx, "refresh")
	defer span.End()

	output, err := c.client.GetObject(ctx, &s3.GetObjectInput{
		Bucket: &c.s3Bucket,
		Key:    &c.s3Key,
	})
	if err != nil {
		return fmt.Errorf("failed to get object: %w", err)
	}

	defer output.Body.Close()

	var config ABTestConfig
	if err := json.NewDecoder(output.Body).Decode(&config); err != nil {
		return fmt.Errorf("failed to decode config: %w", err)
	}

	c.currentConfig.Store(config)
	c.logger.Debug("S3 config refreshed", "config", config)

	return nil
}
