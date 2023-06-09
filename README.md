# ping-base64-webapi
# 1.简介
ping-base64-webapi是一款使用go语言开发用于自动部署的的Web服务
主要功能
- 将运行命令通过base54加密发送到服务端,服务器端通过base54进行解密,解密后执行命令
- 支持文件上传和解压(用于部署前端项目)
- 支持文件上传,解压和运行命令(用于部署后台项目)

主要业务逻辑
- 接受上传文件,解压,移动到指定目录,并执行启动命令

# 2.安装
## 2.1.安装服务端
下载
```
mkdir -p /data/package/
cd /data/package/
wget https://github.com/litongjava/ping-base64-webapi/releases/download/v0.1.0/ping-base64-webapi-linux-amd64.zip
```

解压
```
unzip ping-base64-webapi-linux-amd64.zip -d /opt
mv ping-base64-webapi-linux-amd64 ping-base64-webapi
```

启动
```
cd /opt/ping-base64-webapi
chmod u+x ping-base64-webapi
/opt/ping-base64-webapi/ping-base64-webapi
```
测试服务是否启动成功
```
curl http://localhost:10405/status
```

## 2.2.配置开机启动
使用root用户
```
vi /etc/systemd/system/ping-base64-webapi.service
```

```
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

使用appadmin用户启动
```
vi /etc/systemd/system/ping-base64-webapi.service
```

```
[Unit]
Description=ping-base64-webapi
After=network.target

[Service]
Type=simple
User=appadmin
Restart=on-failure
RestartSec=5s
WorkingDirectory = /home/appadmin/opt/ping-base64-webapi
ExecStart=/home=/home/appadmin/opt/ping-base64-webapi/ping-base64-webapi

[Install]
WantedBy=multi-user.target
```
启动
```
systemctl daemon-reload
systemctl enable ping-base64-webapi
systemctl stop ping-base64-webapi
sudo systemctl start ping-base64-webapi
sudo systemctl status ping-base64-webapi
```
## 2.3.配置nginx
使用nginx代理ping-base64-webapi
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

指定代理前缀路径,代理前缀路径通常是工程命令,例如robot-api
```
location /robot-api/ping-base64-webapi/ {
  proxy_pass http://localhost:10405/;
  proxy_pass_header Set-Cookie;
  proxy_set_header Host $host;
}
```

测试
```
curl http://localhost/robot-api/ping-base64-webapi/status
```

# 3.使用
## 3.1.部署Spring-boot项目
### 3.1.1.修改Spring-boot项目
添加src/main/resources/loader.properties 
```
# 配置启动时外置依赖加载目录，只加载应用根目录下的lib/
loader.path=file:./lib
```

修改pom.xml的properties添加assembly,spring-boot.version和main.class
```
    <spring-boot.version>2.5.6</spring-boot.version>
    <assembly>full</assembly>
    <!-- <assembly>full</assembly> -->
<main.class>com.xxx.ServiceTestApplication</main.class>

```
修改pom.xml的build的plugins配置
pring-boot-maven-plugin
maven-dependency-plugin 
maven-assembly-plugin
```
  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
        <version>${spring-boot.version}</version>
        <configuration>
          <!--使该插件支持热启动 -->
          <fork>true</fork>
          <!-- main 入口 -->
          <mainClass>${main.class}</mainClass>
          <!-- 设置为ZIP，此模式下spring-boot-maven-plugin会将Manifest.MF文件中的Main-Class设置为org.springframework.boot.loader.PropertiesLauncher -->
          <layout>ZIP</layout>
          <includes>
            <include>
              <groupId>org.psyduck</groupId>
              <artifactId>psyduck-admin</artifactId>
            </include>
          </includes>
        </configuration>
        <executions>
          <execution>
            <goals>
              <goal>repackage</goal><!--可以把依赖的包都打包到生成的Jar包中 -->
            </goals>
          </execution>
        </executions>
      </plugin>
      <!--maven-dependency-plugin -->
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-dependency-plugin</artifactId>
        <version>3.2.0</version>
        <executions>
          <execution>
            <id>copy-dependencies</id>
            <phase>prepare-package</phase>
            <goals>
              <goal>copy-dependencies</goal>
            </goals>
            <configuration>
              <!-- 第三方依赖的存放目录，最终生成到target/lib -->
              <outputDirectory>${project.build.directory}/lib</outputDirectory>
              <!-- 需要排除的jar的 groupId -->
              <excludeGroupIds>
                org.psyduck
              </excludeGroupIds>
              <!-- 默认为test，会复制所有依赖，只需要复制runtime的依赖 -->
              <includeScope>
                runtime
              </includeScope>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <!-- 组装文件并压缩zip插件 -->
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-assembly-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
          <!-- not append assembly id in release file name -->
          <appendAssemblyId>false</appendAssemblyId>
          <descriptors>
            <descriptor>assembly-${assembly}.xml</descriptor>
          </descriptors>
        </configuration>
        <executions>
          <execution>
            <id>make-assembly</id>
            <phase>package</phase>
            <goals>
              <goal>single</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
