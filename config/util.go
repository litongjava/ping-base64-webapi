package config

import (
  "fmt"
  "gopkg.in/yaml.v2"
  "io/ioutil"
  "ping-base64-webapi/log"
)

var CONFIG *Config

func init() {
  yamlFile, err := ioutil.ReadFile("./config/config.yml")
  //yamlFile, err := ioutil.ReadFile(filename)
  if err != nil {
    log.Error(err.Error())
  }

  err = yaml.Unmarshal(yamlFile, &CONFIG)
  if err != nil {
    fmt.Println("error", err.Error())
  }
}
