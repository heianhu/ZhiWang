var allType = document.getElementById("J_search_option").getElementsByTagName("ul");  //  获取所有可选项容器（一个ul就是一个类型）
var allTypeLength = allType.length;  // 得到类型总数
var allOption = document.getElementById("J_search_option").getElementsByTagName("li");  //  获取所有可选项
var allOptionLength = allOption.length;  //  所有可选项的总数
var hasChoosedContain = document.getElementById(" J_search_condition"); // 选择项容器
var clearBtn = getLastChild(hasChoosedContain);  // 清空筛选按钮

/**********
 * 初始化index值，给每个选项(即li)的index属性赋值一个数组[x,y];
 * x: 表示当前是第x个类型（ul）
 * y: 表示第y个选项（ul下的第几个li）
 *********/
initIndex();
function initIndex(){
    var i= 0;
    for(; i<allTypeLength; i++){
        var nowType = allType[i];
        var nowOptions = nowType.getElementsByTagName('li');
        var nowOptionsLength = nowOptions.length;
        var j= 0;
        for(;j<nowOptionsLength; j++){
            nowOptions[j].index = new Array(i,j);
        }
    }
}
/**********
 * 得到index值，当前选项(即li)的index值数组[x,y];
 * x: 表示当前是第x个类型（ul）
 * y: 表示第y个选项（ul下的第几个li）
 *********/
 function getIndex(ele){
    return ele.index;
 }

/*********
 * 得到选项文本信息
 * @param index [arr]
 ********/
 function getText(index){
    return J_FUN.innerText(allType[index[0]].getElementsByTagName('li')[index[1]]);
 }

/*********
* 选择的时候 改变选中状态（切换）
*********/
function changeOptionEvent(index){
    var i= 0,
        nowOptions = allType[index[0]].getElementsByTagName('li');
        len = nowOptions.length;
    for(;i<len;i++){
        J_FUN.removeClassName(nowOptions[i].children[0],"l_cur"); // 给所有清空样式
    }
    J_FUN.addClassName(nowOptions[index[1]].children[0],"l_cur");  // 当前追加样式
}

// 增加条件(把当前点击选项添加到已筛选列表)
function addOption(index){
    var newNode = document.createElement("span");
    newNode.className = "l_ceil";
    newNode.id = "search_" +index[0];  // 绑定id为第几个类型（ul）
    var text = getText(index);
    newNode.innerHTML = text +'<a href="#"><i class="l_ceil_i"></i></a>';
    hasChoosedContain.insertBefore(newNode,clearBtn);
}
// 更新(修改)条件
function updateOption(index){
    document.getElementById('search_'+index[0]).innerHTML = getText(index) +'<a href="#"><i class="l_ceil_i"></i></a>';
}
// 删除条件
function deleteOption(index){
    J_FUN.removeNode(document.getElementById('search_'+index[0]));
}
// 清空条件
function emptyOption(){
    var cloneBtn = clearBtn.cloneNode(true);  // 克隆按钮节点
    J_FUN.removeAllChild(hasChoosedContain);   // 清空所有节点
    hasChoosedContain.appendChild(clearBtn);  // 追加按钮节点
    // 将所有类型都改为不限
    var i=0
    for(;i<allTypeLength; i++){
        changeOptionEvent([i,0]);
    }
}
// 得到最后一个子元素节点
function getLastChild(ele){
    return ele.children[ele.children.length-1];
}

/*********
* 所有选项绑定点击（选择）事件
*********/
for(var i=0; i<allOptionLength; i++){
    J_FUN.addEvent(allOption[i], "click", function(){
		console.log(this.index);
        var index = getIndex(this);
        changeOptionEvent(index);  //  改变选中状态
        // 如果当前点击为不限的时候 即index[1] == 0
        if(index[1] == 0){
            deleteOption(index); // 删除当前已选条件
            return 0;
        }
        // 判断当前类型的选项之前有没有添加
        // 如果有就更新选项  没有就添加新选项
        // 当前添加后id为`search_+ index[0]`
        if(!document.getElementById('search_'+index[0])){
            addOption(index);   //  添加到选项列表
        }else{
            updateOption(index);   //  更新已经添加的选项
        }

    });
}

// 清空筛选按钮事件
J_FUN.addEvent(clearBtn,"click",function(){
    emptyOption();
});

// 删除当前已选条件
J_FUN.addEvent(document,"click",function(e){
    var target = J_FUN.getTarget(e);
    if(J_FUN.hasClassName(target,"l_ceil_i")){
        var deleteDom = target.parentNode.parentNode;  //  要删除的节点
        var nowType = deleteDom.id.replace(/search_/,"")|0;
        J_FUN.removeNode(deleteDom);  // 删除当前已选
        changeOptionEvent([nowType,0])//  更新对应可选项到不限
    }
});


