package utils

import (
	"archive/zip"
	"bytes"
	"golang.org/x/text/encoding/simplifiedchinese"
	"golang.org/x/text/transform"
	"io"
	"io/ioutil"
	"mime/multipart"
	"os"
	"path/filepath"
	"ping-base64-webapi/log"
)

//移动文件
func MoveFile(file multipart.File, movedDir string, dstFilename string) (bool, error) {
	// 创建移动路径
	err := os.MkdirAll(movedDir, 0755)
	if err != nil {
		return true, err
	}
	//移动到这个文件夹
	dstFilePath := movedDir + "/" + dstFilename
	log.Info("dstFilePath:", dstFilePath)
	//创建文件
	openFile, err := os.OpenFile(dstFilePath, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		log.Error(err.Error())
		return true, err
	}
	defer openFile.Close()
	io.Copy(openFile, file)
	return false, nil
}

func ExtractFile(file multipart.File, targetDir string, length int64) (bool, error) {
	// 创建解压路径
	err := os.MkdirAll(targetDir, 0755)
	if err != nil {
		return true, err
	}

	// 解压文件
	reader, err := zip.NewReader(file, length)
	if err != nil {
		return true, err
	}

	for _, f := range reader.File {
		filename := GetChineseName(f.Name)
		log.Info("filename:", filename)
		path := filepath.Join(targetDir, filename)

		var err error = nil
		if f.FileInfo().IsDir() {
			err = os.MkdirAll(path, f.Mode())
			if err != nil {
				return true, err
			}
			continue
		}

		err = os.MkdirAll(filepath.Dir(path), 0755)
		if err != nil {
			return true, err
		}

		unzippedFile, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
		if err != nil {
			return true, err
		}
		defer unzippedFile.Close()

		zippedFile, err := f.Open()
		if err != nil {
			return true, err
		}
		defer zippedFile.Close()

		_, err = io.Copy(unzippedFile, zippedFile)
		if err != nil {
			return true, err
		}
	}
	return false, nil
}

//获取中文名称
func GetChineseName(filename string) string {
	i := bytes.NewReader([]byte(filename))
	decoder := transform.NewReader(i, simplifiedchinese.GB18030.NewDecoder())
	content, _ := ioutil.ReadAll(decoder)
	filename = string(content)
	return filename
}
