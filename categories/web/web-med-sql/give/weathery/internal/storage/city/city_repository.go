package city

import (
	"context"
	"fmt"
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

func (p *Repository) FindByCityName(cityname string) (*model.City, error) {
	city := new(model.City)
	err := p.db.Where("cityname = ?", cityname).First(&city).Error
	return city, err
}

func (p *Repository) Create(city *model.City) (*model.City, error) {
	err := p.db.Save(&city).Error
	if err != nil {
		slog.Error(
			"Error creating city",
			"error", err.Error(),
		)
		return nil, err
	}
	return city, err
}

func (p *Repository) SelectDegreesByCityName(cityname interface{}) (int, error) {
	var degrees int
	err := p.db.Table("cities").Select("degrees").Where("cityname = ?", cityname).Scan(&degrees).Error
	if err != nil {
		slog.Error(
			"Error select degrees by cityname",
			"error", err.Error(),
		)
		return 0, err
	}
	return degrees, err
}

func (p *Repository) UpdateCitycodeQuery(ctx context.Context, citycode, cityname interface{}) error {
	query := fmt.Sprintf("UPDATE cities SET citycode = '%s' \n", citycode)
	query = query + "WHERE cityname = ?"
	err := p.db.WithContext(ctx).Exec(query, cityname).Error
	return err
}

func (p *Repository) UpdateDegreesQuery(ctx context.Context, degrees, cityname interface{}) error {
	query := fmt.Sprintf("UPDATE cities SET degrees = %d \n", degrees)
	query = query + "WHERE cityname = ?"
	err := p.db.WithContext(ctx).Exec(query, cityname).Error
	return err
}

func (p *Repository) Migrate() error {
	return p.db.AutoMigrate(&model.City{})
}
