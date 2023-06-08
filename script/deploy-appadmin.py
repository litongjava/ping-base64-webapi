# -*- coding: utf-8 -*-
import argparse
import datetime
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import time
import zipfile

#Version
VERSION = '1.3.5'
# 部署环境 生产prod, 测试test，开发dev
ENVIRONMENT = 'test'
# 后端应用部署根目录
BASE_WEBAPP_DIR = '/data/apps/webapps'
# 前端应用部署根目录
BASE_FRONTEND_DIR = '/data/apps/web'
# 合法操作用户
LEGAL_OPERATOR = 'appadmin'
#等待应用启动秒数
WAIT_CHECK_SECOND = 5
# 进程状态尝试检查次数
TRY_CHECK_TIMES = 10
# 部署包存放目录
BASE_PACKAGE_DIR = BASE_WEBAPP_DIR + '/package'
# 默认JVM参数
DEFAULT_JVM_OPT = '-Xms512m -Xmx512m'
# 加密密码
ENCRYPTOR_PASSWORD = ''
#nacos密码
NACOS_PASSWORD = ''
#nacos地址
NACOS_ADDR= ''

# 兼容python2编码问题
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def get_file_md5(file_path):
    """
    获取文件的MD5值
    :param file_path: 文件路径
    :return:
    """
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        for line in f:
            m.update(line)
    md5code = m.hexdigest()
    return md5code


# 解压文件
def extract_webapp_zip_file(zip_file_path, to_path):
    """
    解压文件
    :param zip_file_path: zip文件路径
    :param to_path: 解压目标路径
    :return:
    """

    zip_file = zipfile.ZipFile(zip_file_path)
    namelist = zip_file.namelist()
    is_contain_lib = False
    is_contain_jar = False
    is_contain_config = False
    jar_file = ''
    lib = 'lib'
    config = 'config'
    lib_dir = lib + os.path.sep
    config_dir = config + os.path.sep
    for name in namelist:
        if lib_dir not in name and name.endswith(".jar"):
            jar_file = name
            is_contain_jar = True
        elif lib_dir in name:
            is_contain_lib = True
        elif config_dir in name:
            is_contain_config = True

    if is_contain_jar is False:
        raise Exception("压缩包中不存在jar包")

    if is_contain_lib:
        delete_folder(to_path, lib)

    # jar_file = ''
    for file in namelist:
        zip_file.extract(file, to_path)
    zip_file.close()
    return jar_file


def delete_folder(to_path, folder_name):
    lib_path = to_path + os.path.sep + folder_name
    if os.path.exists(lib_path):
        shutil.rmtree(lib_path)


# 压缩文件
def compress_webapp_zip_file(zip_file_path, compress_file_path, compress_file_name):
    """
    压缩compress_file_path目录文件到compress_file_name目录，并生成zip_file_path的zip文件
    :param zip_file_path: 生成的zip文件路径
    :param compress_file_path: 压缩文件的目录
    :param compress_file_name: 压缩文件根文件名
    :return:
    """
    zip_file = zipfile.ZipFile(zip_file_path, 'w')
    for path, dir_names, file_names in os.walk(compress_file_path):
        file_path = compress_file_name + path.replace(compress_file_path, '')

        for file_name in file_names:
            if path.endswith('lib') or file_name.endswith(".jar"):
                zip_file.write(os.path.join(path, file_name), os.path.join(file_path, file_name))
    zip_file.close()


# 解压文件
def extract_zip_file(zip_file_path, to_path):
    """
    解压文件
    :param zip_file_path: zip文件路径
    :param to_path: 解压目标路径
    :return:
    """
    zip_file = zipfile.ZipFile(zip_file_path)
    for file in zip_file.namelist():
        if '__MACOSX' in file:
            continue
        zip_file.extract(file, to_path)
    zip_file.close()


# 压缩文件
def compress_zip_file(zip_file_path, compress_file_path, compress_file_name):
    """
    压缩compress_file_path目录文件到compress_file_name目录，并生成zip_file_path的zip文件
    :param zip_file_path: 生成的zip文件路径
    :param compress_file_path: 压缩文件的目录
    :param compress_file_name: 压缩文件根文件名
    :return:
    """
    zip_file = zipfile.ZipFile(zip_file_path, 'w')
    for path, dir_names, file_names in os.walk(compress_file_path):
        file_path = compress_file_name + path.replace(compress_file_path, '')
        for file_name in file_names:
            zip_file.write(os.path.join(path, file_name), os.path.join(file_path, file_name))
    zip_file.close()


