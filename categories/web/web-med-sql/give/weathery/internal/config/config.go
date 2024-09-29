package config

import (
	"os"
	"path/filepath"

	"github.com/spf13/viper"
)

var (
	configuration *Configurartion
	configFileExt = ".yaml"
	configType    = "yaml"
)

type Configurartion struct {
	App      *AppConfiguration
	Database *DatabaseConfiguration
}

type AppConfiguration struct {
	Secretkey string `default:"changeme"`
}

type DatabaseConfiguration struct {
	Name     string `default:"weathery"`
	Host     string `default:"weatherydb"`
	Port     int    `default:"5432"`
	Username string `default:"weathery"`
	Password string `default:"weathery"`
	LogMode  bool   `default:"false"`
	SSLMode  string `default:"disable"`
}

func Init(configPath, configName string) (*Configurartion, error) {
	configFilePath := filepath.Join(configPath, configName) + configFileExt

	initializeConfig(configPath, configName)

	bindEnvs()

	setDefaults()
	if err := readConfiguration(configFilePath); err != nil {
		return nil, err
	}

	viper.AutomaticEnv()
	if err := viper.Unmarshal(&configuration); err != nil {
		return nil, err
	}

	return configuration, nil
}


func readConfiguration(configFilePath string) error {
	err := viper.ReadInConfig() 
	if err != nil {
		if _, err := os.Stat(configFilePath); os.IsNotExist(err) {
			os.Create(configFilePath)
		} else {
			return err
		}
		if err := viper.WriteConfig(); err != nil {
			return err
		}
	}
	return nil
}

func initializeConfig(configPath, configName string) {
	viper.AddConfigPath(configPath)
	viper.SetConfigName(configName)
	viper.SetConfigType(configType)
}

func bindEnvs() {
	viper.BindEnv("app.secretkey", "SECRETKEY")

	viper.BindEnv("database.name", "WEATHERY_DB_NAME")
	viper.BindEnv("database.host", "WEATHERY_DB_HOST")
	viper.BindEnv("database.port", "WEATHERY_DB_PORT")
	viper.BindEnv("database.username", "WEATHERY_DB_USERNAME")
	viper.BindEnv("database.password", "WEATHERY_DB_PASSWORD")
	viper.BindEnv("database.logmode", "WEATHERY_DB_LOG_MODE")
	viper.BindEnv("database.sslmode", "WEATHERY_DB_SSL_MODE")
}

func setDefaults() {
	viper.SetDefault("app.secretkey", "changeme")
	viper.SetDefault("database.name", "weathery")
	viper.SetDefault("database.username", "weathery")
	viper.SetDefault("database.password", "weathery")
	viper.SetDefault("database.host", "weatherydb")
	viper.SetDefault("database.port", 5432)
	viper.SetDefault("database.logmode", false)
	viper.SetDefault("database.sslmode", "disable")
}
