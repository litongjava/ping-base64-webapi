package services

import (
	"ping-base64-webapi/model"
	"ping-base64-webapi/utils"
	"strings"
)

func RunWrapperCommand(command string) model.CommandResult {
	result := model.CommandResult{}
	if "nginx-reload" == command {
		result = utils.RunComamnd("nginx", "-s", "reload")
	} else if "nginx-t" == command {
		result = utils.RunComamnd("nginx", "-t")
	} else {
		slice := strings.Split(command, " ")
		result = utils.RunComamnd(slice[0], slice[1:]...)
	}
	return result
}
