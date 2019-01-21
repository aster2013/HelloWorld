#! /usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import os
import sys
import threading
import urllib.request

# 检查是否安装 you-get
try:
    import you_get
except ImportError:
    # 自动安装 you-get
    print('pip install you-get')
    os.system('pip install you-get')

# 这个脚本用于下载 YouTube 站点上的视频
# Aster Jian (asterjian@qq.com), 2019-01-18

# 注：如果下载到的是分开的视频和音频文件，请使用 av_combine.py 合并视频和音频

class UrlsProvider(ABC):
    ''' 视频 URL 提供者'''
    
    @abstractmethod
    def get_video_urls(self):
        '''得到视频的 URL'''

        raise NotImplementedError

class FileUrlsProvider(UrlsProvider):
    ''' 文件 URL 提供者'''

    def __init__(self, filename):
        self.filename = filename

    def get_video_urls(self):
        if not os.path.exists(self.filename):
            return []

        with open(self.filename, 'rt') as file:
            return [line.strip() for line in file]

class PageUrlsProvider(UrlsProvider):
    ''' 网页 URL 提供者'''

    def __init__(self, page_url, http_proxy=None):
        self.page_url = page_url
        self.http_proxy = http_proxy

    def get_video_urls(self):
        # 普通的视频网页
        if not 'https://www.youtube.com/playlist?list' in self.page_url:
            return [self.page_url]

        # 对于播放列表网页，解析里面的内容，并返回所有的视频列表

        # 是否使用代理
        if self.http_proxy:
            proxy_handler = urllib.request.ProxyHandler({ 'http': self.http_proxy })
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

        # 从页面中得到所有视频的 URL
        video_urls = []
        for element in urllib.request.urlopen(self.page_url).readlines():
            element = element.decode('utf-8')
            if 'pl-video-title-link' in element:
                video_urls.append('https://www.youtube.com/watch?v=' + element.split('href="/watch?v=')[1].split('&amp;')[0])

        return video_urls

class YouTubeDownloader(object):
    '''YouTube 视频下载器'''

    def download(self, urls_provider, max_threads, http_proxy=None):
        # 读取所有的URL
        urls = urls_provider.get_video_urls()
        
        for url in urls:
            print('url:', url)

        # 线程数目
        num_threads = min(max_threads, len(urls))

        # 每个线程分配的URL数目
        urls_per_thread = len(urls) // num_threads
        if len(urls) % num_threads != 0:
            urls_per_thread += 1

        print('num_urls =', len(urls))
        print('num_threads =', num_threads)
        print('urls_per_thread =', urls_per_thread)
        
        # 所有下载线程列表
        download_threads = []
        
        for i in range(num_threads):
            # 将每一段 URL 分配给一个线程
            beg = i * urls_per_thread
            end = min(beg + urls_per_thread, len(urls))
            download_threads.append(DownloadThread(urls[beg:end], http_proxy))

        # 启动线程
        for download_thread in download_threads:
            download_thread.start()
        
        # 同步线程
        for download_thread in download_threads:
            download_thread.join()

class DownloadThread(threading.Thread):
    '''下载线程'''
    
    def __init__(self, urls, http_proxy=None):
        super().__init__()
        self.urls = urls
        self.http_proxy = http_proxy or ''

    def run(self):
        # 调用 you-get 下载每一个 URL
        for url in self.urls:
            # print('you-get -x {} {}'.format(self.http_proxy, url))
            os.system('you-get -x {} {}'.format(self.http_proxy, url))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python av_download.py <filename or page_url>')
    else:
        # 最大线程数目（根据需要修改）
        max_threads = 16
        
        # HTTP 代理（根据需要设置或关闭）
        # http_proxy = None
        http_proxy = 'web-proxy.oa.com:8080'

        if os.path.exists(sys.argv[1]):
            # 从文件读取视频URL
            urls_provider = FileUrlsProvider(sys.argv[1])
        else:
            # 从网页读取视频URL
            urls_provider = PageUrlsProvider(sys.argv[1], http_proxy)

        # 开始下载所有视频
        YouTubeDownloader().download(urls_provider, max_threads, http_proxy)
     