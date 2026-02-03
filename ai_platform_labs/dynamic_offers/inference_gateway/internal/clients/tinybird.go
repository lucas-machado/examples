package clients

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"net/url"
	"time"
)

type Features map[string]any

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

func (c *TinybirdClient) GetFeatures(ctx context.Context, gameID, userID string) (Features, error) {
	// Defina o nome do seu Pipe aqui.
	// O Pipe deve aceitar um parametro 'user_id' e 'game_id'.
	pipeName := "user_features"

	endpoint := fmt.Sprintf("%s/v0/pipes/%s.json", c.host, pipeName)
	u, err := url.Parse(endpoint)
	if err != nil {
		return nil, fmt.Errorf("failed to parse url: %w", err)
	}

	q := u.Query()
	q.Set("user_id", userID)
	q.Set("game_id", gameID)
	u.RawQuery = q.Encode()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.token))

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("tinybird api error: status=%d", resp.StatusCode)
	}

	var tbResp struct {
		Data []Features `json:"data"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&tbResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	if len(tbResp.Data) == 0 {
		// Retorna mapa vazio se não encontrar features para o usuário
		return Features{}, nil
	}

	return tbResp.Data[0], nil
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
