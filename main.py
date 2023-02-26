import enum
import re

import flet as ft
from loguru import logger
from name_manager import NameManager


class WorkMode(enum.Enum):
    Region = enum.auto()
    Track = enum.auto()
    Item = enum.auto()
    Marker = enum.auto()


class App(ft.ListView):

    def __init__(self, page: ft.Page, manager: NameManager):
        super().__init__()
        self.page = page
        self.manager = manager
        self.expand = True
        # self.auto_scroll =True
        self.padding = 20
        # 实例变量
        self.is_running = False
        self.search_string = ''
        self.replace_string = ''
        self.is_match_case = False
        self.is_match_all_text = False
        self.is_match_regex = False
        self.is_selected_only = False
        self.work_mode = WorkMode.Region
        self.search_result = []
        # 初始化 UI
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # 初始化表格数据
        self.refresh_table()
        # 隐藏 替换所有的按钮，暂时不实现这个功能 # todo
        self.btn_replace_all.visible = False
        self.btn_replace_all.disabled = True

    def create_widgets(self):
        def create_table():
            table = ft.DataTable(
                width=1000,
                heading_row_color=ft.colors.BLUE_GREY_800,
                border=ft.border.all(2, ft.colors.BROWN),
                border_radius=10,
                horizontal_lines=ft.BorderSide(1, ft.colors.YELLOW_100),
                vertical_lines=ft.BorderSide(1, ft.colors.RED_50),
                columns=[
                    ft.DataColumn(label=ft.Text('序号'), numeric=True),
                    ft.DataColumn(label=ft.Text('名称')),
                    ft.DataColumn(label=ft.Text('新的名称')),
                ]
            )

            return table

        self.table = create_table()

        self.checkbox_selected_only = ft.Checkbox(label='仅选中的：区域')

        self.edit_search = ft.TextField(label='查找：', expand=True)
        self.edit_replace = ft.TextField(label='替换：', expand=True)
        self.btn_search = ft.ElevatedButton(content=ft.Text('查找', size=22), width=160)
        self.btn_replace = ft.ElevatedButton(content=ft.Text('替换', size=22), width=160)
        self.btn_replace_all = ft.ElevatedButton(content=ft.Text('替换所有', size=22), width=160)

        # Undo Redo button
        self.btn_undo = ft.IconButton(icon=ft.icons.UNDO,tooltip='Undo')

        self.switch_match_case = ft.Switch(label='区分大小写')
        self.switch_match_all_text = ft.Switch(label='全字匹配')
        self.switch_match_regex = ft.Switch(label='使用正则表达式')

        self.radio_region = ft.Radio(label='区域', value='区域')
        self.radio_track = ft.Radio(label='轨道', value='轨道')
        self.radio_item = ft.Radio(label='媒体对象', value='媒体对象')
        self.radio_marker = ft.Radio(label='标记', value='标记')

        self.btn_refresh = ft.IconButton(icon=ft.icons.REFRESH,tooltip='refresh')
        self.btn_clear = ft.IconButton(icon=ft.icons.CLEANING_SERVICES_SHARP,tooltip='clear')

    def create_layouts(self):
        head = ft.Column([
            ft.Row([
                self.edit_search,
                self.edit_replace
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                self.switch_match_case,
                self.switch_match_all_text,
                self.switch_match_regex,
            ]),
            ft.Row([
                self.btn_search,
                ft.Container(width=50),
                self.btn_replace,
                self.btn_replace_all,
                ft.Container(width=30),
                self.btn_undo
            ])
        ], spacing=20)

        self.radio_group = ft.RadioGroup(
            value='区域',
            content=ft.Row([
                self.radio_region,
                self.radio_track,
                self.radio_item,
                self.radio_marker
            ]),
        )

        self.controls = [
            head,
            ft.Container(height=20),
            ft.Row([
                self.radio_group,
                ft.Container(width=50),
                self.checkbox_selected_only,
                ft.Container(width=50),
                self.btn_refresh,
                self.btn_clear
            ]),
            self.table
        ]

    def create_connections(self):
        # 输入框事件
        self.edit_search.on_change = self.edit_search_changed
        self.edit_replace.on_change = self.edit_replace_changed
        # 匹配设模式开关事件
        self.switch_match_case.on_change = self.switch_match_case_changed
        self.switch_match_all_text.on_change = self.switch_match_all_text_changed
        self.switch_match_regex.on_change = self.switch_match_regex_changed
        # 按钮事件
        self.btn_search.on_click = self.btn_search_clicked
        self.btn_replace.on_click = self.btn_replace_clicked
        # self.btn_replace_all.on_click = self.btn_replace_all_clicked
        self.btn_undo.on_click = self.btn_undo_clicked
        # 单选，复选按钮事件
        self.radio_group.on_change = self.radio_group_changed
        self.checkbox_selected_only.on_change = self.checkbox_selected_only_changed
        self.btn_refresh.on_click = self.btn_refresh_clicked
        self.btn_clear.on_click = self.btn_clear_clicked

    def __check_manager_data(self) -> list:
        """
        判断当前模式，获取 reaper 列表资源
        :return: regions, tracks...
        """
        if self.work_mode == WorkMode.Region:
            data = self.manager.regions
        elif self.work_mode == WorkMode.Track:
            data = self.manager.tracks
        elif self.work_mode == WorkMode.Item:
            data = self.manager.items
        elif self.work_mode == WorkMode.Marker:
            data = self.manager.markers
        else:
            data = []

        # 判断是否 勾选 仅选中选框
        if self.is_selected_only:
            data = [i for i in data if i['is_selected']]

        return data

    def __create_table_rows(self, data: list):
        rows = []
        for index, row_data in enumerate(data):
            row = ft.DataRow(
                cells=[
                    ft.DataCell(content=ft.Text(str(index))),
                    ft.DataCell(content=ft.Text(row_data['name'])),
                    ft.DataCell(
                        content=ft.Text(row_data['new_name']),
                        show_edit_icon=True,
                        on_tap=self.on_cell_tap
                    ),
                ]
            )
            rows.append(row)

        return rows

    def refresh_table(self):
        """
        判断当前选择模式，更新数据到表格
        :return:
        """
        ################ 重置搜索结果 ###############
        self.search_result = self.__check_manager_data()

        # 显示到 table
        self.table.rows = self.__create_table_rows(self.search_result)

        # 如果是初始化状态，update 会报错，而且也不需要 update
        try:
            self.table.update()
        except Exception:
            pass

    def search_from_data(self, data: list) -> list:
        """
        根据条件 查找列表中符合的条目，作为列表返回
        :param data:
        :return: search_list
        """
        search_result = []

        # 防止循坏中，UI更新改变实例变量
        search_string = self.search_string
        replace_string = self.replace_string
        is_match_case = self.is_match_case
        is_match_all_text = self.is_match_all_text
        is_match_regex = self.is_match_regex

        # ################## 查找 ###############################
        # 一个匹配模式都不选择，即 - 包含关系，忽略大小写，不能输入正则表达式
        # search_string.lower() in text.lower()
        if not is_match_case and not is_match_all_text and not is_match_regex:
            for i in data:
                if search_string.lower() in i['name'].lower():
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        # 三个匹配模式都选择，即 - 非包含关系，区分大小写，可以输入正则表达式和完整字符串
        # re.match(pattern, text)
        elif is_match_case and is_match_all_text and is_match_regex:
            for i in data:
                if re.match(search_string, i['name']):
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        # 只选择第一个，即 - 包含关系，区分大小写，不能输入正则表达式
        # search_string in text
        elif is_match_case and not is_match_all_text and not is_match_regex:
            for i in data:
                if search_string in i['name']:
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        # 只选择第二个，即 - 非包含关系，忽略大小写，不能输入正则表达式
        # search_string.lower()  == text.lower()
        elif is_match_all_text and not is_match_case and not is_match_regex:
            for i in data:
                if search_string.lower() == i['name'].lower():
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        # 只选第三个，即 - 包含关系，忽略大小写，可以输入正则和字符串片段
        # re.search(search_string, text, re.I)
        elif is_match_regex and not is_match_case and not is_match_all_text:
            for i in data:
                if re.search(search_string, i['name'], re.I):
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        # 选择第一个和第二个，即 - 非包含关系，区分大小写，不能输入正则表达式
        # search_string == text
        elif is_match_case and is_match_all_text and not is_match_regex:
            for i in data:
                if search_string == i['name']:
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        # 选择第一个和第三个，即 - 包含关系，区分大小写，可以输入正则
        # re.search(search_string, text)
        elif is_match_case and is_match_regex and not is_match_all_text:
            for i in data:
                if re.search(search_string, i['name']):
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        # 选择第二个和第三个，即 - 非包含关系，忽略大小写，可以输入正则
        # re.match(search_string, text, re.I)
        elif is_match_all_text and is_match_regex and not is_match_case:
            for i in data:
                if re.match(search_string, i['name'], re.I):
                    new_name = replace_string
                    i['new_name'] = new_name

                    search_result.append(i)

        return search_result

    # region 事件回调方法
    def edit_search_changed(self, e):
        self.search_string = self.edit_search.value

    def edit_replace_changed(self, e):
        self.replace_string = self.edit_replace.value

    def switch_match_case_changed(self, e):
        self.is_match_case = self.switch_match_case.value

    def switch_match_all_text_changed(self, e):
        self.is_match_all_text = self.switch_match_all_text.value

    def switch_match_regex_changed(self, e):
        self.is_match_regex = self.switch_match_regex.value

    def on_cell_tap(self, e):
        def dialog_edit_submit(dialog_edit_e):
            _value = dialog_edit_e.control.value
            e.control.content.value = _value
            # 找到所在位置的行索引
            for _index, row in enumerate(self.table.rows):
                if row.cells[2] == e.control:
                    self.search_result[_index]['new_name'] = _value
            # 关闭对话框
            self.page.dialog.open = False
            e.control.update()
            self.page.update()

        text = e.control.content.value

        dialog = ft.AlertDialog(
            title=ft.Text('输入新名称'),
            content=ft.TextField(value=text, autofocus=True, on_submit=dialog_edit_submit),
        )
        dialog.open = True
        self.page.dialog = dialog
        self.page.update()

    def radio_group_changed(self, e):
        value = e.control.value
        self.checkbox_selected_only.label = f'仅选中的：{value}'
        self.checkbox_selected_only.update()

        if value == '区域':
            self.work_mode = WorkMode.Region
        elif value == '轨道':
            self.work_mode = WorkMode.Track
        elif value == '媒体对象':
            self.work_mode = WorkMode.Item
        elif value == '标记':
            self.work_mode = WorkMode.Marker

        self.refresh_table()

    def checkbox_selected_only_changed(self, e):
        self.is_selected_only = e.control.value
        self.refresh_table()
        self.table.update()

    def btn_refresh_clicked(self, e):
        self.refresh_table()

    def btn_clear_clicked(self, e):
        self.edit_search.value = ''
        self.search_string = ''
        self.edit_replace.value = ''
        self.replace_string = ''
        self.page.update()

    def btn_search_clicked(self, e):
        """
        查找符合条件的资源，并更新显示
        :param e:
        :return:
        """
        logger.debug(
            f'查找：{self.search_string} | 替换：{self.replace_string}'
        )
        logger.debug(
            f'区分大小写：{self.is_match_case} |'
            f' 全字匹配：{self.is_match_all_text} |'
            f'使用正则表达式：{self.is_match_regex}'
        )

        data = self.__check_manager_data()

        # 正则表达式可能会出错
        try:
            self.search_result = self.search_from_data(data)
            logger.debug(f'查找结果：{self.search_result}')
        except Exception as e:
            logger.warning(f'可能不正确的表达式: {self.search_string}')
            logger.warning(e)
            self.search_result = data
        # 显示搜索结果
        self.table.rows = self.__create_table_rows(self.search_result)
        self.table.update()

    def btn_replace_clicked(self, e):
        work_mode = self.work_mode
        if work_mode == WorkMode.Region:
            self.manager.set_marker_name(self.search_result)
        elif work_mode == WorkMode.Track:
            self.manager.set_track_name(self.search_result)
        elif work_mode == WorkMode.Item:
            self.manager.set_item_name(self.search_result)
        elif work_mode == WorkMode.Marker:
            self.manager.set_marker_name(self.search_result)

        # 更新表格
        self.refresh_table()

    def btn_replace_all_clicked(self, e):
        pass

    def btn_undo_clicked(self,e):
        self.manager.do_undo()
        self.refresh_table()


def main(page: ft.Page):
    page.title = 'ReapyBatchRename'
    page.window_width = 800
    page.window_height = 800
    page.window_left = 200
    page.window_top = 50
    # page.window_center()
    manager = NameManager()
    app = App(page, manager)

    page.add(app)


logger.add('RBR.log', rotation='200MB', encoding='utf-8', enqueue=True, retention='3 days')
ft.app(target=main)
