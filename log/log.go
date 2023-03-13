package log

import (
	"io"
	"io/ioutil"
	"log"
	"os"
)

var (
	LoggerTrace *log.Logger //几乎任何东西
	LoggerDebug *log.Logger //调试
	LoggerInfo  *log.Logger //重要信息
	LoggerWarn  *log.Logger //警告
	LoggerError *log.Logger //错误
)

func init() {
	writer := getWriter("~/ping-base64-webapi", "ping-base64-webapi.log")

	flag := log.Ldate | log.Lmicroseconds | log.Lmsgprefix | log.Lshortfile

	LoggerTrace = log.New(ioutil.Discard, "TRACE  ", flag)
	LoggerDebug = log.New(os.Stdout, "DDEBUG  ", flag)
	LoggerInfo = log.New(writer, "INFO  ", flag)
	LoggerWarn = log.New(os.Stdout, "EARN ", flag)
	LoggerError = log.New(writer, "ERROR  ", flag)
}

//写入的文件
func getWriter(logPath string, logFilename string) io.Writer {
	err := os.MkdirAll(logPath, 0755)
	var file *os.File = nil
	if err != nil {
		log.Println(err.Error())
	} else {
		file, err = os.OpenFile(logPath+"/"+logFilename, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0666)
		if err != nil {
			log.Println("can't open log file", err)
		}
	}
	var writer io.Writer = nil
	if file == nil {
		writer = io.MultiWriter(file, os.Stdout)
	} else {
		writer = io.MultiWriter(os.Stdout)
	}
	return writer
}

func Trace(v ...interface{}) {
	LoggerTrace.Println(v...)
}

func Debug(v ...interface{}) {
	LoggerDebug.Println(v...)
}

func Info(v ...interface{}) {
	LoggerInfo.Println(v...)
}

func Warn(v ...interface{}) {
	LoggerWarn.Println(v...)
}

func Error(v ...interface{}) {
	LoggerError.Println(v...)
}
