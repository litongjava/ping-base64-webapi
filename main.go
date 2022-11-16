package main

import (
	"log"
	"net/http"
	"os"
	"ping-base64-webapi/controller"
)

func main() {
	port := "10405"
	for i := 1; i < len(os.Args); i += 2 {
		param := os.Args[i]
		if param == "--port" {
			port = os.Args[i+1]
		}
	}
	log.Println("start")
	controller.RegisterRoutes()
	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		log.Fatalln(err)
	}
}
