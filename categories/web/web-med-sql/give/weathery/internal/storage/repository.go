package storage

import (
	"context"
	"weathery/internal/model"
)

type CityRepository interface {
	FindByCityName(cityname string) (*model.City, error)
	Create(*model.City) (*model.City, error)
	SelectDegreesByCityName(cityname interface{}) (int, error)
	UpdateCitycodeQuery(ctx context.Context, cityname, citycode interface{}) error
	UpdateDegreesQuery(ctx context.Context, cityname, degrees interface{}) error
	Migrate() error
}

type AuthRepository interface {
}

type NewsRepository interface {
	All() ([]model.News, error)
	Create(news *model.News) (*model.News, error)
	Migrate() error
}
