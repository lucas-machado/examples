package domain

import "context"

type VideoRepository interface {
	Save(ctx context.Context, video *Video) error
	FindById(ctx context.Context, id string) (*Video, error)
}
