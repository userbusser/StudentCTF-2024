package news

import (
	"log/slog"
	"weathery/internal/model"

	"gorm.io/gorm"
)

type Repository struct {
	db *gorm.DB
}

func NewRepository(db *gorm.DB) *Repository {
	return &Repository{db: db}
}

func (p *Repository) All() ([]model.News, error) {
	news := []model.News{}
	err := p.db.Model(&model.News{}).Find(&news).Error
	if err != nil {
		slog.Error(
			"Error getting all news",
			"error", err.Error(),
		)
		return nil, err
	}

	return news, err
}

func (p *Repository) Create(news *model.News) (*model.News, error) {
	err := p.db.Create(&news).Error
	if err != nil {
		slog.Error(
			"Error creating news",
			"error", err.Error(),
		)
		return nil, err
	}

	return news, err
}

func (p *Repository) Migrate() error {
	return p.db.AutoMigrate(&model.News{})
}
