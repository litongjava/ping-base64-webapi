package controller

import (
	"archive/zip"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

func registerUnzipRouter() {
	http.HandleFunc("/file/upload-unzip/", handleUploadUnzip)
}

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

	// 创建解压路径
	err = os.MkdirAll(targetDir, 0755)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 解压文件
	reader, err := zip.NewReader(file, r.ContentLength)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	for _, f := range reader.File {
		path := filepath.Join(targetDir, f.Name)
		if f.FileInfo().IsDir() {
			err = os.MkdirAll(path, f.Mode())
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
			continue
		}

		err = os.MkdirAll(filepath.Dir(path), 0755)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		unzippedFile, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer unzippedFile.Close()

		zippedFile, err := f.Open()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer zippedFile.Close()

		_, err = io.Copy(unzippedFile, zippedFile)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
	return
}
