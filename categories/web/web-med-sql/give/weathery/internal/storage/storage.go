package storage

type Store interface {
	City() CityRepository
	Auth() AuthRepository
	News() NewsRepository
}
