package main

import (
  "net/http"
  "ping-base64-webapi/controller"
)

func main() {
  controller.RegisterRoutes()
  http.ListenAndServe(":10404", nil)
}
