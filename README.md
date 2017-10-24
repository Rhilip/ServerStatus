# ServerStatus中文版：   

* ServerStatus中文版是一个酷炫高逼格的云探针、云监控、服务器云监控、多服务器探针~，该云监控（云探针）是ServerStatus（ https://github.com/BotoX/ServerStatus ）项目的中文（优化）版。
* 在线演示：https://tz.cloudcpp.com    

# 目录介绍：

* clients-linux.py  客户端文件
* server            服务端文件
* web               网站文件  

# 更新说明：

* 20171024，在上游基础上，修改client-linux.py代码，使其支持客户端以IPv6的形式连接SERVER。移除没有用的自动部署autodeploy以及跨平台client-psutil
---------
* 20170807，更新平均1，5，15负载
* 20170108, 更新支持所有系统
* 20161205, 去掉无用的IPV6信息，增加服务器总流量监控                          

# 安装教程：     
   
【克隆代码】:
```
git clone https://github.com/tenyue/ServerStatus.git
```

【服务端配置】（服务端程序在ServerStatus/web下）:  
          
一、生成服务端程序              
```
cd ServerStatus/server
make
./sergate
```
如果没错误提示，OK，ctrl+c关闭；如果有错误提示，检查35601端口是否被占用    

二、修改配置文件         
修改config.json文件，注意username, password的值需要和客户端对应一致                 
```
{"servers":
	[
		{
			"username": "s01",
			"name": "Mainserver 1",
			"type": "Dedicated Server",
			"host": "GenericServerHost123",
			"location": "Austria",
			"password": "some-hard-to-guess-copy-paste-password"
		},
	]
}       
```

三、拷贝ServerStatus/status到你的网站目录        
例如：
```
sudo cp -r ServerStatus/web/* /home/wwwroot/default
```

四、运行服务端：             
web-dir参数为上一步设置的网站根目录，务必修改成自己网站的路径   
```
./sergate --config=config.json --web-dir=/home/wwwroot/default   
```

【客户端配置】（客户端程序为client-linux.py）：           
1、vim client-linux.py, 修改SERVER地址，username帐号， password密码        
2、python client-linux.py 运行即可。
```
请注意，client-linux仅支持py2.7以上版本，centos 6请自行安装py2.7或py3
```

打开云探针页面，就可以正常的监控。接下来把服务器和客户端脚本自行加入开机启动，或者进程守护，或以后台方式运行即可！例如： nohup python client-linux.py &      

# 为什么会有ServerStatus中文版：

* 有些功能确实没用
* 原版本部署，英文说明复杂
* 不符合中文版的习惯
* 没有一次又一次的轮子，哪来如此优秀的云探针

# 相关开源项目，感谢： 

* ServerStatus中文版：https://github.com/tenyue/ServerStatus
* ServerStatus：https://github.com/BotoX/ServerStatus
* mojeda: https://github.com/mojeda 
* mojeda's ServerStatus: https://github.com/mojeda/ServerStatus
* BlueVM's project: http://www.lowendtalk.com/discussion/comment/169690#Comment_169690
