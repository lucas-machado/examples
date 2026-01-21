package infrastructure

import "clean_architecture/internal/domain"

type VideoProcessorBridge struct {
	domain.Notifier
	domain.VideoRepository
}

func NewVideoProcessorBridge(notifier domain.Notifier, videoRepository domain.VideoRepository) *VideoProcessorBridge {
	return &VideoProcessorBridge{Notifier: notifier, VideoRepository: videoRepository}
}
