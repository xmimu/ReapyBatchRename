import re


class ReaperWildCardHelper:
    Project = '$Project'
    Item = '$Item'

    @staticmethod
    def is_valid(text: str) -> bool:
        for k, v in ReaperWildCardHelper.__dict__.items():  # type:str,object
            if not isinstance(v, str) or not v.startswith('$'): continue
            if v == text:
                return True
        return False

    @staticmethod
    def parse(match_count, current_name, new_name, replace_string) -> str:
        # 判断 替换输入字符，只要包含 $ 加字符串，就认为是 reaper 通配符
        groups = re.findall(r'\$\w+', replace_string)
        for wildcard in groups:
            if not ReaperWildCardHelper.is_valid(wildcard): continue
            wildcard_value = ReaperWildCardHelper.get_wildcard_value(wildcard)
            new_name.replace(wildcard, wildcard_value)

        return new_name

    @staticmethod
    def get_wildcard_value(wildcard: str):
        if wildcard == ReaperWildCardHelper.Project:
            pass
        elif wildcard == ReaperWildCardHelper.Item:
            pass


class WildcardHelper:

    @staticmethod
    def parse(match_count, current_name, replace_string, regex_groups=None):
        """处理替换字符串里面的通配符，生成新的名称"""
        ############### 判断替换字符串里面的 $0 通配符，表示旧名称
        new_name = replace_string
        # 判断的是输入的替换字符，操作的是新的变量 new_name，最后返回
        if '$0' in replace_string:
            new_name = replace_string.replace('$0', current_name)

        ############### 判断 正则表达式 通配符
        new_name = WildcardHelper.parse_regex_wildcard(
            match_count, current_name, new_name, replace_string, regex_groups)

        ############### 判断 REAPER 通配符
        new_name = WildcardHelper.parse_reaper_wildcard(
            match_count, current_name, new_name, replace_string)

        ############### 判断 自定义通配符
        new_name = WildcardHelper.parse_custom_wildcard(
            match_count, current_name, new_name, replace_string)

        return new_name

    @staticmethod
    def parse_regex_wildcard(match_count, current_name, new_name, replace_string, regex_groups):
        # 条件，搜索的正则表达式包含group，也就是括号，
        # 同时，替换的字符串输入，包含 $1，也就是 $ 加上group序号
        # 排除 $0，前面第一个包含了 $0的实现
        replace_groups = re.findall(r'\$[1-9]+', replace_string)
        if regex_groups is not None and replace_groups:
            for group_text in replace_groups:  # type:str
                # 规定 replace输入的正则group索引 从 1 开始
                # 而正则 group 是从 0 开始索引，所以这里要 -1
                regex_group_index = int(group_text[1:]) - 1

                # 超出索引，不用管，保留错误的 $ 输入
                if regex_group_index > len(regex_groups): continue

                new_name = new_name.replace(group_text, regex_groups[regex_group_index])

        # 实现一个方法，把 正则 group 里的内容 删除，
        # 替换通配符用 \ 加 group 索引，从 1 开始
        # replace_remove_groups = re.findall(r'\\[1-9]+', replace_string)
        # deleted_string_result = '' # 这个删除通配符后的字符串，要记录成唯一
        # if regex_groups is not None and replace_remove_groups:
        #     for group_text in replace_remove_groups:  # type:str
        #         # 规定 replace输入的正则group索引 从 1 开始
        #         # 而正则 group 是从 0 开始索引，所以这里要 -1
        #         regex_group_index = int(group_text[1:]) - 1
        #
        #         # 超出索引，不用管，保留错误的 $ 输入
        #         if regex_group_index > len(regex_groups): continue
        #
        #         if not deleted_string_result:
        #             deleted_string_result = current_name.replace(
        #                 regex_groups[regex_group_index], '')
        #         new_name = new_name.replace(group_text, deleted_string_result)

        return new_name

    @staticmethod
    def parse_reaper_wildcard(match_count, current_name, new_name, replace_string) -> str:
        ReaperWildCardHelper.parse(match_count, current_name, new_name, replace_string)

    @staticmethod
    def parse_custom_wildcard(match_count, current_name, new_name, replace_string) -> str:
        # 用 # 加数字，可以转换成搜索结果的顺序，升序，并按格式自动补零
        # 比如替换输入是#001，依次次命名为 001, 002...
        if '#' in replace_string:
            _list = re.findall(r'(#\d+)', replace_string)
            for i in _list:  # type:str
                start_num = int(i.replace('#', ''))
                str_len = len(i) - 1
                temp_name = str(start_num + match_count).zfill(str_len)
                new_name = new_name.replace(i, temp_name)

        # @ 加数字，类似上面，但是降序
        if '@' in replace_string:
            _list = re.findall(r'(@\d+)', replace_string)
            for i in _list:  # type:str
                start_num = int(i.replace('@', ''))
                str_len = len(i) - 1
                temp_name = str(start_num - match_count).zfill(str_len)
                new_name = new_name.replace(i, temp_name)

        # 实现一个 通配符，可以改变 替换名称的大小写字母
        # 这个通配符只能配置在开始位置，
        # "#A" 表示转为大写，"#a" 表示转为小写
        # "#_A" 表示转为首字母大写，"#_a" 表示转为首字母小写
        if re.match('#A', replace_string):
            new_name = new_name.replace('#A', '').upper()
        elif re.match('#a', replace_string):
            new_name = new_name.replace('#a', '').lower()
        elif re.match('#_A', replace_string):
            new_name = new_name.replace('#_A', '')
            new_name = new_name[0].upper() + new_name[1:]
        elif re.match('#_a', replace_string):
            new_name = new_name.replace('#_a', '')
            new_name = new_name[0].lower() + new_name[1:]

        return new_name


if __name__ == '__main__':
    print(ReaperWildCardHelper.is_valid('$Project'))
