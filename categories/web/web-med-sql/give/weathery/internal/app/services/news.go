package services

import (
	"fmt"
	"log"
	"net/http"
	"weathery/internal/model"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func (s *Service) GetNews(c *gin.Context) {
	news, err := s.store.News().All()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unexpected error occurred"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"news": news})
}

func (s *Service) SendNews(c *gin.Context) {
	session := sessions.Default(c)

	cityname := session.Get("city_id")
	newstitle := c.PostForm("newstitle")
	newsbody := c.PostForm("newsbody")

	go func(newstitle, newsbody string, cityname interface{}) {
		citynameStr, ok := cityname.(string)
		fmt.Println(citynameStr)
		if !ok {
			log.Printf("Failed to convert cityname to string")
			return
		}
		_, err := s.store.News().Create(&model.News{Newstitle: newstitle, Newsbody: newsbody, Cityname: citynameStr})

		if err != nil {
			log.Printf("Failed to insert message: %v", err)
		}
	}(newstitle, newsbody, cityname)

	c.JSON(http.StatusOK, gin.H{"news": "News created"})
}
