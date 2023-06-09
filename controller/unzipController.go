package controller

import (
	"encoding/json"
	"fmt"
	"net/http"
	"ping-base64-webapi/log"
	"ping-base64-webapi/services"
	"ping-base64-webapi/utils"
)

func registerUnzipRouter() {
	http.HandleFunc("/file/upload-unzip/", handleUploadUnzip)
	http.HandleFunc("/file/upload-run/", handleUploadRun)
}

// 上传文件,放到指定目录,并运行脚本
func handleUploadRun(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	file, header, err := r.FormFile("file")
	//将压缩包移动到的文件夹
	movedDir := r.FormValue("m")
	// 获取解压路径
	targetDir := r.FormValue("d")
	//运行的命令
	cmd := r.FormValue("c")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer file.Close()

	if movedDir == "" {
		log.Info("Not find m from request parameters")
	} else {
		b, err := utils.MoveFile(file, movedDir, header.Filename)
		if b {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	if targetDir == "" {
		log.Info("Not find d from request parameters")
	} else {
		length := r.ContentLength
		b, err := utils.ExtractFile(file, targetDir, length)
		if b {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}
	//执行命令
	if cmd == "" {
		log.Info("Not find c from request parameters")
	} else {
		log.Info("cmd:", cmd)
		result := services.RunWrapperCommand(cmd)
		jsonBytes, err := json.Marshal(result)
		if err != nil {
			log.Info("err", err.Error())
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		_, err = fmt.Fprintln(w, string(jsonBytes))
		if err != nil {
			return
		}
	}

}

// 上传文件并解压
func handleUploadUnzip(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer file.Close()

	// 获取解压路径
	targetDir := r.FormValue("d")
	if targetDir == "" {
		http.Error(w, "targetDir is required", http.StatusBadRequest)
		return
	}

	length := r.ContentLength
	b, err := utils.ExtractFile(file, targetDir, length)
	if b {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	return
}
