package storage

import "log/slog"

func MigrateTables(s Store) {
	if err := s.City().Migrate(); err != nil {
		slog.Error(
			"failed to migrate city",
			"error", err.Error(),
		)
	}
	if err := s.News().Migrate(); err != nil {
		slog.Error(
			"failed to migrate news",
			"error", err.Error(),
		)
	}
}
