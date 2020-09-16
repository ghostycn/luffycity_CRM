"""
分页组件
"""


class Pagination(object):
    def __init__(self, current_page, all_count, base_url, query_params, per_page=20, pager_page_count=11):
        """
        分页初始化
        :param current_page: 当前页码
        :param per_page: 每页显示数据条数
        :param all_count: 数据库中总条数
        :param base_url: 基础URL
        :param query_params: QueryDict对象，内部含所有当前URL的原条件
        :param pager_page_count: 页面上最多显示的页码数量
        """
        # 初始化基础URl
        self.base_url = base_url
        try:
            # 初始化当前页码
            self.current_page = int(current_page)
            # 初始页面小于0报错
            if self.current_page <= 0:
                raise Exception()
        except Exception as e:
            # 捕捉报错设置默认初始页面为一
            self.current_page = 1
        # 获取原始URL查询条件
        self.query_params = query_params
        # 设置每个页码显示的数据条数
        self.per_page = per_page
        # 设置数据库数据总数
        self.all_count = all_count
        # 设置页面下方查询页码个数
        self.pager_page_count = pager_page_count
        # 取出分页总页数和余数
        pager_count, b = divmod(all_count, per_page)
        # 如果有余数，分页总页数加1
        if b != 0:
            pager_count += 1

        self.pager_count = pager_count

        # 取出下方页码查询个数除2
        half_pager_page_count = int(pager_page_count / 2)
        self.half_pager_page_count = half_pager_page_count

    @property
    def start(self):
        """
        数据获取值起始索引
        :return:
        """
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        """
        数据获取值结束索引
        :return:
        """
        return self.current_page * self.per_page

    def page_html(self):
        """
        生成HTML页码
        :return:
        """
        # 如果分页总数小于下方查询页码数量
        if self.pager_count < self.pager_page_count:
            # 开始页码为1
            pager_start = 1
            # 结束页码为分页总数
            pager_end = self.pager_count
        else:
            # 数据页码已经超过11
            # 判断： 如果当前页 <= 5 half_pager_page_count
            if self.current_page <= self.half_pager_page_count:
                # 开始页码为1
                pager_start = 1
                # 结束页码为下方查询页码数量
                pager_end = self.pager_page_count
            else:
                # 如果： 当前页+5 > 下方查询页码数量
                if (self.current_page + self.half_pager_page_count) > self.pager_count:
                    # 结束页码为总页数
                    pager_end = self.pager_count
                    # 开始页码为总页码-设置下方查询页码个数+1
                    pager_start = self.pager_count - self.pager_page_count + 1
                else:
                    # 开始页码为当前页码减去下方一半页码数量
                    pager_start = self.current_page - self.half_pager_page_count
                    # 结束页码为当前页码加上下方一半页码数量
                    pager_end = self.current_page + self.half_pager_page_count

        # 设置页码li列表
        page_list = []

        # 如果当前页码小于等于一，设置为上一页
        if self.current_page <= 1:
            prev = '<li><a href="#">上一页</a></li>'
        else:
            self.query_params['page'] = self.current_page - 1
            # 将存入的字典参数编码为URL查询字符串，即转换成以key1=value1&key2=value2的形式
            prev = '<li><a href="%s?%s">上一页</a></li>' % (self.base_url, self.query_params.urlencode())
        page_list.append(prev)
        for i in range(pager_start, pager_end + 1):
            self.query_params['page'] = i
            if self.current_page == i:
                tpl = '<li class="active"><a href="%s?%s">%s</a></li>' % (
                    self.base_url, self.query_params.urlencode(), i,)
            else:
                tpl = '<li><a href="%s?%s">%s</a></li>' % (self.base_url, self.query_params.urlencode(), i,)
            page_list.append(tpl)

        if self.current_page >= self.pager_count:
            nex = '<li><a href="#">下一页</a></li>'
        else:
            self.query_params['page'] = self.current_page + 1
            nex = '<li><a href="%s?%s">下一页</a></li>' % (self.base_url, self.query_params.urlencode(),)
        page_list.append(nex)
        page_str = "".join(page_list)
        return page_str
