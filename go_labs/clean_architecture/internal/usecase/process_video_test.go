package usecase

import (
	"clean_architecture/internal/domain"
	"context"
	"errors"
	"log"
	"testing"
)

type MockProcessor struct {
	SaveCalled     bool
	FindByIdCalled bool
	NotifyCalled   bool
	ReturnError    error
}

func (m *MockProcessor) Save(ctx context.Context, video *domain.Video) error {
	m.SaveCalled = true
	return m.ReturnError
}

func (m *MockProcessor) FindById(ctx context.Context, id string) (*domain.Video, error) {
	m.FindByIdCalled = true
	return nil, m.ReturnError
}

func (m *MockProcessor) Notify(ctx context.Context, message string) error {
	m.NotifyCalled = true
	return m.ReturnError
}

func TestProcessVideoUsecase_Execute_FlowControl(t *testing.T) {
	dbError := errors.New("database error")
	mock := MockProcessor{ReturnError: dbError}
	uc := NewProcessVideoUsecase(&mock)

	log.Println("INFO: Executing process video usecase")
	err := uc.Execute(context.Background(), "test", "test")

	if err == nil {
		t.Errorf("Expected error, got nil")
	}

	if !mock.SaveCalled {
		t.Errorf("Expected save method to be called, but it was not")
	}

	if mock.NotifyCalled {
		t.Errorf("Expected notify method to not be called, but it was")
	} else {
		t.Log("SUCCESS: Notify method was called as expected")
	}
}

func TestProcessVideoUsecase_Execute_TableNotFound(t *testing.T) {
	tests := []struct {
		name               string
		mockError          error
		expectNotifyCalled bool
		expectError        bool
	}{
		{
			name:               "full success flow",
			mockError:          nil,
			expectNotifyCalled: true,
			expectError:        false,
		},
		{
			name:               "save error",
			mockError:          errors.New("save error"),
			expectNotifyCalled: false,
			expectError:        true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			mock := MockProcessor{ReturnError: test.mockError}
			uc := NewProcessVideoUsecase(&mock)
			err := uc.Execute(context.Background(), "test", "test")

			if (err != nil) != test.expectError {
				t.Errorf("Expected error: %v, got: %v", test.expectError, err)
			}

			if mock.NotifyCalled != test.expectNotifyCalled {
				t.Errorf("Expected notify method to be called: %v, got: %v", test.expectNotifyCalled, mock.NotifyCalled)
			}
		})
	}
}
