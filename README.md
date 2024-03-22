# Pyttyd
*Python开发的web分享终端的工具*

### 安装

```commandline
$ pip install pyttyd
```

### 启动服务

```commandline
$ pyttyd
```

浏览器访问 [http://127.0.0.1:8221](http://127.0.0.1:8221)


### 说明
[xterm.js](https://github.com/xtermjs/xterm.js)制作终端效果展示  
[uvicorn](https://github.com/encode/uvicorn)+[FastApi](https://github.com/tiangolo/fastapi)提供http服务  
[websockets](https://github.com/aaugustin/websockets)实现web终端与pty交互

把终端分享到网页是**不安全**的，请小心使用。

### 更好的相关工具
c [ttyd](https://github.com/tsl0922/ttyd)  
go [gotty](https://github.com/yudai/gotty)
