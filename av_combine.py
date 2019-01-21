#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import threading

# 调用 ffmpeg 合并当前目录下的视频和音频文件
# 要使用这个脚本，请先安装 ffmpeg 到 C:\ffmpeg\bin 目录

# Aster Jian (asterjian@qq.com), 2019-01-18

class CombineThread(threading.Thread):
    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def run(self):
        # 调用 ffmpeg 合并每一个 URL
        for url in self.urls:
            # 视频文件
            video_file = url + '[00].mp4'
            # 音频文件
            audio_file = url + '[01].mp4'
            if os.path.exists(video_file) and os.path.exists(audio_file):
                # 输出文件
                combined_av_file = url + '.mp4'
                # print('C:\\ffmpeg\\bin\\ffmpeg.exe -i "{}" -i "{}" "{}"'.format(audio_file, video_file, combined_av_file))
                os.system('C:\\ffmpeg\\bin\\ffmpeg.exe -i "{}" -i "{}" "{}"'.format(audio_file, video_file, combined_av_file))
                os.remove(video_file)
                os.remove(audio_file)

class AVCombiner(object):
    '''YouTube 视频下载器'''

    def combine(self, urls, max_threads):
        '''合并 URL 中为文件'''

        if len(urls) == 0:
            return

        # 线程数目
        num_threads = min(max_threads, len(urls))

        # 每个线程分配的URL数目
        urls_per_thread = len(urls) // num_threads
        if len(urls) % num_threads != 0:
            urls_per_thread += 1

        print('num_urls =', len(urls))
        print('num_threads =', num_threads)
        print('urls_per_thread =', urls_per_thread)

        # 所有合并线程列表
        combine_threads = []

        for i in range(num_threads):
            # 将每一段 URL 分配给一个线程
            beg = i * urls_per_thread
            end = min(beg + urls_per_thread, len(urls))
            combine_threads.append(CombineThread(urls[beg:end]))

        # 启动线程
        for combine_thread in combine_threads:
            combine_thread.start()
        
        # 同步线程
        for combine_thread in combine_threads:
            combine_thread.join()

if __name__ == '__main__':
    # 当前目录绝对路径
    DIR = os.path.abspath('.')

    # 得到所有要合并的文件的 URL
    urls = [os.path.join(DIR, file[:-8]) for file in os.listdir(DIR) if file.endswith('[00].mp4')]

    for url in urls:
        print(url)

    AVCombiner().combine(urls=urls, max_threads=4)
    