package clients

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type RecommendationResponse struct {
	RecommendationID string `json:"recommendation_id"`
}

type ModelClient struct {
	httpClient *http.Client
	baseURL    string
}

func NewModelClient(baseURL string) *ModelClient {
	return &ModelClient{
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		baseURL: baseURL,
	}
}

func (m *ModelClient) Recommend(ctx context.Context, model string, features Features) (*RecommendationResponse, error) {
	url := fmt.Sprintf("%s/%s/recommend", m.baseURL, model)

	body, err := json.Marshal(features)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal features: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := m.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to recommend: %s", resp.Status)
	}

	var recommendationResponse RecommendationResponse
	if err := json.NewDecoder(resp.Body).Decode(&recommendationResponse); err != nil {
		return nil, fmt.Errorf("failed to decode recommendation response: %w", err)
	}

	return &recommendationResponse, nil
}
