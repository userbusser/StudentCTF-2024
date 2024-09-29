package model

type City struct {
	Cityname string `gorm:"primary_key" json:"cityname"`
	Citycode string `json:"citycode"`
	Degrees  int    `json:"degrees"`
	News    []News `gorm:"foreignKey:Cityname;references:Cityname" json:"news"`
}
