package controller

import (
	"encoding/base64"
	"encoding/json"
	"log"
	"net/http"
	"ping-base64-webapi/services"
	"regexp"
)

func registerWebRouters() {
	http.HandleFunc("/web/", handleWeb)
}

func handleWeb(writer http.ResponseWriter, request *http.Request) {
	//log.Println(request.URL.Path)
	pattern, _ := regexp.Compile(`/web/(.+)`)
	matches := pattern.FindStringSubmatch(request.URL.Path)
	if len(matches) > 0 {
		bytes, _ := base64.StdEncoding.DecodeString(matches[1])
		result := services.RunWrapperCommand(string(bytes))
		encoder := json.NewEncoder(writer)
		err := encoder.Encode(result)
		if err != nil {
			log.Println("err", err)
		}
	} else {
		log.Println("not find base64 string")
		writer.WriteHeader(http.StatusNotFound)
	}
}
