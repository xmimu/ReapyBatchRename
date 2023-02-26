from pathlib import Path

import reapy
from loguru import logger
from reapy import reascript_api as rp


class NameManager:

    def __init__(self):
        self.accept_empty_new_name = False

    @reapy.inside_reaper()
    def __get_tracks(self) -> [dict]:
        """
        获取轨道信息
        :return: [{
                'track': track,
                'name': track.name,
                'is_selected': track.is_selected,
                'new_name': ''
            }]
        """
        tracks = reapy.Project().tracks
        data = []
        for track in tracks:
            item = {
                'track': track,
                'name': track.name,
                'is_selected': track.is_selected,
                'new_name': ''
            }
            data.append(item)
        return data

    @reapy.inside_reaper()
    def __get_items(self) -> [dict]:
        """
        获取 每个 item 的 active take 信息，记录 item 的索引，选择状态，
        active take 的名称，
        :return: [{
                'item_index': idx,
                'name': name,
                'is_selected': is_selected,
                'new_name': ''
            }]
        """
        data = []
        count = rp.CountMediaItems(0)
        for idx in range(count):
            item = rp.GetMediaItem(0, idx)
            is_selected = rp.IsMediaItemSelected(item)
            take = rp.GetActiveTake(item)
            name = rp.GetTakeName(take)
            take_info = {
                'item_index': idx,
                'name': name,
                'is_selected': is_selected,
                'new_name': ''
            }
            data.append(take_info)

        return data

    def __get_marker_name(self, marker_index, is_region) -> str:
        """
        获取 mark 或者 region 名称
        :param marker_index: rp.EnumProjectMarkers 获取 marker 索引
        :return: marker_name
        """
        fs = rp.SNM_CreateFastString("")  # get region name
        rp.SNM_GetProjectMarkerName(0, marker_index, is_region, fs)
        name = rp.SNM_GetFastString(fs)
        rp.SNM_DeleteFastString(fs)
        return name

    def __get_marker_info(self, marker_index) -> dict:
        """
        获取 marker 信息
        :param marker_index:
        :return: {
            'marker_index': marker_index,
            'name': name,
            'is_region': is_region,
            'is_marker': not is_region,
            'is_selected': False,
            'start':start,
            'end':end,
            'new_name': ''
        }
        """
        (_, _, is_region_out, start, end, _,
         marker_index) = rp.EnumProjectMarkers(marker_index, 0, 0, 0, 0, 0)

        name = self.__get_marker_name(marker_index, is_region_out)
        is_region = is_region_out == 1

        marker_info = {
            'marker_index': marker_index,
            'name': name,
            'is_region': is_region,
            'is_marker': not is_region,
            'is_selected': False,
            'start': start,
            'end': end,
            'new_name': ''
        }

        return marker_info

    def __count_markers_regions(self):
        return reapy.Project().n_markers + reapy.Project().n_regions

    @reapy.inside_reaper()
    def __get_markers_regions(self):
        """
        获取 region + marker 信息
        :return: [{}]
        """
        data = []
        all_count = self.__count_markers_regions()

        for i in range(all_count):
            region_info = self.__get_marker_info(i)
            data.append(region_info)
        return data

    @property
    def regions(self):
        return [i for i in self.__get_markers_regions() if i['is_region']]

    @property
    def markers(self):
        return [i for i in self.__get_markers_regions() if i['is_marker']]

    @property
    def tracks(self):
        return [i for i in self.__get_tracks()]

    @property
    def items(self):
        return [i for i in self.__get_items()]

    @reapy.inside_reaper()
    def set_track_name(self, search_result):
        rp.Undo_BeginBlock2(0)

        for i in search_result:
            track = i['track']
            new_name = i['new_name']
            # 空白名称判断
            if not self.accept_empty_new_name and not new_name:
                continue
            track.set_info_string('P_NAME', new_name)

        ##############################################
        ######## 玄学问题，undo block 只在函数里面才有效
        #############################################
        rp.Undo_EndBlock2(0, 'Reapy batch rename tracks', 1)
        self.refresh_all()

    @reapy.inside_reaper()
    def set_item_name(self, search_result):
        rp.Undo_BeginBlock2(0)

        for i in search_result:
            logger.debug(i)
            item_id = i['item_index']
            new_name = i['new_name']
            # 空白名称判断
            if not self.accept_empty_new_name and not new_name:
                continue

            item = rp.GetMediaItem(0, item_id)
            # take = rp.GetMediaItemTake(item, 0)
            take = rp.GetActiveTake(item)
            rp.GetSetMediaItemTakeInfo_String(take, 'P_NAME', new_name, True)

        ############ undo block 无法生效
        rp.Undo_EndBlock2(0, 'Reapy batch rename items', 1)
        self.refresh_all()

    def set_marker_name(self, search_result):
        """
        设置 region 或者 mark 名称
        :param search_result: [{
            'marker_index': marker_index,
            'name': name,
            'is_region': is_region,
            'is_marker': not is_region,
            'is_selected': False,
            'start':start,
            'end':end,
            'new_name': ''
        }]
        :return:
        """
        rp.Undo_BeginBlock2(0)

        for i in search_result:
            new_name = i['new_name']
            # 空白名称判断
            if not self.accept_empty_new_name and not new_name:
                continue

            rp.SetProjectMarker(
                i['marker_index'], i['is_region'],
                i['start'], i['end'], i['new_name']
            )
        # 不能正确显示 undo 信息，但是有效
        rp.Undo_EndBlock2(0, 'Reapy batch rename markers', 1)
        self.refresh_all()

    @reapy.inside_reaper()
    def refresh_all(self):
        # 刷新 layouts
        rp.ThemeLayout_RefreshAll()
        rp.DockWindowRefresh()

    @reapy.inside_reaper()
    def start_undo(self):
        rp.Undo_BeginBlock2(0)

    @reapy.inside_reaper()
    def end_undo(self, msg: str):
        logger.debug(msg)
        # 设置 extraflags 为 1可以正常显示
        rp.Undo_EndBlock2(0, msg, 0)

    @reapy.inside_reaper()
    def do_undo(self):
        rp.Undo_DoUndo2(0)
        self.end_undo('Reapy Undo') # 反正不加 reaper 会卡...
        logger.debug('Do undo 2')


if __name__ == '__main__':
    mgr = NameManager()
    # print('trackers', mgr.tracks)
    # print('items', mgr.items)
    # print('regions', mgr.regions)
    # print('markers', mgr.markers)

    # print(mgr.get_regions())
    # path = Path('get_region.py').resolve()
    # reapy.add_reascript(str(path))
