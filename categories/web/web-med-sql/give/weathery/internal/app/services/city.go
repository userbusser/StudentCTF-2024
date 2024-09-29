package services

import (
	"context"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func (s *Service) GetProfile(c *gin.Context) {
	session := sessions.Default(c)
	cityname := session.Get("city_id")

	if cityname == nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	degrees, err := s.store.City().SelectDegreesByCityName(cityname)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unexpected error occurred"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"degrees": degrees, "cityname": cityname})
}

func (s *Service) Updatecitycode(c *gin.Context) {
	session := sessions.Default(c)
	cityname := session.Get("city_id")
	citycode := c.PostForm("citycode")

	if citycode == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "citycode cannot be empty"})
		return
	}

	go func(citycode, cityname interface{}) {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()

		err := s.store.City().UpdateCitycodeQuery(ctx, citycode, cityname)
		if err != nil {
			log.Printf("Failed to update city code: %v", err)
		}
	}(citycode, cityname)

	s.Leavecity(c)
}

func (s *Service) Updatecitydegrees(c *gin.Context) {
	session := sessions.Default(c)
	cityname := session.Get("city_id")
	degreesStr := c.PostForm("degrees")

	if degreesStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Degrees cannot be empty"})
		return
	}

	var degrees int
	degrees, err := strconv.Atoi(degreesStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid degrees format"})
		return
	}

	go func(degrees, cityname interface{}) {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()

		err := s.store.City().UpdateDegreesQuery(ctx, degrees, cityname)
		if err != nil {
			log.Printf("Failed to insert message: %v", err)
		}

	}(degrees, cityname)

	c.JSON(http.StatusOK, gin.H{"message": "Degrees was succsessfuly updated"})
}
