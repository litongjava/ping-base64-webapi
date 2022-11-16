package controller

import (
	"bytes"
	"fmt"
	"log"
	"net/http"
	"os/exec"
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
		//for i := 0; i < len(matches); i++ {
		//  fmt.Println(matches[i])
		//}
		//将string转为int

		result := ""
		if "nginx-reload" == matches[1] {
			result = runCmdbyGrep("nginx", "-s", "reload")
		} else {
			result = runCmdbyGrep(matches[1])
		}
		n, err := fmt.Fprintln(writer, result)
		if err != nil {
			log.Println(err)
		} else {
			log.Println(n)
		}
	} else {
		log.Println("not find base64 string")
		writer.WriteHeader(http.StatusNotFound)
	}
}

func runCmdbyGrep(name string, arg ...string) string {
	cmd := exec.Command(name, arg...)
	var out bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &stderr
	err := cmd.Run()
	if err != nil {
		return stderr.String()
	} else {
		return out.String()
	}
}
