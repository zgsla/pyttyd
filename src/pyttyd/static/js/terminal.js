
import {Encryptor} from './crypt.js'

// 修改terminal的高度为body的高度
document.getElementById('terminal').style.height = (window.innerHeight * 0.999) + 'px';
// document.getElementById('terminal').style.width = window.innerWidth + 'px';

var opened = false;

window.addEventListener('message', ev => {
    console.log(ev.data)
    if (!opened) {
        var conn = JSON.parse(ev.data);
        // xterm docs https://xtermjs.org/docs/api/terminal/classes/terminal/
        const term = new Terminal({
            cursorStyle: 'underline',  //光标样式
            cursorBlink: true,  //光标闪烁
        });
        const fitAddon = new FitAddon.FitAddon();

        term.focus();
        term.open(document.getElementById('terminal'));
        term.loadAddon(fitAddon);
        fitAddon.fit();
        
        var enc = Encryptor();
        var token = enc.encrypt(JSON.stringify(conn))

        document.cookie = 'session=' + enc.auth + '; path=/';

        document.title = conn.name ? conn.name + '(' + conn.user + '@' + conn.host + ':' + conn.port + ')': conn.user + '@' + conn.host + ':' + conn.port
        var ws = new WebSocket("ws://127.0.0.1:8221/ssh/connect?token=" + encodeURIComponent(token) + '&cols=' + term.cols + '&rows=' + term.rows); 
        //申请一个WebSocket对象，参数是服务端地址，同http协议使用http://开头一样，WebSocket协议的url使用ws://开头，另外安全的WebSocket协议使用wss://开头
        ws.onopen = function () {
            //当WebSocket创建成功时，触发onopen事件
            console.log("open");
        }
        ws.onmessage = function (e) {
            //当客户端收到服务端发来的消息时，触发onmessage事件，参数e.data包含server传递过来的数据
            term.write(e.data);
        }
        ws.onclose = function (e) {
            //当客户端收到服务端发送的关闭连接请求时，触发onclose事件
            alert('连接关闭\n原因: ' + e.reason)
            console.log("close");
        }
        ws.onerror = function (e) {
            //如果出现连接、处理、接收、发送数据失败的时候触发onerror事件
            console.log(error);
        }

        term.onData(function (s) {
            ws.send(JSON.stringify({ "input": s }))
        });

        window.onresize = function () {
            document.getElementById('terminal').style.height = (window.innerHeight * 0.999) + 'px';
            // document.getElementById('terminal').style.width = window.innerWidth + 'px';
            fitAddon.fit();
        }

        term.onResize(function (size) {
            ws.send(JSON.stringify({
                'resize': [size.cols, size.rows]
            }));

        })
        opened = true;
    }
})

window.addEventListener('load', () => {
    window.opener.postMessage('load');
})

window.addEventListener('unload', () => {
    window.opener.postMessage('unload');
})
