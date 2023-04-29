</p>
<p align="center">
<a href="https://img.shields.io/badge/Python-3.9.11+-green" target="__blank"><img src="https://img.shields.io/badge/Python-3.9.11+-green" alt="custard preview"></a>
<a href="https://pypi.org/project/custard/" target="__blank"><img src="https://img.shields.io/pypi/v/custard" alt="custard preview"></a>
<a href="https://pypistats.org/packages/custard" target="__blank"><img src="https://img.shields.io/pypi/dm/custard"></a>
<br>
</p>

## 📚简介
custard是一个小而全的Python工具类库，通过静态方法封装，降低相关API的学习成本，提高工作效率，使Python拥有函数式语言般的优雅，让Python语言也可以“甜甜的”。

custard中的工具方法来自每个用户的精雕细琢，它涵盖了Python开发底层代码中的方方面面，它既是大型项目开发中解决小问题的利器，也是小型项目中的效率担当；

custard是项目中“util”包友好的替代，它节省了开发人员对项目中公用类和公用工具方法的封装时间，使开发专注于业务，同时可以最大限度的避免封装不完善带来的bug。

## 🍺custard如何改变我们的coding方式

custard的目标是使用一个工具方法代替一段复杂代码，从而最大限度的避免“复制粘贴”代码的问题，彻底改变我们写代码的方式。

以计算MD5为例：

- 👴【以前】打开搜索引擎 -> 搜“Python MD5加密” -> 打开某篇博客-> 复制粘贴 -> 改改好用
- 👦【现在】引入custard  -> Kerberos.md5_encode()

custard的存在就是为了减少代码搜索成本，避免网络上参差不齐的代码出现导致的bug。

-------------------------------------------------------------------------------

## 🛠️包含组件

一个Python基础工具类，对文件、流、加密解密、转码、正则、线程、XML等JDK方法进行封装，组成各种Util工具类，同时提供以下组件：

| 模块                |     介绍                                                                     |
|-------------------|----------------------------------------------------------------------------- |
| core      |     核心，包括Bean操作、各种Util等                                          |
| crypto    |     加密解密模块，提供对称、非对称和摘要算法封装  |
| curl      |     curl实现                                  |
| hitfilter |     敏感词过滤器                               |
| limiter   |     拦截器                                   |
| time      |     日期                                    |
| kaptcha   |     图片验证码实现          |
| swagger   |     自动解析swagger生成request请求        |
| pagination |    分页组件      |

-------------------------------------------------------------------------------

## [📝中文文档](https://github.com/kamalyes/custard/docs/)

-------------------------------------------------------------------------------

## 🚽编译安装

访问custard的Github主页：[https://github.com/kamalyes/custard](https://github.com/kamalyes/custard) 下载整个项目源码（master或dev分支都可）然后进入custard项目目录执行：

```sh
pip3 install -r requirements.txt -i https://pypi.douban.com/simple
pip install build
python -m build
```

然后就可以使用引入了。

-------------------------------------------------------------------------------

## 🏗️添砖加瓦

### 🎋分支说明

custard的源码分为两个分支，功能如下：

| 分支       | 作用                                                          |
|-----------|---------------------------------------------------------------|
| master | 主分支，release版本使用的分支，与中央库提交的jar一致，不接收任何pr或修改 |
| dev    | 开发分支，默认为下个版本的SNAPSHOT版本，接受修改或pr                 |

### 🐞提供bug反馈或建议

提交问题反馈请说明正在使用的JDK版本呢、custard版本和相关依赖库版本。

- [GitHub issue](https://github.com/kamalyes/custard/issues)


### 🧬贡献代码的步骤

1. 在Gitee或者Github上fork项目到自己的repo
2. 把fork过去的项目也就是你的项目clone到你的本地
3. 修改代码（记得一定要修改dev分支）
4. commit后push到自己的库（dev分支）
5. 登录Gitee或Github在你首页可以看到一个 pull request 按钮，点击它，填写一些说明信息，然后提交即可。
6. 等待维护者合并

### 📐PR遵照的原则

custard欢迎任何人为custard添砖加瓦，贡献代码，不过维护者是一个强迫症患者，为了照顾病人，需要提交的pr（pull request）符合一些规范，规范如下：

1. 注释完备，尤其每个新增的方法应按照Python文档规范标明方法说明、参数说明、返回值说明等信息，必要时请添加单元测试，如果愿意，也可以加上你的大名。
2. custard的缩进按照IDEA 默认（tab）缩进，所以请遵守（不要和我争执空格与tab的问题，这是一个病人的习惯）。
3. 新加的方法不要使用第三方库的方法，custard遵循无依赖原则（除非在extra模块中加方法工具）。
4. 请pull request到`dev`分支。`master`是主分支，表示已经发布中央库的版本，这个分支不允许pr，也不允许修改。
5. 我们如果关闭了你的issue或pr，请不要诧异，这是我们保持问题处理整洁的一种方式，你依旧可以继续讨论，当有讨论结果时我们会重新打开。
