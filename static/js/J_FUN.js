(function(window,undefined){

    //添加删除数组中某一个值的方法
    Array.prototype.removeFromArr = function(val){
        var index = this.indexOf(val);
        //index不等于-1 说明数组中存在这一项
        if (index > -1) {
            this.splice(index, 1);
        }
    }

    //数组去重
    Array.prototype.unique = function(){
        var res = [];
        var json = {};
        for(var i = 0; i < this.length; i++){
            if(!json[this[i]]){
                res.push(this[i]);
                json[this[i]] = 1;
            }
        }
        return res;
    }

    //处理IE低版本浏览器不兼容数组indexOf方法
    if(!Array.indexOf){
        Array.prototype.indexOf = function(obj){
            for(var i=0; i<this.length; i++){
                if(this[i]==obj){
                    return i;
                }
            }
            return -1;
        }
    }

    //定义gy对象
    var Common = {};

    window.J_FUN = Common;//向window暴露Common对象
    //返回字符串字节的长度 英文字符为一个字节 汉字为两字节
    Common.strLength = function (str) {
        if (str == null) return 0;
        if (typeof str != "string"){
            str += "";
        }
        //这里是将双字节的字符替换成“01” 然后获取字符串的长度
        return str.replace(/[^x00-xff]/g,"01").length;
    }
    Common.getClassName = function(element){
        return element.className.replace(/\s+/, ' ').split(' ');
    }

    Common.hasClassName = function(element,className){
        var classes = this.getClassName(element);
        for (var i = 0; i < classes.length; i++) {
            if (classes[i] === className) {
                return true;
            }
        }
        return false;
    }

    Common.addClassName = function(element,className){
        element.className += (element.className ? ' ' : '') + className;
    }

    Common.removeClassName = function(element,className){
        var classes = this.getClassName(element);
        var length = classes.length
        for (var i = length - 1; i >= 0; i--) {
            if (classes[i] === className) {
                delete(classes[i]);
            }
        }
        //由于在getClassNames中移除了空格 取得了数组 所以要重新用空格分隔
        element.className = classes.join(' ');
    }

    // 移除指定节点
    Common.removeNode = function(node){
        node.parentNode.removeChild(node);
    }

    // 移除所有子节点
    Common.removeAllChild = function(parent){
        //移除所有子节点
        while (parent.firstChild) {
            parent.firstChild.parentNode.removeChild(parent.firstChild);
        }
        return parent;
    }
    //js事件绑定方法
    //三个参数①绑定事件的对象 ② 事件类型 ③事件处理函数
    Common.addEvent = function (node,type,listener){
                        if (node.addEventListener) {
                    node.addEventListener(type, listener, false);
                    return true;
                } else if (node.attachEvent) {
                    node['e' + type + listener] = listener;
                    node[type + listener] = function() {
                        node['e' + type + listener](window.event);
                    }
                    node.attachEvent('on' + type, node[type + listener]);
                    return true;
                }
                return false;
                    }
    //js移除绑定方法
    Common.removeEvent = function (node,type,listener){
			if (node.removeEventListener) {
                    node.removeEventListener(type, listener, false);
                    return true;
                } else if (node.detachEvent) {
                    if(type && node[type + listener]){
                        node.detachEvent('on' + type, node[type + listener]);
                        node[type + listener] = null;
                    }
                    return true;
                }
                return false;
    }
    //获取所有子元素节点 返回节点的集合
    Common.getChildren = function (oParent) {
                        var aResult = []; //存放查找的节点
                        var aChild = oParent.childNodes; //获取所有的节点 包括 元素节点 属性节点 文本节点
                        var i = 0;
                        var alength = aChild.length;
                        for (i; i < alength; i++) {

                            if (aChild[i].nodeType === 1) { //节点类型为1的话就是元素节点
                                aResult.push(aChild[i]);
                            }
                        }
                        return aResult; //返回元素节点的集合
                    }
    //通过ID名找元素
    Common.getById = function(id){
        return document.getElementById(id);
    }
    //通过类名找元素 返回元素集合
    //传两个参数 ①要查找的类名 ②obj就是找的标签范围（父级元素）;
    Common.getElementsByClass = function  (sClass,obj) {
        var _this = this;
        //如果obj没有参数传进来的话就为假,就返回document;
        var obj = obj || document;
        var arr=[];//设置一个数组来存要查找类名的元素;

        //判断浏览器有没有getElementsByClassName方法
        if(obj.getElementsByClassName){
            return obj.getElementsByClassName(sClass) //存在就直接调用此方法
        }else{
            var alls = obj.getElementsByTagName("*");//首先找到页面所有的标签;
            for (var i=0; i<alls.length; i++) {
                if(_this.hasClassName(alls[i].className,sClass)){//回调函数判断类名,因为同一标签可能有多个类名;
                    arr.push(alls[i])//如果是真的,就把这个元素推进数组里面;
                }
            }
            return arr;
        }
    }

    //去掉字符串前后的引号
    Common.removeYinhao = function(str){
        return  str.replace(/^\"|\"$/g, "");
    }
    //封装innerText方法
    Common.innerText = function (element) {
        return (typeof element.textContent == "string") ? element.textContent : element.innerText;
    }
    //将xml字符串转换为xml文档 返回xml文档
    Common.parseXML = function ( data ) {
        var xml, tmp;
        try {
            if ( window.DOMParser ) { // 标准浏览器
                tmp = new DOMParser();
                xml = tmp.parseFromString( data , "text/xml" );
            } else { // IE
                xml = new ActiveXObject( "Microsoft.XMLDOM" );
                xml.async = "false";
                xml.loadXML( data );
            }
        } catch( e ) {
            xml = undefined;
        }
        if ( !xml || !xml.documentElement || xml.getElementsByTagName( "parsererror" ).length ) {
            throw new Error( "Invalid XML: " + data );
        }
        return xml;
    }
    //将html字符串转换为html文档 返回html文档
    Common.parseHTML = function ( data ) {
        var htmlString ;
        //创建div
        var oDiv = document.createElement('div');
        //把字符串添加到oDiv里这样就成dom对象了
        oDiv.innerHTML = data;
        //然后获取到添加进去的文档
        htmlString = this.getChildren(oDiv)[0];
        //删除没用的oDiv对象
        oDiv = null;
        delete  oDiv;
        //返回转换之后的dom对象
        return htmlString;
    }
    //获取xml文档指定节点的文本 返回文本
    //只适用xml文档
    Common.getxmlnodeText = function (oNode) {
                            if (this.is_IE()) {
                                return this.removeYinhao(oNode.text);  //并且移除前后的引号
                            } else {
                                if (oNode.nodeType ==1)
                                    return this.removeYinhao(oNode.textContent);
                            }
                        }
    //获取xml文档指定节点的属性值
    //只适用xml文档
    Common.getxmlnodeattribute = function (oNode, attrName) {
        if (this.is_IE()) {
            return oNode.getAttribute(attrName);
        } else {
            if (oNode.nodeType == 1 || oNode.nodeType == "1")
                return oNode.attributes[attrName].value;
            return"undefined";
        }
    }
    //判断是不是IE浏览器 是返回true 不是返回false
    Common.is_IE = function (){
                if (window.ActiveXObject) { //ActiveXObject对象为IE独有
                    return true;
                }
                return false;
            }
    //封装ajax请求方法
    //两个参数①url地址 ②请求成功后的回调函数
    Common.getXmlHttpRequest = function (url,callback) {
        var xmlhttp;
        if (window.XMLHttpRequest) {// code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp=new XMLHttpRequest();
        }
        else{// code for IE6, IE5
            xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
        }
        //注册回调函数
        xmlhttp.onreadystatechange = function() {
            //接收响应数据
            //判断对象状态是否交互完成，如果为4则交互完成
            if(xmlhttp.readyState == 4) {
                //判断对象状态是否交互成功,如果成功则为200
                if(xmlhttp.status == 200) {
                    //接收数据,得到服务器输出的纯文本数据
                    var response = xmlhttp.responseText;
                    //得到的response为字符串
                    //将得到的xmlDoc转换为xml文档
                    var xmlDoc = gy.parseXML(response);
                    //执行回调函数
                    callback(xmlDoc);

                }
            }
        };
        //1.是http请求的方式
        //2.是服务器的地址
        //3.是采用同步还是异步，true为异步
        //xmlhttp.open("GET",url,true);
        //post请求与get请求的区别
        //第一个参数设置成post第二个只写url地址，第三个不变
        xmlhttp.open("GET",url,true);
        //post请求要自己设置请求头
        //xmlhttp.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
        //发送数据，开始与服务器进行交互
        //post发送请求
        xmlhttp.send(null);
    }
    //清除字符串前后空格
    Common.trimAll = function(str){
        return str.replace(/(^\s+)|(\S+$)/g ,"");
    }
    //获得事件对象
    Common.getEvent = function (e) {
                        return e || window.event;
                    }
    //获取事件目标
    Common.getTarget = function (e) {
                        return this.getEvent(e).target || this.getEvent(e).srcElement;
                    }
    //阻止事件冒泡
    Common.stopPropagation = function (e) {
                                 if (window.event) {
                                         return this.getEvent(e).cancelBubble = true;
                                     } else {
                                         return arguments.callee.caller.arguments[0].stopPropagation();
                                     }
                            }
    //阻止浏览器默认行为
    Common.preventDefault = function (e) {
                 if (window.event) {
                         return this.getEvent().returnValue = false;
                     } else {
                         return arguments.callee.caller.arguments[0].preventDefault();
                     }
             }
    //获取cookie
    Common.getCookie = function (c_name){
        if (document.cookie.length>0){　　//先查询cookie是否为空，为空就return ""
            c_start=document.cookie.indexOf(c_name + "=")　　//通过String对象的indexOf()来检查这个cookie是否存在，不存在就为 -1　　
            if (c_start!=-1){
                c_start=c_start + c_name.length+1　　//最后这个+1其实就是表示"="号啦，这样就获取到了cookie值的开始位置
                c_end=document.cookie.indexOf(";",c_start)　　//其实我刚看见indexOf()第二个参数的时候猛然有点晕，后来想起来表示指定的开始索引的位置...这句是为了得到值的结束位置。因为需要考虑是否是最后一项，所以通过";"号是否存在来判断
                if (c_end==-1) c_end=document.cookie.length
                return unescape(document.cookie.substring(c_start,c_end))　　//通过substring()得到了值。想了解unescape()得先知道escape()是做什么的，都是很重要的基础，想了解的可以搜索下，在文章结尾处也会进行讲解cookie编码细节
            }
        }
        return ""
    }
    //设置cookies
    //使用方法：setCookie('username','Darren',30)
    Common.setCookie = function (c_name, value, expiredays){
         　　　　var exdate=new Date();
         　　　　exdate.setDate(exdate.getDate() + expiredays);
         　　　　document.cookie=c_name+ "=" + escape(value) + ((expiredays==null) ? "" : ";expires="+exdate.toGMTString());
         　　}
     　　
})(window);