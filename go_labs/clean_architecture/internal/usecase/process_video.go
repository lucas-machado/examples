package usecase

import (
	"clean_architecture/internal/domain"
	"context"
	"fmt"
)

type ProcessVideoUsecase struct {
	Processor VideoProcessor
}

func NewProcessVideoUsecase(processor VideoProcessor) *ProcessVideoUsecase {
	return &ProcessVideoUsecase{Processor: processor}
}

func (u *ProcessVideoUsecase) Execute(ctx context.Context, title string, path string) error {
	video := &domain.Video{
		Title: title,
		Path:  path,
	}

	if err := u.Processor.Save(ctx, video); err != nil {
		return err
	}

	if err := u.Processor.Notify(ctx, fmt.Sprintf("Processing video: %s", video.Title)); err != nil {
		return err
	}

	return nil
}
