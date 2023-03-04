package main

import (
	"net/http"
	"os"
	"ping-base64-webapi/config"
	"ping-base64-webapi/controller"
	"ping-base64-webapi/log"
	"strconv"
)

func main() {
	port := strconv.Itoa(config.CONFIG.App.Port)
	for i := 1; i < len(os.Args); i += 2 {
		param := os.Args[i]
		if param == "--port" {
			port = os.Args[i+1]
		}
	}
	log.Info("start listen on", port)
	controller.RegisterRoutes()
	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		log.Error(err.Error())
	}
}
