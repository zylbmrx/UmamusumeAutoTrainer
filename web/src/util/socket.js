class webSocketClass {
    constructor() {
        let that = this;
        this.webSocket = null;  //websocket实例
        this.isConnect = false; //连接状态
        this.globalCallback = function (e) {
            console.log(e)
        };//定义外部接收数据的回调函数
        this.globalFirstConnectFunc = function (e) {
            console.log(e)
        }//定义首次连接成功的回调函数
        this.reConnectNum = 0;//重连次数
        this.websocketUrl = "ws://localhost:8071/ws";

        //心跳设置
        this.heartCheck = {
            heartbeatData: {
                msgType: 'ping'
            },//心跳包
            timeout: 60 * 1000, //每段时间发送一次心跳包 这里设置为60s
            heartbeat: null, //延时发送消息对象（启动心跳新建这个对象，收到消息后重置对象）
            start: function () {
                this.heartbeat = setInterval(() => {
                    if (that.isConnect) {
                        console.log("发送心跳包");
                        that.webSocketSendJson(this.heartbeatData);
                    } else {
                        this.clear();
                    }
                }, this.timeout);
            }, reset: function () {
                clearInterval(this.heartbeat);
                this.start();
            }, clear: function () {
                clearInterval(this.heartbeat);
            }
        }
    }


//初始化websocket
    initWebSocket(websocketUrl, callback = null, firstConnectFunc = null) {
        let that = this;
        if (websocketUrl) {
            this.websocketUrl = websocketUrl
        }

        //此callback为在其他地方调用时定义的接收socket数据的函数
        if (callback) {
            if (typeof callback == 'function') {
                this.globalCallback = callback
            } else {
                throw new Error("callback is not a function")
            }
        }
        console.log(websocketUrl)
        console.log(firstConnectFunc)

        if (firstConnectFunc) {
            if (typeof firstConnectFunc == 'function') {
                this.globalFirstConnectFunc = firstConnectFunc
            } else {
                throw new Error("firstConnectFunc is not a function")
            }
        }

        if ("WebSocket" in window) {
            this.webSocket = new WebSocket(this.websocketUrl);//创建socket对象
        } else {
            console.log("该浏览器不支持websocket!");
            return
        }
        //打开
        this.webSocket.onopen = function () {
            that.webSocketOpen(firstConnectFunc);
        };
        //收信

        this.webSocket.onmessage = function (e) {
            that.webSocketOnJsonMessage(e);
            that.heartCheck.reset();
        };
        //关闭
        this.webSocket.onclose = function (e) {
            that.webSocketOnClose(e);
        };
        //连接发生错误的回调方法
        this.webSocket.onerror = function (e) {
            that.webSocketonError(e);
        };
    }

//连接socket建立时触发
    webSocketOpen() {
        console.log("WebSocket连接成功");
        //首次握手
        this.webSocketSendJson(this.heartCheck.heartbeatData);
        this.isConnect = true;
        this.heartCheck.start();
        this.reConnectNum = 0;
        this.globalFirstConnectFunc();
    }

//客户端接收服务端数据时触发,e为接受的数据对象
    webSocketOnJsonMessage(e) {
        // console.log("websocket信息:");
        // console.log(e.data)
        const data = JSON.parse(e.data);//根据自己的需要对接收到的数据进行格式化
        this.globalCallback(data);//将data传给在外定义的接收数据的函数，至关重要。
    }

//socket关闭时触发
    webSocketOnClose(e) {
        let that = this;
        this.heartCheck.clear();
        this.isConnect = false; //断开后修改标识
        console.log(e)
        console.log('webSocket已经关闭 (code：' + e.code + ')')
        //被动断开，重新连接
        if (e.code === 1006) {
            if (this.reConnectNum < 9) {
                setTimeout(function () {
                    that.initWebSocket(that.websocketUrl);
                    ++that.reConnectNum;
                    console.log('第' + that.reConnectNum + '次重连')
                }, this.reConnectNum * 2000);


            } else {
                console.log('websocket连接不上')
            }
        }
    }

//连接发生错误的回调方法
    webSocketonError(e) {
        this.heartCheck.clear();
        this.isConnect = false; //断开后修改标识
        console.log("WebSocket连接发生错误:");
        console.log(e);
    }


//发送数据
    webSocketSend(data) {
        this.webSocket.send(data);
    }

    webSocketSendJson(data) {
        this.webSocket.send(JSON.stringify(data));//在这里根据自己的需要转换数据格式
    }

//在其他需要socket地方主动关闭socket
    closeWebSocket(e) {
        this.webSocket.close();
        this.heartCheck.clear();
        this.isConnect = false;
        this.reConnectNum = 0;
    }

}

var webSocketMap = new Map();

function initWebSocket(websocketUrl, callback = null, firstConnectFunc = null) {
    if (websocketUrl === null || websocketUrl === undefined || websocketUrl === "") {
        return null;
    }

    if (webSocketMap.has(websocketUrl)) {
        return webSocketMap.get(websocketUrl);
    }
    let webSocket = new webSocketClass();
    webSocket.initWebSocket(websocketUrl, callback, firstConnectFunc);
    webSocketMap.set(websocketUrl, webSocket);
    return webSocket;
}


export default {
    initWebSocket
};