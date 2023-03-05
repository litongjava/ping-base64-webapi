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
	file, err := os.OpenFile("/opt/ping-base64-webapi/out.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatalln("can't open log file", err)
	}
	flag := log.Ldate | log.Lmicroseconds | log.Lmsgprefix | log.Lshortfile
	writer := io.MultiWriter(file, os.Stdout)
	LoggerTrace = log.New(ioutil.Discard, "TRACE  ", flag)
	LoggerDebug = log.New(os.Stdout, "DDEBUG  ", flag)
	LoggerInfo = log.New(file, "INFO  ", flag)
	LoggerWarn = log.New(os.Stdout, "EARN ", flag)
	//writer := io.MultiWriter(os.Stdout)
	LoggerError = log.New(writer, "ERROR  ", flag)
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
