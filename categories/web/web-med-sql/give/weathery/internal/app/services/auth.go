package services

import (
	"net/http"
	"weathery/internal/model"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func (s *Service) Createcity(c *gin.Context) {
	cityname := c.PostForm("cityname")
	citycode := c.PostForm("citycode")

	if cityname == "" || citycode == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "cityname or citycode cannot be empty"})
		return
	}

	if len(cityname) < 5 || len(citycode) < 5 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "cityname and citycode must be at least 5 characters"})
		return
	}

	_, err := s.store.City().FindByCityName(cityname)

	if err != gorm.ErrRecordNotFound {
		c.JSON(http.StatusBadRequest, gin.H{"error": "cityname is already taken"})
		return
	}

	if err != nil {
		_, err = s.store.City().Create(&model.City{Cityname: cityname, Citycode: citycode, Degrees: 273})

		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to create city"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Successfully signuped"})
	}
}

func (s *Service) Visitcity(c *gin.Context) {
	cityname := c.PostForm("cityname")
	citycode := c.PostForm("citycode")

	if cityname == "" || citycode == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "cityname or citycode cannot be empty"})
		return
	}

	city, err := s.store.City().FindByCityName(cityname)

	if err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid login credentials"})
			return
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Unexpected error occurred"})
			return
		}
	}

	if citycode != city.Citycode {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid login credentials"})
		return
	}

	session := sessions.Default(c)
	session.Set("city_id", city.Cityname)
	err = session.Save()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save session"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Successfully signed in"})
}

func (s *Service) Leavecity(c *gin.Context) {
	session := sessions.Default(c)
	session.Clear()
	err := session.Save()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to clear session"})
	}

	c.Redirect(http.StatusMovedPermanently, "/visit")
}
