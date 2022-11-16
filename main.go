package main

import (
	"log"
	"net/http"
	"ping-base64-webapi/controller"
)

func main() {
	log.Println("start")
	controller.RegisterRoutes()
	err := http.ListenAndServe(":10404", nil)
	if err != nil {
		log.Println(err)
	}
}
