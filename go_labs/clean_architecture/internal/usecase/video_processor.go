package usecase

import "clean_architecture/internal/domain"

type VideoProcessor interface {
	domain.Notifier
	domain.VideoRepository
}
