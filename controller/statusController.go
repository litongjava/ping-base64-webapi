package controller

import (
	"fmt"
	"net/http"
)

func registerStatusRouter() {
	http.HandleFunc("/status", handleStatus)
}

func handleStatus(writer http.ResponseWriter, request *http.Request) {
	fmt.Fprintln(writer, "OK")
}
