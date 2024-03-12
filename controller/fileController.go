package controller

import (
	"fmt"
	"github.com/google/uuid"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"ping-base64-webapi/config"
	"ping-base64-webapi/log"
	"regexp"
	"time"
)

func registerFileRouter() {
	http.HandleFunc("/file/upload", handleUpload)
	http.HandleFunc("/file/download/", handleDownload)
}

// 上传文件
func handleUpload(writer http.ResponseWriter, request *http.Request) {
	file, header, err := request.FormFile("file")
	if err != nil {
		return
	}
	//上传目录
	timeNow := time.Now()
	dateString := timeNow.Format("2006-01-02")
	uuidString := uuid.New().String()

	savePath := config.CONFIG.App.FilePath + "/" + dateString + "/" + uuidString
	isExists := IsExist(savePath)
	if !isExists {
		log.Info("create path", savePath)
		os.MkdirAll(savePath, os.ModePerm)
	}
	//读取文件名
	log.Info("dstFilePath", header.Filename)

	//上传目录 uploadPath+/+日期+uuid+dstFilePath
	dstFilePath := savePath + "/" + header.Filename
	//创建文件
	openFile, err := os.OpenFile(dstFilePath, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		log.Error(err.Error())
		return
	}
	defer file.Close()
	defer openFile.Close()
	io.Copy(openFile, file)
	fmt.Fprintln(writer, dateString+"/"+uuidString)
}

// 下载文件
func handleDownload(writer http.ResponseWriter, request *http.Request) {
	subDir, done := getId(writer, request)
	if done {
		return
	}

	log.Info("subDir:", subDir)
	savePath := config.CONFIG.App.FilePath + "/" + subDir
	filename, done := getFilename(writer, savePath)
	if done {
		return
	}

	filePath := savePath + "/" + filename
	bytes, err := os.ReadFile(filePath)
	if err != nil {
		log.Error("读取文件失败", err)
		return
	}
	writer.Header().Add("Content-Type", "application/octet-stream")
	writer.Header().Add("Content-Disposition", "attachment; filename= "+filename)
	writer.Write(bytes)
}

// 获取文件名
func getFilename(writer http.ResponseWriter, savePath string) (string, bool) {
	fileInfoList, err := ioutil.ReadDir(savePath)
	if err != nil {
		log.Error("读取文件列表失败", err.Error())
		fmt.Fprint(writer, "读取文件列表失败", err.Error())
		return "", true
	}
	filename := ""
	if len(fileInfoList) > 0 {
		filename = fileInfoList[0].Name()
	} else {
		log.Error("没有读取到文件")
		fmt.Fprint(writer, "没有读取到文件")
		return "", true
	}
	return filename, false
}

func getId(writer http.ResponseWriter, request *http.Request) (string, bool) {
	pattern, _ := regexp.Compile(`/file/download/(.+)`)
	matches := pattern.FindStringSubmatch(request.URL.Path)
	id := ""
	if len(matches) > 0 {
		id = matches[1]
	} else {
		fmt.Fprint(writer, "请求输入正确的路径")
		return id, true
	}
	return id, false
}

func IsExist(path string) bool {
	_, err := os.Stat(path)
	return err == nil || os.IsExist(err)
}
