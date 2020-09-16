RBAC组件的使用文档

1、将rbac组件拷贝到项目中

2、将rbac/migrations目录中的数据库迁移记录删除

3、进行业务开发
    
    3.1 对于用户表使用onetoone将用户表拆分两种表中，如:
    
        rbac/models.py
        
            class UserInfo(models.Model):
                """
                用户表
                """
                name = models.CharField(verbose_name='用户名', max_length=32)
                password = models.CharField(verbose_name='密码', max_length=64)
                email = models.CharField(verbose_name='邮箱', max_length=32)
                roles = models.ManyToManyField(verbose_name='拥有的所有角色', to='Role', blank=True)
            
                def __str__(self):
                    return self.name
        
        业务/models.py
            
            class UserInfo(models.Model):
                """
                用户表
                """
                user = models.OneToOneField(verbose_name="用户",to=RbacUseerInfo)
                phone = models.CharField(verbose_name="联系方式",max_length=32)
                level_choices = (
                    (1,"T1"),
                    (2,"T2"),
                    (3,"T3")
                )
            
                depart = models.ForeignKey(verbose_name="部门",to='Department')
            
                def __str__(self):
                    return self.user.name
        
        缺点: 用户表数据分散
        优点：利用上rbac的用户管理的功能
        
    3.2 用户表整合在一张表中（推荐）
        rbac/models.py
            class UserInfo(models.Model):
                """
                用户表
                """
                name = models.CharField(verbose_name='用户名', max_length=32)
                password = models.CharField(verbose_name='密码', max_length=64)
                email = models.CharField(verbose_name='邮箱', max_length=32)
                # 迁移数据库报错解决：
                # roles = models.ManyToManyField(verbose_name='拥有的所有角色', to=Role, blank=True) "to=去掉引号即可"
                
                roles = models.ManyToManyField(verbose_name='拥有的所有角色', to=Role, blank=True)
            
                def __str__(self):
                    return self.name
            
                class Meta:
                    # django以后再做数据库迁移时，不再为UserInfo类创建相关的表以及结构
                    # 此类可以当作"父类"，被其他Model类继承
                    # 因为时抽象的，清空admin.py文件内容
                    abstract = True
        
        业务/models.py
            class UserInfo(RbacUseerInfo):
                """
                用户表
                """
                phone = models.CharField(verbose_name="联系方式",max_length=32)
                level_choices = (
                    (1,"T1"),
                    (2,"T2"),
                    (3,"T3")
                )
                level = models.IntegerField(verbose_name='级别', choices=level_choices)
                depart = models.ForeignKey(verbose_name="部门",to='Department')
            
                def __str__(self):
                    return self.name
        
        优点：将所有用户信息放到一张表中（业务的用户表中）
        缺点：在rbac中所有关于用户表的操作，不能使用了
        
        注意：rbac中两处使用了用户表（如果使用用户表使用此方法，请更改下边功能对应代码）
            - 用户管理【删除】
            - 权限分配时用户列表【读取业务中的用户表即可】
        
        对于rbac中的代码修改：
            1、在URl中将用户表的增删改查和修改密码功能删除
            2、在权限分配之时，读取用户表变成通过配置文件来进行指定并导入
            
            setting.py
                # 权限相关配置
                # 业务中的用户表
                RBAC_USER_MODLE_CLASS = "app01.models.UserInfo"
                
            将用户权限相关代码进行修改：
                rbac/views/menu.py
                    from django.conf import settings
                    from django.utils.module_loading import import_string
                    
                    # 业务中的用户表 "app01.models.UserInfo"
                    user_model_class = import_string(settings.RBAC_USER_MODLE_CLASS)
                    将代码中"models.UserInfo"相关代码替换为user_model_class
    
    3.3 业务开发
        - 用户表的增删改查
        - 主机表的增删改查
        
    如果要使用rbac中的模版，则需要将模版中的 导航条和菜单注释掉，当业务开发完成之后，上线之前再取消注释
    {% multi_menu request %}
    {% url_record request %}

4、权限的应用
    
    4.1 将菜单和导航条添加到layout.html中
        <div class="pg-body">
            <div class="left-menu">
                <div class="menu-body">
                    {% multi_menu request %}
                </div>
            </div>
            <div class="right-body">
                {% url_record request %}
                {% block content %} {% endblock %}
            </div>
        </div>
    
    4.2 中间件的应用
        MIDDLEWARE = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'rbac.middlewares.rbac.RbacMiddleware'
        ]
    
    4.3 白名单处理 setting.py 中添加以下配置
        VALID_URL_LIST = [
            '/login/',
            '/admin/.*'
        ]
 
    4.4 权限初始化 setting.py 中添加以下配置
        首先通过页面添加用户对应的角色与权限
        # 权限在Session中存储的key
        PERMISSION_SESSION_KEY = "luffy_permission_url_list_key"
        # 菜单在Session中存储的key
        MENU_SESSION_KEY = "luffy_permission_menu_key"
 
    4.5 批量操作权限时，自动发现路由中所有的URl，应该排查的URL
        AUTO_DISCOVER_EXCLUDE = [
            '/admin/.*',
            '/login/',
            '/logout/',
            '/index/',
        ]
    
    4.6 用户登录逻辑
        写完用户登录逻辑，对于 /index/,/login/,/logout/, 三个是否用分配
        方案一：
            将 /index/,/logout/,录入数据库。以后给每个用户都分配该权限
        
        方案二：
            默认用户登录后，都能访问/index/和/login/
          
            