def show_error(p_str):
    print('\n')
    print('  ERROR  @_@： %s' % p_str)
    print('\n')
    sys.exit(1)


class Shell(object):
    """
        Shell基础操作类
    """

    def execute(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True)
        stdout, stderr = proc.communicate()
        return proc.returncode, stdout, stderr

    def check_executor(self):
        code, user, err = self.execute('whoami')
        user = user.replace('\n', '')
        if user == LEGAL_OPERATOR:
            pass
        elif user == 'root':
            show_error('当前用户为%s，不是%s, 请使用su %s -c "部署命令"进行操作执行' % (user, LEGAL_OPERATOR, LEGAL_OPERATOR))
        else:
            show_error('当前用户为%s，不是%s，无法进行部署操作' % (user, LEGAL_OPERATOR))

    def show_env(self):
        env = '未知'
        if ENVIRONMENT == 'prod':
            env = '生产'
        elif ENVIRONMENT == 'test':
            env = '测试'
        elif ENVIRONMENT == 'dev':
            env = '开发'
        log.info('当前脚本版本是 %s' % VERSION)
        log.info('当前脚本是 %s 环境配置，如需修改请手动编辑部署脚本修改”ENVIRONMENT“参数' % env)

    def execute_and_get(self, command):
        code, stdout, stderr = self.execute(command)
        res = None
        if stdout is not None and len(stdout) > 0:
            res = stdout.replace('\n', '')
        return res


class Logger:
    """
        日志类
    """

    def __init__(self, sys_name, app_name, log_level=logging.DEBUG, format_level=1):

        log_name = sys_name + '::' + app_name
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(log_level)

        today = datetime.datetime.now().strftime('%Y%m%d')

        log_dir = BASE_WEBAPP_DIR + '/common/log/%s' % app_name
        log_file = '%s/%s.log' % (log_dir, today)

        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                # print('创建日志目录: %s' % log_dir)
        except:
            show_error('日志目录创建失败...')

        # 创建一个handler，用于写入日志文件
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # 再创建一个handler，用于输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # 定义handler的输出格式
        # 用字典保存日志级别
        format_dict = {
            1: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            2: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            3: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            4: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            5: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        }

        formatter = format_dict[int(format_level)]
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


