package config

import (
	"fmt"

	"github.com/knadh/koanf/providers/env"
	"github.com/knadh/koanf/v2"
)

type Config struct {
	Port         string `koanf:"PORT"`
	Env          string `koanf:"ENV"`
	ModelBaseURL string `koanf:"MODEL_BASE_URL"`
	TinybirdURL  string `koanf:"TINYBIRD_URL"`
	TinybirdKey  string `koanf:"TINYBIRD_KEY"`
	S3Bucket     string `koanf:"S3_BUCKET"`
	S3ConfigKey  string `koanf:"S3_CONFIG_KEY"`
}

func Load() (*Config, error) {
	k := koanf.New(".")

	err := k.Load(env.Provider("", ".", func(s string) string {
		return s
	}), nil)

	if err != nil {
		return nil, fmt.Errorf("failed to load config: %w", err)
	}

	var cfg Config
	if err := k.Unmarshal("", &cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	if cfg.Port == "" {
		cfg.Port = "8080"
	}

	return &cfg, nil
}
