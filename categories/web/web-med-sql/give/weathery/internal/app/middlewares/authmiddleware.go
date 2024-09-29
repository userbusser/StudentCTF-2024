package middlewares

import (
	"net/http"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func AuthRequired(c *gin.Context) {
	session := sessions.Default(c)
	city := session.Get("city_id")
	if city == nil {
		c.Redirect(http.StatusSeeOther, "/visit")
		c.Abort()
		return
	}
	c.Next()
}
