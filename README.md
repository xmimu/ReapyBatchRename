# ReapyBatchRename

代码地址：https://github.com/xmimu/ReapyBatchRename.git



### 使用：

- ​	0、python 3.9 以上环境、正确安装并配置好 reapy

- ​	1、pip install -r requirements.txt 安装依赖库

- ​	1、打开reaper、然后在外部运行 ReapyBatchRename.py

- ​	2、如果需要，可以用 pyinstaller 打包 exe 大概27mb（不过你都装python了

  

### 基本功能：

- ​	0、支持 轨道、区域、midi 和媒体对象、标记 的改名

- ​	1、支持 过滤仅选择的对应资源，但是暂不支持选中的 区域、标记

- ​	2、支持 区分大小写、全字匹配、正则表达式 三种匹配模式

- ​	3、支持 手动多行输入，比如从表格复制多行字符，点表格编辑，自动换行输入

- ​	4、支持 撤销



### 已知问题：

- 更新 区域、标记的时候，dock 窗口不正常刷新，但是名称已正确修改

- midi 和 媒体对象 改名操作无法撤销

  

### 后续实现：

- ​	1、正则表达式 group 替换
- ​	2、类似 REAPER 通配符风格的替换

------

### 20230304 更新：

- 新增实现一个自定义通配符，可以改变替换之后名称的英文大小，只能配置在开始位置并且不能单独使用。

  - "#A"    - 表示转为大写，            "#a"   - 表示转为小写，

  - "#\_A"  - 表示转为首字母大写，"#\_a"  - 表示转为首字母小写。

    <img src="D:\PycharmProjects\ReapyBatchRename\images\大小写转换" alt="image-20230304192034239" style="zoom: 80%;" />

- 新增针对正则表达式 group 的替换实现。

  - $ 加数字 - 用于替换正则表达式group捕获到的值，索引从1开始。

  - ~~\ 加数字 - 用于删除正则表达式group捕获到的值，把删除之后的内容替换到新名称。~~

    <img src="D:\PycharmProjects\ReapyBatchRename\images\正则替换.png" alt="image-20230304192730574" style="zoom:80%;" />

    