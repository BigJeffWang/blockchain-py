[TOC]

# Alembic 使用方法 - 1

1. 新增Model的话需要再 alembic/env.py中import model(已废弃此条,新增model会自动添加到env.py中,如果不想被同步更新,可以在model文件的名字开头加上 "__")

2. 修改完model的话需要执行alembic revision --autogenerate -m "xxxxxxxxx（message）"

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

    
## 发布注意事项

### 1.脚本：
      automatic_release_script  项目发布脚本 
      robot_auto_bet_script.py  机器人自动投注  
      lottery_auto_script.py    开奖
      bitcoin_price_script.py   获取币价
      block_miner_script.py     私有链上链脚本

### 2.Usercenter 2个config

