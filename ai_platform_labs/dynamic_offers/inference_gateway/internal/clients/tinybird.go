package clients

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"time"
)

type TinybirdClient struct {
	httpClient *http.Client
	host       string
	token      string
	logger     *slog.Logger
}

func NewTinybirdClient(host, token string, logger *slog.Logger) *TinybirdClient {
	return &TinybirdClient{
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		host:   host,
		token:  token,
		logger: logger,
	}
}

func (c *TinybirdClient) Ingest(ctx context.Context, dataSource string, payload any) error {
	url := fmt.Sprintf("%s/v0/events?name=%s", c.host, dataSource)

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.token))
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to ingest data: %s", resp.Status)
	}

	return nil
}
