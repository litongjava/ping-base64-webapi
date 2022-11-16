package utils

import (
	"os/exec"
	"ping-base64-webapi/model"
	"time"
)

func RunComamnd(name string, arg ...string) model.CommandResult {
	start := time.Now().Unix()
	command := exec.Command(name, arg...)
	//会自动执行命令
	result, err := command.CombinedOutput()
	end := time.Now().Unix()

	cmdResult := model.CommandResult{}
	cmdResult.Time = end - start
	if err != nil {
		cmdResult.Error = err.Error()
		cmdResult.Success = false
	} else {
		cmdResult.Success = true
	}
	cmdResult.Output = (string(result))
	return cmdResult
}