class BaseWebapp(Shell):
    """
        web后端部署操作类
    """

    def __init__(self, project_name, app_name, package_name, port, action, recover_file):
        self.today = datetime.datetime.now().strftime('%Y%m%d')

        # 项目名
        self.project_name = project_name

        # 应用名
        self.app_name = app_name

        # 包名
        self.package_name = package_name

        # 端口号
        self.port = port

        self.base_path = BASE_WEBAPP_DIR
        self.package_dir = BASE_PACKAGE_DIR

        project_app = self.app_name

        self.backup_dir = self.base_path + ('/backup/%s' % project_app)
        self.backup_file = ''

        self.recover_dir = self.base_path + ('/backup/%s' % project_app)
        self.recover_file = recover_file

        self.app_dir = (self.base_path + '/%s') % self.app_name

        if self.package_name.endswith('.zip'):
            zip_file_path = self.package_dir + '/' + self.package_name
            if action == 'rollback':
                recover_str = recover_file.rsplit('_', 1)[1]
                file_day = recover_str[0:8]
                zip_file_path = self.recover_dir + ('/%s/%s' % (file_day, self.recover_file))

            if not os.path.exists(zip_file_path):
                show_error("部署包不存在：%s" % zip_file_path)

            zip_file = zipfile.ZipFile(zip_file_path)
            namelist = zip_file.namelist()
            jar_file = None
            for name in namelist:
                if 'lib' not in name and name.endswith(".jar"):
                    jar_file = name
                    break
                else:
                    pass
            zip_file.close()
            if jar_file is not None:
                self.jar_file = jar_file
            else:
                show_error("压缩包中不存在jar包")
        else:
            self.jar_file = self.package_name

    def show_info(self):
        self.show_env()
        log.info("当前项目名：%s", self.project_name)
        log.info("当前应用名：%s", self.app_name)
        log.info("当前应用包名：%s", self.package_name)
        log.info("当前应用端口：%s", self.port)
        log.info("当前应用部署路径：%s", self.base_path + '/' + self.app_name)
        log.info("当前应用部署包存放路径：%s", self.package_dir)
        log.info("当前应用部署备份包存放目录：%s", self.backup_dir)
        log.info("当前应用部署回滚包查找目录：%s", self.recover_dir)

    def start_app(self):
        server_port = ' --server.port=%s' % self.port
        server_active = ' --spring.profiles.active=%s' % ENVIRONMENT
        error_jvm_opt = ' -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=%s' % self.app_dir
        decrypt_opt = ' -Djasypt:decrypt -Djasypt.encryptor.password=%s' % ENCRYPTOR_PASSWORD
        nacos_opt = ' -Dspring.cloud.nacos.password=%s' % NACOS_PASSWORD
        nacos_addr = ' -Dspring.cloud.nacos.server-addr=%s' % NACOS_ADDR
        nacos_log = ' -Dnacos.logging.default.config.enabled=false'

        # 读取jvm_opt
        jvm_opt = ''
        jvm_opt_path = self.app_dir + '/jvm_opt'
        user_jvm_opt = self.execute_and_get('cat %s' % jvm_opt_path)
        if user_jvm_opt is not None:
            if '-Xms' not in user_jvm_opt and '-Xmx' not in user_jvm_opt:
                user_jvm_opt = DEFAULT_JVM_OPT + ' ' + user_jvm_opt
            jvm_opt = user_jvm_opt
        else:
            jvm_opt = DEFAULT_JVM_OPT
        # 如果不存在jvm_opt则写入默认配置
        if os.path.exists(jvm_opt_path) is False:
            self.execute('echo %s > %s;' % (jvm_opt, jvm_opt_path))
        jvm_opt = jvm_opt + error_jvm_opt

        log_path = self.app_dir + '/log/nohup.out'
        dir_name = os.path.dirname(log_path)
        if os.path.exists(dir_name) is False:
            os.makedirs(dir_name)

        # 读取java_opt
        java_opt = ''
        java_opt_path = self.app_dir + '/java_opt'
        user_java_opt = self.execute_and_get('cat %s' % java_opt_path)
        if user_java_opt is not None:
            if '--server.port' not in user_java_opt:
                user_java_opt = user_java_opt + server_port
            if '--spring.profiles.active' not in user_java_opt:
                user_java_opt = user_java_opt + server_active
            java_opt = user_java_opt
        else:
            java_opt = java_opt + server_port
            java_opt = java_opt + server_active
        # 如果不存在java_opt则写入默认配置
        if os.path.exists(java_opt_path) is False:
            self.execute('echo %s > %s;' % (java_opt, java_opt_path))

        jar_name = self.jar_file

        jar_opt = '-jar %s' % jar_name

        boot_command = 'nohup java %s %s %s %s %s %s %s' % (jvm_opt,decrypt_opt,nacos_addr,nacos_opt,nacos_log,jar_opt,java_opt)
        command = "cd %s; %s > %s 2>&1 &" \
                  % (self.app_dir, boot_command, log_path)
        log.debug("command: %s" % command)
        log.info('应用启动操作开始执行')
        self.execute(command)
        log.info('应用启动操作执行完成')

    def stop_app(self):
        pid = self.check_port()
        if pid is not None:
            log.info('检测应用在运行中, 开始结束应用进程，pid=%s' % pid)
            self.execute("kill -9 %s" % pid)
            log.info('已操作结束应用进程')
            self.check_end_status()
        else:
            log.info('未检测到正在运行的应用进程')

    def check_end_status(self):
        pid = None
        for i in range(1, TRY_CHECK_TIMES + 1):
            pid = self.check_port()
            if pid is None:
                self.execute('echo "" > %s/pid;' % self.app_dir)
                log.info('应用进程已结束')
                break
            else:
                time.sleep(1)
                log.info('检查进程状态中...%s' % i)
        if pid is not None:
            show_error('进程结束失败，可能是无权限停止，请手动停止应用pid：%s' % pid)

    def backup_app(self):
        try:
            backup_file_dir = self.backup_dir + '/' + self.today
            if not os.path.exists(backup_file_dir):
                os.makedirs(backup_file_dir)
                log.info('创建备份目录：%s' % backup_file_dir)
        except:
            pass

        if self.is_zip():
            zip_file_path = '%s/%s' % (backup_file_dir, self.backup_file)
            compress_webapp_zip_file(zip_file_path, self.app_dir, '')
        else:
            self.execute("mv %s/%s %s/%s" % (self.app_dir, self.package_name, backup_file_dir, self.backup_file))
        log.info("文件备份成功，备份位置：%s/%s" % (backup_file_dir, self.backup_file))

    def copy_jar(self):
        try:
            if not os.path.exists(self.app_dir):
                os.makedirs(self.app_dir)
                log.info('创建应用目录：%s' % self.app_dir)
        except:
            pass

        if self.is_zip():
            # 如果jar包打成zip, 则解压zip
            zip_path = '%s/%s' % (self.package_dir, self.package_name)
            extract_webapp_zip_file(zip_path, self.app_dir)
        else:
            self.execute("cp %s/%s %s" % (self.package_dir, self.package_name, self.app_dir))
        self.execute("chown %s %s/%s" % (LEGAL_OPERATOR, self.app_dir, self.package_name))
        self.execute("echo %s > %s/port;" % (self.port, self.app_dir))

    def stop_app_4_update(self):
        package_file = '%s/%s' % (self.package_dir, self.package_name)
        if os.path.exists(package_file) and (
                os.path.basename(package_file).endswith('.jar') or os.path.basename(package_file).endswith('.zip')):
            file_md5 = get_file_md5(package_file)
            file_ctime = time.ctime(os.path.getctime(package_file))
            log.info("当前发布包的MD5：%s", file_md5)
            log.info("当前发布包的创建时间：%s", file_ctime)
            self.stop_app()
        else:
            show_error('jar 或 zip发布包不存在：%s' % package_file)

    def update(self):
        for i in range(1, 999):
            num = str(i)
            day_str = self.today + num.zfill(3)
            backup_file_dir = self.backup_dir + '/' + self.today

            if self.is_zip():
                prefix = self.package_name.split('.zip')[0]
                self.backup_file = '%s_%s.zip' % (prefix, day_str)
            else:
                self.backup_file = '%s_%s' % (self.package_name, day_str)
            self.backup_file = self.backup_file.strip()
            if os.path.exists('%s/%s' % (backup_file_dir, self.backup_file)):
                pass
            else:
                self.stop_app_4_update()
                self.backup_app()
                self.copy_jar()
                self.start_app()
                self.check_status(can_rollback=True)
                break;

    def check_status(self, can_rollback=False):
        pid = None
        for i in range(1, WAIT_CHECK_SECOND + 1):
            log.info("等待应用启动...%s" % i)
            time.sleep(1)

        for i in range(1, TRY_CHECK_TIMES + 1):
            pid = self.check_port()
            if pid is not None:
                log.info("应用%s已成功启动，进程pid：%s" % (self.package_name, pid))
                self.execute('echo %s > %s/pid;' % (pid, self.app_dir))
                if can_rollback:
                    script_dir = '%s/package/deploy.py' % self.base_path
                    log.info("如需回滚，请执行：python %s -s %s -m %s -a rollback -pg %s -p %s -rf %s" %
                             (script_dir, self.project_name, self.app_name, self.package_name, self.port,
                              self.backup_file))
                break
            else:
                log.info("检查应用状态，暂未发现启动进程pid...%s" % i)
                time.sleep(1)
        if pid is None:
            log.info("应用包%s发布失败" % self.package_name)
            show_error("应用包%s发布失败" % self.package_name)
        return pid

    def check_port(self):
        jar = self.jar_file
        server_port = "port=" + self.port
        command = "ps -ef | grep %s | grep -v python | grep -v grep | grep %s | awk '{print $2}'" % (jar, server_port)
        # log.info('检查应用启动端口:%s' % command)
        pid = self.execute_and_get(command)
        return pid

    def recover_app(self):
        recover_str = self.recover_file.rsplit('_', 1)[1]
        file_day = recover_str[0:8]
        recover_file_path = self.recover_dir + ('/%s/%s' % (file_day, self.recover_file))
        if os.path.exists(recover_file_path):
            recover_package = self.app_dir + '/' + self.package_name
            if self.is_zip():
                extract_webapp_zip_file(recover_file_path, self.app_dir)
            else:
                self.execute('cp %s %s' % (recover_file_path, recover_package))
            log.info('回滚应用包%s到%s' % (recover_file_path, recover_package))
        else:
            show_error('回滚包不存在，查找路径为：%s' % recover_file_path)

    def rollback(self):
        self.stop_app()
        self.recover_app()
        self.start_app()
        self.check_status()

    def is_zip(self):
        is_zip = self.package_name.endswith(".zip")
        return is_zip

    def restart_app(self):
        self.stop_app()
        self.start_app()
        self.check_status()