```
在项目根目录下添加assembly文件
assembly-full.xml
```
<assembly xmlns="http://maven.apache.org/plugins/maven-assembly-plugin/assembly/1.1.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/plugins/maven-assembly-plugin/assembly/1.1.0 http://maven.apache.org/xsd/assembly-1.1.0.xsd">
  <id>zipPackage</id>
  <formats>
    <format>zip</format>
  </formats>
  <includeBaseDirectory>false</includeBaseDirectory>
  <fileSets>
    <fileSet>
      <directory>${project.build.directory}</directory>
      <outputDirectory>${file.separator}</outputDirectory>
      <includes>
        <include>*.jar</include>
      </includes>
    </fileSet>
    <!--打包targ/lib-->
    <fileSet>
      <directory>${project.build.directory}/lib</directory>
      <outputDirectory>lib</outputDirectory>
      <includes>
        <include>*.jar</include>
      </includes>
    </fileSet>

    <!-- 项目根下面的脚本文件 copy 到根目录下 -->
    <fileSet>
      <directory>${basedir}/src/main/bin</directory>
      <lineEnding>unix</lineEnding>
      <outputDirectory></outputDirectory>
      <!-- 脚本文件在 linux 下的权限设为 755，无需 chmod 可直接运行 -->
      <fileMode>755</fileMode>
      <includes>
        <include>*.sh</include>
        <include>*.service</include>
      </includes>
    </fileSet>

    <fileSet>
      <directory>${project.build.directory}/../../native-config</directory>
      <outputDirectory>config</outputDirectory>
      <includes>
        <include>*.yml</include>
      </includes>
    </fileSet>
  </fileSets>
</assembly>
```
assembly-thin.xml
```
<assembly xmlns="http://maven.apache.org/plugins/maven-assembly-plugin/assembly/1.1.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/plugins/maven-assembly-plugin/assembly/1.1.0 http://maven.apache.org/xsd/assembly-1.1.0.xsd">
  <id>zipPackage</id>
  <formats>
    <format>zip</format>
  </formats>
  <includeBaseDirectory>false</includeBaseDirectory>
  <fileSets>
    <fileSet>
      <directory>${project.build.directory}</directory>
      <outputDirectory>${file.separator}</outputDirectory>
      <includes>
        <include>*.jar</include>
      </includes>
    </fileSet>

    <fileSet>
      <directory>${project.build.directory}/../../native-config</directory>
      <outputDirectory>config</outputDirectory>
      <includes>
        <include>*.yml</include>
      </includes>
    </fileSet>
  </fileSets>
</assembly>
```
### 3.1.2.构建Spring-boot项目

全量包：
```
set JAVA_HOME=D:\\dev_program\\java\\jdk1.8.0_121
mvnd clean package -DskipTests -Dassembly=full
```
瘦子包：
```
set JAVA_HOME=D:\\dev_program\\java\\jdk1.8.0_121
mvnd clean package -DskipTests -Dassembly=thin
```
构建完成后会生成
target\spring-boot-table-to-json-1.0.zip
第一次不是打包成全量包后续部署如果依赖没有变化可以打包成瘦子包
### 3.1.3.基于python脚本部署Spring-Boot项目
添加python脚本到服务器
```
mkdir -p /data/apps/webapps/package/
cd /data/apps/webapps/package/
wget https://raw.githubusercontent.com/litongjava/ping-base64-webapi/main/script/deploy-root.py
```

客户端发送命令调用脚本进行部署
添加upload-run.bat内容如下
```
set JAVA_HOME=D:\\dev_program\\java\\jdk1.8.0_121
mvnd clean package -DskipTests -Dassembly=thin
ping-base64-client -url http://192.168.3.9:10405/file/upload-run/ -file target\spring-boot-table-to-json-1.0.zip -m /data/apps/webapps/package -c "python2.7 /data/apps/webapps/package/deploy-root.py -s spring-boot -m spring-boot-table-to-json -pg spring-boot-table-to-json-1.0.zip -p 8021 -a update"
```
输出"success":true 表示部署成功
这里使用了ping-base64-client  
https://github.com/litongjava/ping-base64-client

部署的项目是spring-boot-table-to-json  
https://github.com/litongjava/table-to-json/tree/main/spring-boot-table-to-json

### 3.1.4.基于Docker部署Spring-Boot项目
首次部署
将文件上传到服务器上,解压并启动docker容器
upload-start-docker.bat
```
ping-base64-client -url http://192.168.3.9:10405/file/upload-run/ -file target\spring-boot-table-to-json-1.0.zip -m /data/apps/webapps/package -d /data/apps/webapps/spring-boot-table-to-json -c "docker run --name spring-boot-table-json -dit -v /data/apps/webapps/spring-boot-table-to-json:/app --net=host -w /app litongjava/jdk:8u211 /usr/java/jdk1.8.0_211/bin/java -jar spring-boot-table-to-json-1.0.jar"
```

执行docker部署命令如下,用于启动工程
```
docker run --name spring-boot-table-json -dit -v /data/apps/webapps/spring-boot-table-to-json:/app --net=host -w /app litongjava/jdk:8u211 /usr/java/jdk1.8.0_211/bin/java -jar spring-boot-table-to-json-1.0.jar
```

更新
将文件上传到服务器上,解压并重启docker容器
```
ping-base64-client -url http://192.168.3.9:10405/file/upload-run/ -file target\spring-boot-table-to-json-1.0.zip -m /data/apps/webapps/package -d /data/apps/webapps/spring-boot-table-to-json -c "docker restart spring-boot-table-json"
```
