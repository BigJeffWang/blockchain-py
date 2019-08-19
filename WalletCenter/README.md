[TOC]

# Alembic 使用方法

1. 新增Model的话需要再 alembic/env.py中import model(已废弃此条,新增model会自动添加到env.py中,如果不想被同步更新,可以在model文件的名字开头加上 "__")

2. 修改完model的话需要执行alembic revision --autogenerate -m "xxxxxxxxx（message）", 如果没有alembic目录, 需要初始化 alembic init alembic

3. 需要与数据库同步的话输入 alembic upgrade head

4. 需要回滚数据库版本的话
   ```
   alembic downgrade -1
   ```

   或者

   ```
   alembic downgrade ae1027a6acf
   ```

5. **注意** ：autogenerate 不是能检测到所有的改变:

   Autogenerate **will detect**:

   - Table additions, removals.
   - Column additions, removals.
   - Change of nullable status on columns.
   - Basic changes in indexes and explcitly-named unique constraints

   Autogenerate can **optionally detect**:

   - Change of column type. This will occur if you set the [`EnvironmentContext.configure.compare_type`](http://alembic.zzzcomputing.com/en/latest/api/runtime.html#alembic.runtime.environment.EnvironmentContext.configure.params.compare_type) parameter to `True`, or to a custom callable function. The feature works well in most cases, but is off by default so that it can be tested on the target schema first. It can also be customized by passing a callable here; see the section [Comparing Types](http://alembic.zzzcomputing.com/en/latest/autogenerate.html#compare-types) for details.
   - Change of server default. This will occur if you set the [`EnvironmentContext.configure.compare_server_default`](http://alembic.zzzcomputing.com/en/latest/api/runtime.html#alembic.runtime.environment.EnvironmentContext.configure.params.compare_server_default) parameter to `True`, or to a custom callable function. This feature works well for simple cases but cannot always produce accurate results. The Postgresql backend will actually invoke the “detected” and “metadata” values against the database to determine equivalence. The feature is off by default so that it can be tested on the target schema first. Like type comparison, it can also be customized by passing a callable; see the function’s documentation for details.

   Autogenerate **can not detect**:

   - Changes of table name. These will come out as an add/drop of two different tables, and should be hand-edited into a name change instead.

   - Changes of column name. Like table name changes, these are detected as a column add/drop pair, which is not at all the same as a name change.

   - Anonymously named constraints. Give your constraints a name, e.g. `UniqueConstraint('col1', 'col2', name="my_name")`. See the section [The Importance of Naming Constraints](http://alembic.zzzcomputing.com/en/latest/naming.html) for background on how to configure automatic naming schemes for constraints.

   - Special SQLAlchemy types such as [`Enum`](http://docs.sqlalchemy.org/en/latest/core/type_basics.html#sqlalchemy.types.Enum) when generated on a backend which doesn’t support ENUM directly - this because the representation of such a type in the non-supporting database, i.e. a CHAR+ CHECK constraint, could be any kind of CHAR+CHECK. For SQLAlchemy to determine that this is actually an ENUM would only be a guess, something that’s generally a bad idea. To implement your own “guessing” function here, use the [`sqlalchemy.events.DDLEvents.column_reflect()`](http://docs.sqlalchemy.org/en/latest/core/events.html#sqlalchemy.events.DDLEvents.column_reflect) event to detect when a CHAR (or whatever the target type is) is reflected, and change it to an ENUM (or whatever type is desired) if it is known that that’s the intent of the type. The[`sqlalchemy.events.DDLEvents.after_parent_attach()`](http://docs.sqlalchemy.org/en/latest/core/events.html#sqlalchemy.events.DDLEvents.after_parent_attach) can be used within the autogenerate process to intercept and un-attach unwanted CHECK constraints.

6. 协同开发时出现多个分支的情况

   For example：

   ```
   $ alembic history
   a -> b (head)
   a -> c (head)

   $ alembic merge -m "message" b c

   $ alembic history
   b, c -> d (head)

# 数据库 表,以及文件命名和变量,相关的 规则和规范
## 1. 先介绍几种下面会用到的命名法:
    
### a.匈牙利命名法:
    开头字母用变量类型的缩写，其余部分用变量的英文或英文的缩写，要求单词第一个字母大写.
    ex:
    int iMyAge; “i”是int类型的缩写；
    char cMyName[10]; “c”是char类型的缩写；
    float fManHeight; “f”是float类型的缩写；
    
### b.驼峰式命名法:
    又叫小驼峰式命名法.
    第一个单词首字母小写，后面其他单词首字母大写.
    ex:
    int myAge;
    char myName[10];
    float manHeight;
    
### c.帕斯卡命名法:
    又叫大驼峰式命名法.
    每个单词的第一个字母都大写.
    ex:
    int MyAge;
    char MyName[10];
    float ManHeight;
    
### d.下划线命名法:
    每个单词都是小写并都以下划线分隔开.
    ex:
    int my_age;
    char my_name[10];
    float man_height;
    
### e.全小写命名法:
    所有单词都是小写
    ex:
    int myage;
    char myname[10];
    float manheight;
    
### f.下划线全大写命名法:
    所有单词都是大写,并且以下划线分隔开.
    ex:
    int MY_AGE;
    char MY_NAME[10];
    float MAN_HEIGHT;
    
### 文件和变量命名 用法:
    1.文件名,用下划线命名法,因为mac下,会有部分文件忽略文件名大小写的情况而导致文件名相同而大小写不同会打不开文件,而且Linux系统的,系统文件和目录文件,都是大驼峰命名,所以建议项目文件都以下划线命名,方便迁移和开发,并不会因任何系统产生歧义.
    2.models services controllers,这三个文件目录下的文件名都以下划线命名法创建文件名,并且该文件里的 需要外部引用的主要的类,都需要以 文件名转换成 帕斯卡命名法也就是大驼峰命名法命名 下面举个例子:
        models
          -base_model.py    类名: class BaseModel():
        services
          -base_service.py  类名: class BaseService():
        controllers
          -base_controller.py   类名: class BaseController():
    ps: 之所以,采用这种规则,是因为,alembic同步model数据的时候,env.py自动引用models目录下的类,采用此规则,
        并且,以后的脚本,如果采用了注册回调方法,也会用到此规则.
    3.这条可以因个人习惯而定, 类的实例化的变量名,和普通变量名,建议 都用下划线命名法,主要pycharm的pylint代码静态检查工具,默认是变量都是下划线命名法,这样可以减少报错提示
    4.某些对外提供的方法的参数,封装对外接口的参数,类的实例化的参数 等等,建议部分参数命名的时候,采用匈牙利命名法,但是由于pylint的报错提示,所以建议在该参数命名的时候 用下划线命名法,并在最后加上该字段的类型,复杂方法的注释尽量全面详细! 下面举个例子:
        def convert_arguments_whether_empty(outoff_type=(int,), check_surely_args_list=None, check_reg_args_list=None):
            Author: wang ye
            装饰器函数,参数合法性验证,校验函数传入参数是否有为空的参数
            用法1:
            @convert_arguments_whether_empty()  # 这样可以int 0
            def test(arg):
            pass
            用法2:
            @convert_arguments_whether_empty(())  # 这样所有类型 都必须 通过 if arg: 由python判断是否为空
            def test(arg):
            pass
            :param check_reg_args_list: 校验需要正则判断的参数列表,例如 ["mobile"],方便后期扩展
            :param check_surely_args_list: 校验必填参数字段名,默认先从args开始找dict开始校验,如果没有再找kwargs开始找dict再校验
            :param outoff_type: 校验为空的例外参数类型,默认刨除type int,参数可以为数字0
            :return:
    
## 2.数据库字段命名规范

### 1.字段命名规范

    （1）采用26个英文字母(区分大小写)和0-9的自然数(经常不需要)加上下划线'_'组成，命名简洁明确，多个单词用下划线'_'分隔
    
    （2）全部小写命名，禁止出现大写
    
    （3）字段必须填写描述信息
    
    （4）禁止使用数据库关键字，如：name，time ，datetime password 等
    
    （5）字段名称一般采用名词或动宾短语
    
    （6）采用字段的名称必须是易于理解，一般不超过三个英文单词
    
    （7）在命名表的列时，不要重复表的名称 例如，在名employe的表中避免使用名为employee_lastname的字段
    
    （8）不要在列的名称中包含数据类型
    
    （9）字段命名使用完整名称，禁止缩写
    
### 2.字段类型规范

    （1）所有字段在设计时，除以下数据类型timestamp、image、datetime、smalldatetime、uniqueidentifier、binary、sql_variant、binary 、varbinary外，必须有默认值，字符型的默认值为一个空字符值串’’，数值型的默认值为数值0，逻辑型的默认值为数值0
    
    （2）系统中所有逻辑型中数值0表示为“假”，数值1表示为“真”，datetime、smalldatetime类型的字段没有默认值，必须为NULL
    
    （3）用尽量少的存储空间来存储一个字段的数据

    使用int就不要使用varchar、char，

    用varchar(16)就不要使varchar(256)

    IP地址使用int类型

    固定长度的类型最好使用char，例如：邮编(postcode)

    能使用tinyint就不要使用smallint，int

    最好给每个字段一个默认值，最好不能为null

    用合适的字段类型节约空间

    字符转化为数字(能转化的最好转化，同样节约空间、提高查询性能)

    避免使用NULL字段(NULL字段很难查询优化、NULL字段的索引需要额外空间、NULL字段的复合索引无效)

    少用text类型(尽量使用varchar代替text字段)

### 3.数据库中每个字段的规范描述 

    (1）尽量遵守第三范式的标准（3NF） 
    
         表内的每一个值只能被表达一次 
    
         表内的每一行都应当被唯一的标示 
    
         表内不应该存储依赖于其他键的非键信息
    
    (2) 如果字段事实上是与其它表的关键字相关联而未设计为外键引用，需建索引
    
    (3) 如果字段与其它表的字段相关联，需建索引
    
    (4) 如果字段需做模糊查询之外的条件查询，需建索引
    
    (5) 除了主关键字允许建立簇索引外，其它字段所建索引必须为非簇索引
    
### 4.定义某些字段类型
    (1) 是否 用boolean类型,实际会转换tinyint(1)类型
    (2) 状态 用tinyint(1)类型,方便排序,-128~128,值范围也够用了
    (3) 时间 用datetime类型,并且最好定义的时候,default=datetime.datetime.now() 给一个默认值,方便在数据库里操作
    (4) 钱相关 用decimal类型  例子: Column(Numeric(21, 4), doc="金额")
    (5) 其他字段或者有争议的字段 用char() 或 varchar(),主要看字段值是否长度可变 

## 3.api接口及其他命名规范
### 1.api命名规范
    (1) 当标准合理的时候遵守标准。
    (2) API应该对程序员友好，并且在浏览器地址栏容易输入。
        这里推荐使用减号"-"来连接函数单词,并且最好是动宾规则,
        例子:/users/open-account,不要使用驼峰命名和下划线"_"命名
        如果这个函数的动词宾语就是这个对象本身，那么可以省略掉宾语。
        如果不服,请参考这个理由:https://www.woorank.com/en/blog/underscores-in-urls-why-are-they-not-recommended
    (3) API应该简单，直观，容易使用的同时优雅。
        拼写要准确,不仅是英文单词不要拼错，时态也不要错。
        不要用生僻单词，这不是秀英语的地方，也不要用汉语拼音。
        不要自己发明缩写。
    (4) API应该具有足够的灵活性来支持上层ui。
        保持方法的对称性，有些方法一旦出现就应该是成对的，
        站在使用者的角度去思考，API设计也要讲究用户体验。
    (5) API设计权衡上述几个原则。
### 2.返回值,当返回给前端的返回值规范
    (1) 是、成功、允许、包含  等等含有代表"正确"意思的返回值,统一用 字符串 "true" 作为值返回给前端(PC,iOS,Android)
    (2) 同上 含有代表"否定"意思的返回值,统一用 字符串 "false"
    (3) 当返回给前端,需要包含状态码、状态信息的时候,请参考RollingStone项目的状态码形式,error_code.py
    (4) 例子:
    {
        "status": "true" / "false"
    }
    (5) 业务层有数据时，返回值为:
    {
        "key1": "value1"
    }
### 3.后端函数方法调用返回值规范
    (1) 正确用 Python的Boolean类型 True
    (2) 否定用 Python的Boolean类型 False
### 4.与银行调用传参等返回值规范
    (1) 商户接收到异步响应之后，应及时返回接收结果，接收成功则返回“success”，失败则返回“fail” (参考文档接入规范)
    (2) 其他参数,整数转成字符串,尽量用字符串传值(具体请参考各自的接口详细文档)