class BaseFrontend(Shell):
    """
        前端部署操作类
    """

    def __init__(self, project_name, app_name, package_name, port, action, recover_file):
        self.today = datetime.datetime.now().strftime('%Y%m%d')

        # 项目名
        self.project_name = project_name

        # 应用名
        self.app_name = app_name

        # 包名
        self.package_name = package_name

        # 端口号
        self.port = port

        self.base_path = BASE_FRONTEND_DIR
        self.package_dir = BASE_PACKAGE_DIR
        self.app_dir = (self.base_path + '/%s') % self.app_name

        project_app = self.app_name

        self.backup_dir = self.base_path + ('/backup/%s' % project_app)
        self.backup_file = ''

        self.recover_dir = self.base_path + ('/backup/%s' % project_app)
        self.recover_file = recover_file

    def show_info(self):
        self.show_env()
        log.info("当前项目名：%s", self.project_name)
        log.info("当前应用名：%s", self.app_name)
        log.info("当前应用包名：%s", self.package_name)
        log.info("当前应用部署路径：%s", self.base_path + '/' + self.app_name)
        log.info("当前应用部署包存放路径：%s", self.package_dir)
        log.info("当前应用部署备份包存放目录：%s", self.backup_dir)
        log.info("当前应用部署回滚包查找目录：%s", self.recover_dir)

    def update(self):
        for i in range(1, 999):
            num = str(i)
            day_str = self.today + num.zfill(3)
            backup_file_dir = self.backup_dir + '/' + self.today
            self.backup_file = '%s_%s.zip' % (self.app_name, day_str)
            self.backup_file = self.backup_file.strip()
            if os.path.exists('%s/%s' % (backup_file_dir, self.backup_file)):
                pass
            else:
                self.backup_app()
                self.extract_app()
                break;

    def backup_app(self):
        backup_file_dir = self.backup_dir + '/' + self.today
        try:
            if not os.path.exists(backup_file_dir):
                os.makedirs(backup_file_dir)
                log.info('创建备份目录：%s' % backup_file_dir)
        except:
            pass
        # self.execute("mv %s/%s %s/%s" % (self.app_dir, self.app_name, backup_file_dir, self.backup_file))
        backup_file_path = backup_file_dir + os.path.sep + self.backup_file
        compress_zip_file(backup_file_path, self.app_dir, self.app_name)
        log.info("文件备份成功，备份位置：%s/%s" % (backup_file_dir, self.backup_file))

    def extract_app(self):
        package_file = self.package_dir + '/' + self.package_name
        if not os.path.exists(package_file):
            log.info('发布包不存在：%s' % package_file)
        file_md5 = get_file_md5(package_file)
        file_ctime = time.ctime(os.path.getctime(package_file))
        log.info("当前发布包的MD5：%s", file_md5)
        log.info("当前发布包的创建时间：%s", file_ctime)
        self.execute('chown %s %s' % (LEGAL_OPERATOR, package_file))
        if os.path.exists(self.app_dir):
            self.execute("rm -rf %s" % self.app_dir)
            log.info('已清除旧目录文件：%s' % self.app_dir)
        extract_zip_file(package_file, self.base_path)
        log.info('应用包%s已解压到%s' % (package_file, self.base_path))

        script_dir = '%s/package/deploy.py' % BASE_WEBAPP_DIR
        log.info("如需回滚，请执行：python %s -s %s -m %s -a rollback -pg %s -rf %s" %
                 (script_dir, self.project_name, self.app_name, self.package_name,
                  self.backup_file))

    def rollback(self):
        self.recover_app()

    def recover_app(self):
        day_str = self.recover_file.replace('.zip', '').split('_')[1]
        day = day_str[:8]
        recover_file_path = '%s/%s/%s' % (self.recover_dir, day, self.recover_file)
        if os.path.exists(recover_file_path):
            if os.path.exists(self.app_dir):
                self.execute("rm -rf %s" % self.app_dir)
                log.info('已清除旧目录文件：%s' % self.app_dir)
            extract_zip_file(recover_file_path, self.base_path)
            log.info('文件%s已解压到%s' % (recover_file_path, self.base_path))
        else:
            log.error('回滚包不存在：%s' % recover_file_path)


