package notification

import (
	"clean_architecture/internal/domain"
	"context"
)

type PushNotifier struct {
	APIKey string
}

func NewPushNotifier(apiKey string) domain.Notifier {
	return &PushNotifier{APIKey: apiKey}
}

func (n *PushNotifier) Notify(ctx context.Context, message string) error {
	// TODO: Implement
	return nil
}
