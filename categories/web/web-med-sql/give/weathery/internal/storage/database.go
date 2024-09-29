package storage

import (
	"fmt"
	"weathery/internal/config"
	"weathery/internal/storage/auth"
	"weathery/internal/storage/city"
	"weathery/internal/storage/news"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type Database struct {
	db *gorm.DB

	city CityRepository
	auth AuthRepository
	news NewsRepository
}

func DBConn(cfg *config.DatabaseConfiguration) (*gorm.DB, error) {
	var db *gorm.DB
	var err error

	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=%s", cfg.Host, cfg.Username, cfg.Password, cfg.Name, cfg.Port, cfg.SSLMode)

	db, err = gorm.Open(postgres.Open(dsn))
	if err != nil {
		return nil, fmt.Errorf("could not open postgresql connection: %v", err)
	}

	return db, err
}

func New(db *gorm.DB) *Database {
	return &Database{
		db:   db,
		city: city.NewRepository(db),
		auth: auth.NewRepository(db),
		news: news.NewRepository(db),
	}
}

func (db *Database) City() CityRepository {
	return db.city
}

func (db *Database) Auth() AuthRepository {
	return db.auth
}

func (db *Database) News() NewsRepository {
	return db.news
}
