#ping-base64-webapi
## 1.简介
使用go语言进行编写

主要功能
- 将运行命令通过base54加密发送到服务端,服务器端通过base54进行解密,解密后执行命令
- 支持文件上传和解压(用于部署前端项目)
- 支持文件上传和解压,并执行命令(用于部署后端项目)

## 2.安装
```
创建解压目录
mkdir /opt/ping-base64-webapi
解压
略
```
启动
```shell
/opt/ping-base64-webapi/ping-base64-webapi
```
测试服务
```shell
curl http://localhost:10405/status
```


配置nginx
```
location /ping-base64-webapi/ {
  proxy_pass http://localhost:10405/;
  proxy_pass_header Set-Cookie;
  proxy_set_header Host $host;
}
```

测试
```
curl http://localhost/ping-base64-webapi/status
```
配置开机启动
```
vi /lib/systemd/system/ping-base64-webapi.service
[Unit]
Description=ping-base64-webapi
After=network.target

[Service]
Type=simple
User=root
Restart=on-failure
RestartSec=5s
WorkingDirectory = /opt/ping-base64-webapi
ExecStart=/opt/ping-base64-webapi/ping-base64-webapi

[Install]
WantedBy=multi-user.target
```

```
systemctl daemon-reload
systemctl enable ping-base64-webapi
systemctl stop ping-base64-webapi
systemctl start ping-base64-webapi
systemctl status ping-base64-webapi
```
查看日志
```
cd /opt/ping-base64-webapi
tail -f out.log
```

##3.常用命令对照
```
nginx -t        bmdpbnggLXQ=
nginx s reload  bmdpbnggLXMgcmVsb2Fk
systemctl status nginx c3lzdGVtY3RsIHN0YXR1cyBuZ2lueA==
systemctl restart nginx c3lzdGVtY3RsIHJlc3RhcnQgbmdpbng=
```