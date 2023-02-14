// import './jquery.min.js'
// import './bootstrap.min.js'
import {Encryptor} from './crypt.js'

$(function () {
    var sshCRUDUrl = "/ssh";
    var connectUrl = "/ssh/connect";
    var publickeyUrl = "/publickey"

    loadSSHList();
    
    // 修改terminal的高度为body的高度
    // document.getElementById('terminal').style.height = (window.innerHeight * 0.8) + 'px';
    
    $('#new').on('show.bs.modal', function (event) {
        // do something...
    })

    $('#edit').on('show.bs.modal', function (event) {
        // do something...
        var $btngroup = $(event.relatedTarget.parentNode);
        var id = $btngroup.data('id');
        var modal = $(this)

        var enc = Encryptor();

        var url = sshCRUDUrl + '?token=' + encodeURIComponent(enc.encrypt(id))

        $.ajax({
            url,
            type: "GET",
            headers: {
                'auth': enc.auth
            },
            success: function (res) {
                if (res.code == 0) {
                    var item = enc.decrypt(res.data);
                    modal.find("#id").val(item.id);
                    modal.find(".name").val(item.name);
                    modal.find(".host").val(item.host);
                    modal.find(".port").val(item.port);
                    modal.find(".user").val(item.user);
                    modal.find(".password").val(item.password);
                }
            }
        });
    })

    $('.show-hide-password').click(function (e) {
        if ($(this).data('show')) {
            // $(this.parentNode.parentNode).find('#password').attr('type', 'text');
            $(this).parentsUntil('.modal').find('.password').attr('type', 'text');
            $(this).attr('title', '隐藏密码');
            $(this).find('span').removeClass('glyphicon-eye-open');
            $(this).find('span').addClass('glyphicon-eye-close');
            $(this).data('show', 0)
        }
        else {
            $(this).parentsUntil('.modal').find('.password').attr('type', 'password');
            $(this).attr('title', '显示密码');
            $(this).find('span').removeClass('glyphicon-eye-close');
            $(this).find('span').addClass('glyphicon-eye-open');
            $(this).data('show', 1)
        }

    })

    // $('.edit').click(function(e){
    //     console.log(e);
    //     console.log(this)
    // })

    function checkInput(modal) {
        var result = {
            status: 0,
            data: new Object()
        }
        var $name = modal.find('.name');
        var $host = modal.find('.host');
        var $port = modal.find('.port');
        var $user = modal.find('.user');
        var $password = modal.find('.password');
        $.each([$name, $host, $port, $user, $password], function (i, ele) {
            var key = ele.attr('name');
            var value = ele.val();
            if (!value) {
                ele.parent().parent().addClass('has-error')
                result.status = 1
            } else {
                result.data[key] = value
            }
        });
        return result;
    }

    function loadSSHList(q) {
        var url = q? sshCRUDUrl + '?q=' + q: sshCRUDUrl;
        var enc = Encryptor();
        $.ajax({
            url: url,
            type: "GET",
            headers: {
                'auth': enc.auth
            },
            success: function (res) {
                
                if (res.code == 0) {
                    var data = enc.decrypt(res.data)
                    $('#ssh-list').html('');
                    $.each(data, function (i, item) {
                        // $('#ssh ul').append('<li class="list-group-item" data-id="' + item.id + '">' + item.name + '</li>')
                        $('#ssh-list').append(
                            `<div class="col-md-3">
                                <div class="ssh-item" style="padding-bottom: 20px;">
                                    <div class="btn-group" data-id=` + item.id + ` data-name=` + item.name + ` data-host=` + item.host + ` data-port=` + item.port + ` data-user=` + item.user + ` data-password=` + item.password + `>
                                        <button type="button" class="btn conn btn-sm">
                                            <span class="glyphicon glyphicon-grain"></span><span>` + item.ellipsis + `</span>
                                        </button>
                                        <button type="button" class="btn btn-default btn-sm edit hide" data-toggle="modal" data-toggle="tooltip" data-target="#edit" data-placement="top" title="编辑">
                                            <span class="glyphicon glyphicon-edit"></span>
                                        </button>
                                        <button type="button" class="btn btn-default btn-sm csl hide" data-toggle="tooltip" data-placement="top" title="连接">
                                            <span class="glyphicon glyphicon-console"></span>
                                        </button>
                                        <button type="button" class="btn btn-default btn-sm trash hide" data-toggle="tooltip" data-placement="top" title="删除">
                                            <span class="glyphicon glyphicon-trash"></span>
                                        </button>
                                    </div>
                                </div>
                            </div>`
                        )
                    })
                }
            }
        });
    }

    $(".save").click(function () {
        var modal = $(this).parentsUntil('.modal')

        var checkResult = checkInput(modal);
        console.log(checkResult)
        if (checkResult.status === 1) {
            return
        }
        var id = $("#id").val();
        var $btn = $(this).button('loading');
        var requestType = "POST";
        if (id) {
            requestType = "PUT";
            checkResult.data['id'] = id
        }
        var enc = Encryptor();
        var token = enc.encrypt(JSON.stringify(checkResult.data))
        $.ajax({
            url: sshCRUDUrl,
            type: requestType,
            data: JSON.stringify({ token }),
            dataType: "json",
            headers: {
                'auth': enc.auth,
            },
            contentType: "application/json; charset=utf-8",
            success: function (res) {
                if (res.code == 0) {
                    $btn.button('reset');
                    $('#ssh div[class~=form-group]').removeClass('has-error')
                    loadSSHList();
                }
            }
        });
    });

    var terminals = new Object();

    $('.console').click(function () {

        var modal = $(this).parentsUntil('.modal')

        var checkResult = checkInput(modal);
        console.log(checkResult);
        if (checkResult.status === 1) {
            return
        }
        var $btn = $(this).button('loading');
        var id = nanoid(32);

        var termWindow = window.open(window.location.href + "ssh/connect", id);
        terminals[id] = { data: checkResult.data, termWindow };
        $btn.button('reset');

    });

    

    $(document).on('click', '.csl', function () {

        var conn = $(this).parent().data()
        var $btn = $(this).button('loading');
        var id = nanoid(32);
        var termWindow = window.open(window.location.href + "ssh/connect", id);
        terminals[id] = { data: conn, termWindow };
        $btn.button('reset');
    })

    $(document).on('click', '.trash', function () {

        var conn = $(this).parent().data()
        var $btn = $(this).button('loading');

        
        if (conn.id){
            if (confirm('将删除 ' + conn.name + '(' + conn.user + '@' + conn.host + ':' + conn.port + ')'))
            {
                deleteSSH(conn.id);
                console.log('delete ' + JSON.stringify(conn))
            }
            else{
                console.log('cancel')
            }
        }
        $btn.button('reset');
    })

    $('#ssh-list').on('mouseover', '.conn', function () {
        $(this).siblings('button').each(function (i, e) {
            $(e).removeClass('hide');
        })
    })
    $('#ssh-list').on('click', '.conn', function () {
        var conn = $(this).parent().data();
    })
    $('#ssh-list').on('mouseleave', 'div', function () {
        $(this).find('button').each(function (i, e) {
            if (i !== 0){
                $(e).addClass('hide');
            }
        })
    })

    window.addEventListener("message", e => {
        if (e.data == 'load') {
            terminals[e.source.name].termWindow.postMessage(JSON.stringify(terminals[e.source.name].data), "*");
        }
        console.log(e);
        // else if (e.data == 'unload') {
        //     delete terminals[e.source.name]
        // }
    });

    $("#delete").click(function () {
        var modal = $(this).parentsUntil('.modal')
        var id = modal.find('#id').val();
        if (id) {
            deleteSSH(id);
        }
    });

    function deleteSSH(id) {
        var enc = Encryptor();
        var token = enc.encrypt(JSON.stringify({ id }))
        
        var $btn = $(this).button('loading');
        $.ajax({
            url: sshCRUDUrl,
            type: 'DELETE',
            data: JSON.stringify({ token }),
            dataType: "json",
            headers: {
                'auth': enc.auth,
            },
            contentType: "application/json; charset=utf-8",
            success: function (res) {
                if (res.code == 0) {
                    $btn.button('reset');
                    // $('#ssh div[class~=form-group]').removeClass('has-error')
                    $("#edit").modal('hide');
                    loadSSHList();
                }
            }
        });
    }

    $("#search").click(function () {
        var searchText = $("#searchText").val();
        loadSSHList(searchText);
    });

    $('#searchText').bind('keydown', function (event) {
        if(event.keyCode == "13")    
        {
            var searchText = $("#searchText").val();
            loadSSHList(searchText);
        }
    })

    $("#ssh ul").on('click', 'li', function () {
        $("#ssh li").removeClass('active');
        this.setAttribute('class', this.getAttribute('class') + ' active');
        $('#ssh div[class~=form-group]').removeClass('has-error')
        var id = this.getAttribute('data-id')
        if (id) {
            // var $p = $('<p id="name" class="form-control-static" style="text-indent: 12px;"></p>')
            // $('#name').replaceWith($p)
            $("#id").val(id);
            $("#delete").removeClass('hide')

            var enc = Encryptor();

            var url = sshCRUDUrl + '?token=' + encodeURIComponent(enc.encrypt(id))
            $.ajax({
                url,
                type: "GET",
                headers: {
                    'auth': enc.auth
                },
                success: function (res) {
                    var data = enc.decrypt(res);
                    if (data.code == 0) {
                        var item = data.data;
                        $("#name").val(item.name);
                        $("#host").val(item.host);
                        $("#port").val(item.port);
                        $("#user").val(item.user);
                        $("#password").val(item.password);
                    }
                }
            });

        } else {
            // var $input = $('<input class="form-control" id="name" type="text">')
            // $('#name').replaceWith($input).val('');

            $("#id").val('');
            $("#name").val('');
            $("#host").val('');
            $("#port").val('22');
            $("#user").val('');
            $("#password").val('');
            $("#delete").addClass('hide');
        }
    });

    function openTab(conn) {
        var id = nanoid(32);
        var sshInfo = conn.user + '@' + conn.host + ':' + conn.port
        var newli = `
        <li style="padding: 0;" role="presentation" class="active col-md-1" data-toggle="tooltip" data-placement="top" title="` + conn.name + `">
            <a style="padding: 6px 0 4px 0;; overflow: hidden; text-overflow: ellipsis;" href="#` + id + `" aria-controls="`+ id +`" role="tab" data-toggle="tab">`+conn.name+`</span></a>
        </li>`

        $('.nav-tabs li').each(function (i, e) {
            $(e).removeClass('active')
            $(e).find('button').eq(0).removeClass('btn-success')
            $(e).find('button').eq(0).addClass('btn-default')
        })
        $(newli).insertBefore($('.nav-tabs li').eq(-1));

        $('.tab-content div').each(function (i, e) {
            $(e).removeClass('active')
        })
        var newdiv = `<div role="tabpanel" class="tab-pane active" id=` + id + `><div id="terminal-`+ id + `"></div></div>`;
        $('.tab-content').append(newdiv);

        document.getElementById('terminal-' + id).style.height = (window.innerHeight * 0.7) + 'px';

        const term = new Terminal({
            cursorStyle: 'underline',  //光标样式
            cursorBlink: true,  //光标闪烁
        });
        const fitAddon = new FitAddon.FitAddon();

        term.focus();
        term.open(document.getElementById('terminal-' + id));
        term.loadAddon(fitAddon);
        fitAddon.fit();

        var enc = Encryptor();
        var token = enc.encrypt(JSON.stringify(conn))
        document.cookie = 'session=' + enc.auth + '; path=/';
        
        // document.title = conn.user + '@' + conn.host + ':' + conn.port
        var ws = new WebSocket("ws://127.0.0.1:8000/ssh/connect?token=" + encodeURIComponent(token) + '&cols=' + term.cols + '&rows=' + term.rows); 
        //申请一个WebSocket对象，参数是服务端地址，同http协议使用http://开头一样，WebSocket协议的url使用ws://开头，另外安全的WebSocket协议使用wss://开头
        ws.onopen = function(){
            //当WebSocket创建成功时，触发onopen事件
            console.log("open");
        }
        ws.onmessage = function(e){
            //当客户端收到服务端发来的消息时，触发onmessage事件，参数e.data包含server传递过来的数据
            term.write(e.data);
        }
        ws.onclose = function(e){
            //当客户端收到服务端发送的关闭连接请求时，触发onclose事件
            alert('连接关闭\n原因: ' + e.reason)
            console.log("close");
        }
        ws.onerror = function(e){
            //如果出现连接、处理、接收、发送数据失败的时候触发onerror事件
            console.log(error);
        }

        term.onData(function(s){
            ws.send(JSON.stringify({"input": s}))
        });

        window.onresize = function () {
            document.getElementById('terminal-' + id).style.height = (window.innerHeight * 0.7) + 'px';
            // document.getElementById('terminal').style.width = window.innerWidth + 'px';
            fitAddon.fit();
        }

        term.onResize(function (size) {
            ws.send(JSON.stringify({
            'resize': [size.cols, size.rows]
            }));
        })
    }
});