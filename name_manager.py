from pathlib import Path

import reapy
from reapy import reascript_api as rp


class NameManager:

    def __init__(self):
        self.filter_list = []

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
    def __get_takes(self) -> [dict]:
        """
        获取 take 信息
        :return: [{
                'take': take,
                'name': take.name,
                'is_selected': is_item_selected,
                'new_name':''
            }]
        """
        data = []
        items = reapy.Project().items
        for i in items:
            is_item_selected = i.is_selected
            take = i.active_take
            take_info = {
                'take': take,
                'name': take.name,
                'is_selected': is_item_selected,
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

    def __get_marker_info(self, mark_index) -> dict:
        """
        获取 marker 信息
        :param mark_index:
        :return: {
            'marker_index': marker_index,
            'name': name,
            'is_region': is_region,
            'is_marker': not is_region,
            'is_selected': False,
            'new_name': ''
        }
        """
        (_, _, is_region_out, start, end, _,
         marker_index) = rp.EnumProjectMarkers(mark_index, 0, 0, 0, 0, 0)

        name = self.__get_marker_name(marker_index, is_region_out)
        is_region = is_region_out == 1

        marker_info = {
            'marker_index': marker_index,
            'name': name,
            'is_region': is_region,
            'is_marker': not is_region,
            'is_selected': False,
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
        return [i for i in self.__get_takes()]


if __name__ == '__main__':
    mgr = NameManager()
    print('trackers', mgr.tracks)
    print('items', mgr.items)
    print('regions', mgr.regions)
    print('markers', mgr.markers)

    # print(mgr.get_regions())
    # path = Path('get_region.py').resolve()
    # reapy.add_reascript(str(path))
