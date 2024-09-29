package main

import (
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"path/filepath"
	"weathery/internal/app/middlewares"
	"weathery/internal/app/services"
	"weathery/internal/config"
	"weathery/internal/constants"
	"weathery/internal/storage"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func main() {

	if err := os.Chdir(filepath.Dir(appFilePath())); err != nil {
		mustInitWithoutLogger(fmt.Errorf("failed to set working directory: %w", err))
	}

	cfg, err := config.Init(constants.ConfigPath, constants.ConfigName)
	if err != nil {
		mustInitWithoutLogger(fmt.Errorf("failed to init config: %w", err))
	}


	db, err := storage.DBConn(cfg.Database)
	if err != nil {
		mustInit(fmt.Errorf("failed to init db: %w", err))
	}

	s := storage.New(db)

	storage.MigrateTables(s)

	err = executeInitScript(db, "./db/init.sql")
	if err != nil {
		mustInit(fmt.Errorf("failed to run init.sql: %w", err))
	}

	srv := services.NewService(s)

	r := gin.Default()

	store := cookie.NewStore([]byte(cfg.App.Secretkey))
	r.Use(sessions.Sessions("session", store))

	r.LoadHTMLGlob("./templates/*.html")
	r.Static("/static", "./static")

	// Init routers
	unauthorized := r.Group("/")
	unauthorized.GET("/visit", func(c *gin.Context) {
		c.HTML(http.StatusOK, "visit.html", nil)
	})
	unauthorized.GET("/create", func(c *gin.Context) {
		c.HTML(http.StatusOK, "create.html", nil)
	})

	auth := r.Group("/")
	{
		auth.POST("/create", srv.Createcity)
		auth.POST("/visit", srv.Visitcity)
	}

	authorized := r.Group("/")
	authorized.Use(middlewares.AuthRequired)
	{
		authorized.GET("/", func(c *gin.Context) {
			c.HTML(http.StatusOK, "index.html", nil)
		})
		authorized.GET("/profile", func(c *gin.Context) {
			c.HTML(http.StatusOK, "profile.html", nil)
		})
		authorized.GET("/leave", srv.Leavecity)
		authorized.GET("/profile/get", srv.GetProfile)
		authorized.POST("/profile/degrees", srv.Updatecitydegrees)
		authorized.POST("/profile/citycode", srv.Updatecitycode)
		
		authorized.GET("/news/get", srv.GetNews) 
		authorized.POST("/news/send", srv.SendNews)
	}

	r.Run("0.0.0.0:8080")
}

func mustInit(err error) {
	if err != nil {
		slog.Error(
			"Error init",
			"error", err.Error(),
		)
		os.Exit(1)
	}
}

func mustInitWithoutLogger(err error) {
	if err != nil {
		fmt.Printf("Error init: %v\n", err)
		os.Exit(1)
	}
}

func appFilePath() string {
	path, err := os.Executable()
	if err != nil {
		return os.Args[0]
	}
	return path
}

func executeInitScript(db *gorm.DB, filepath string) error {
	content, err := os.ReadFile(filepath)
	if err != nil {
		return fmt.Errorf("Cant read init.sql: %w", err)
	}

	sql := string(content)
	return db.Exec(sql).Error
}