if __name__ == '__main__':
    usage = '''用法:
        后端部署：
        更新：
        \033[32m python deploy.py -s 系统名 -m 模块名 -a 操作 -pg 应用包名 -p 端口号\033[0m
        \033[32m python deploy.py -s qyzx -m qyzx-job -a update -pg qyzx-job-1.0.0.jar -p 8086\033[0m
        回滚：
        \033[32m python deploy.py -s 系统名 -m 模块名 -a 操作 -pg 应用包名 -p 端口号 -f 还原包名 \033[0m
        \033[32m python deploy.py -s qyzx -m qyzx-job -a rollback -pg qyzx-job-1.0.0.jar -p 8086 -rf qyzx-job-1.0.0.jar_20200218001\033[0m
        查看参数对应部署信息：
        \033[32m python deploy.py -s 系统名 -m 模块名 -a 操作 -pg 应用包名 -p 端口号 -c\033[0m
        \033[32m python deploy.py -s qyzx -m qyzx-job -a rollback -pg qyzx-job-1.0.0.jar -p 8086 -c\033[0m

        前端部署：
        更新：
        \033[32m python deploy.py -s 系统名 -m 模块名 -a 操作 -pg 应用包名\033[0m
        \033[32m python deploy.py -s qyzx -m qyzx-admin -a update -pg qyzx-admin.zip\033[0m
        回滚：
        \033[32m python deploy.py -s 系统名 -m 模块名 -a 操作 -pg 应用包名\033[0m
        \033[32m python deploy.py -s qyzx -m qyzx-admin -a rollback -pg qyzx-admin.zip -rf qyzx-admin_20200218001.zip\033[0m
        查看参数对应部署信息：
        \033[32m python deploy.py -s 系统名 -m 模块名 -a 操作 -pg 应用包名 -c\033[0m
        \033[32m python deploy.py -s qyzx -m qyzx-admin -a update -pg qyzx-admin.zip -c\033[0m
        '''

    arg_parser = argparse.ArgumentParser(usage=usage)
    arg_parser.add_argument("-s", help="sys_name", required='true', dest="sys_name")
    arg_parser.add_argument("-m", help="app_name", required='true', dest="app_name")
    arg_parser.add_argument("-a", help="action", required="true", dest="action",
                            choices=['update', 'rollback', 'stop', 'start', 'restart'])
    arg_parser.add_argument("-pg", help="package", required="true", dest="package")
    arg_parser.add_argument("-p", help="port", dest="port")
    arg_parser.add_argument("-rf", help="recover_file", dest="recover_file")
    arg_parser.add_argument("-c", help="check", dest="check", action="store_true")
    arg_parse = arg_parser.parse_args()

    sys_name = arg_parse.sys_name
    app_name = arg_parse.app_name
    action = arg_parse.action
    package = arg_parse.package
    port = arg_parse.port
    recover_file = arg_parse.recover_file
    check = arg_parse.check

    is_webapp = False
    if package.endswith(".jar"):
        is_webapp = True
        D = BaseWebapp(project_name=sys_name, app_name=app_name, package_name=package, port=port,
                       action=action, recover_file=recover_file)
        if port is None:
            show_error('-p 参数错误，部署后端应用，端口号必填')
    elif package.endswith('.zip'):
        if port is None:
            is_webapp = False
            D = BaseFrontend(project_name=sys_name, app_name=app_name, package_name=package, port=port,
                             action=action, recover_file=recover_file)
        else:
            is_webapp = True
            D = BaseWebapp(project_name=sys_name, app_name=app_name, package_name=package, port=port,
                           action=action,  recover_file=recover_file)
    else:
        show_error("-pg参数错误，应用包需以.jar/.zip结尾")

    # 检查执行者
    D.check_executor()
    if check:
        D.show_info()
        sys.exit(1)

    log = Logger(sys_name=sys_name, app_name=app_name).get_logger()

    # 显示包信息
    if is_webapp:
        D.show_info()
        if action == 'update':
            D.update()
        elif action == 'stop':
            D.stop_app()
        elif action == 'start' or action == 'restart':
            D.restart_app()
        elif action == 'rollback':
            if recover_file is not None:
                D.rollback()
            else:
                log.error('-rf 参数错误，缺少回滚包参数')
        else:
            log.error('-a 参数错误，操作类型必填')
    else:
        D.show_info()
        if action == 'update':
            D.update()
        elif action == 'rollback':
            if recover_file is not None:
                D.rollback()
            else:
                log.error('-rf 参数错误，缺少回滚包参数')
        else:
            log.error('-a 参数错误，操作类型必填')