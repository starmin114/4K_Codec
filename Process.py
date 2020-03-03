# -*-coding: utf-8 -*-
from PIL import Image, ImageSequence

import cv2

import os
from pathlib import Path
import enum

from multiprocessing import Pool , Process, Queue, active_children

import time

import atexit

def getRootDir(): 
    return "D:\PlayVideo"

class VideoEnum(enum.Enum):
    INDEX = 0
    NAME = 1
    FORMAT = 2
    PATH = 3
    WIDTH = 4
    HEIGHT = 5
    FPS = 6
    TOTAL_FRAME_NUMBER = 7
    LENGTH = 8

class FrameEnum(enum.Enum):
    INDEX = 0
    NAME = 1
    FORMAT = 2
    PATH = 3
    MSEC = 4
    RATIO = 5


class Video:

    def __init__(self, index, _format):
        self.index = index
        self.NAME = f"V{index}"
        self.FORMAT = _format
        self.PATH = os.path.join(getRootDir(), os.path.join(self.NAME,f"{self.NAME}.{self.FORMAT}"))

        
        video = cv2.VideoCapture(self.PATH)
        if (not video.isOpened()):
            print(f"Video {self.NAME} not opened.")
            return None
        
        self.WIDTH = int(video.get(3))
        self.HEIGHT = int(video.get(4))
        self.FPS = int(video.get(5))
        # FOURCC = video.get(6)
        self.TOTAL_FRAME_NUMBER = int(video.get(7))
        # FormatRetrieved = video.get(8)
        self.LENGTH = self.TOTAL_FRAME_NUMBER / self.FPS

        print("VideoOpened :")
        print(self)
        self.video = video
        self.METADATA = (self.index, self.NAME, self.FORMAT, self.PATH, self.WIDTH, self.HEIGHT, self.FPS, self.TOTAL_FRAME_NUMBER, self.LENGTH)

    def exhandler(self):
        self.pool.terminate()

    def getFrames(self, frameFormat, display = True, save = True, Thr = False):
        procs = []
        # frameCut = 100
        cntFrame = 0
        if(self.video is not None):
            self.time_start = time.time()

            while(True):
                frameExist, frame = self.video.read()
                if(frameExist):
                    framePosByMSec = self.video.get(0)
                    framePosByFrameNumber = int(self.video.get(1))
                    framePosByRatio = self.video.get(2)

                    # proc = Process(target = self.Thr_getFrames, args = (self.video, frame, frameFormat, display, save))
                    var = (self.time_start, self.METADATA, frame, [framePosByFrameNumber, None ,frameFormat, None, framePosByMSec, framePosByRatio], display, save,)
                    
                    # q.put()
                    
                    if(Thr):
                        while len(active_children()) >= 16:
                            time.sleep(0.5)
                        proc = Process(target=Thr_getFrames, args=(var))
                        procs.append(proc)
                        proc.start()
                    else:
                        Thr_getFrames(self.time_start, self.METADATA, frame, [framePosByFrameNumber, None ,frameFormat, None, framePosByMSec, framePosByRatio], display, save)

                    # print("Process # :: ",len(active_children()))
                else:
                    break

                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

                cntFrame += 1
            
            # for proc in procs:
            #     proc.join()

            print((time.time()-self.time_start)/cntFrame)
        else:
            print("There is no video opened")
            return -1
       
    
    def __repr__(self):
        return f"""
        VideoPath   : {self.PATH}.
        Size        : ({self.WIDTH} x {self.HEIGHT})
        Length      : [{self.TOTAL_FRAME_NUMBER}]frames / [{self.FPS}]fps = {self.LENGTH}s
        """
    
    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()
    
    def __get__(self):
        return self.video

class Frame:
    def __init__(self, RGBarray, frameMetaData, videoMetaData):
        self.index = frameMetaData[FrameEnum.INDEX.value]
        self.FORMAT = frameMetaData[FrameEnum.FORMAT.value]
        self.NAME = frameMetaData[FrameEnum.NAME.value] = f"F{self.index}"
        self.PATH = frameMetaData[FrameEnum.PATH.value] = os.path.join(getRootDir(), os.path.join(videoMetaData[VideoEnum.NAME.value], os.path.join("Frames",f"{self.NAME}.{self.FORMAT}")))
        self.MSEC = frameMetaData[FrameEnum.MSEC.value]
        self.RATIO = frameMetaData[FrameEnum.RATIO.value]
        self.RGBarray = RGBarray #default
        self.PILimage = Image.fromarray(self.RGBarray)
        self.video = videoMetaData
        self.METADATA = tuple(frameMetaData)

    def toPILimage(self):
        if self.PILimage is not None:
            return self.PILimage
        else:
            self.PILimage = Image.fromarray(self.RGBarray)
            return self.PILimage

    def getTiles(self, start_time):
        path = os.path.dirname(self.PATH)
        path = os.path.join(path, str(self.index))
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("cannot make dir" + path)

        MAX_WIDTH = int(self.video[VideoEnum.WIDTH.value]/64)
        MAX_HEIGHT = int(self.video[VideoEnum.HEIGHT.value]/64)
        

        for i in range(MAX_WIDTH):
            for j in range(MAX_HEIGHT):
                tile = self.PILimage.crop((64 * i, 64 * j, 64 * i + 64, 64*j + 64))
                tile.save(os.path.join(path, f"{i}_{j}.png"))

        self.start_time = start_time

        self.save()

    def save(self):
        self.PILimage.save(self.PATH)
        print("saved" + str(self))
        # start_time[self.index] =  timeit.default_timer()

    def __get__(self):
        return self.RGBarray
    

    def __repr__(self):
        return f"Frame {self.index}/{self.video[VideoEnum.TOTAL_FRAME_NUMBER.value]} ({format(100*self.index/self.video[VideoEnum.TOTAL_FRAME_NUMBER.value],'3.3f')}%), Time {format(self.MSEC/1000,'10.4f')}/{self.video[VideoEnum.LENGTH.value]}, ElapsedT : {((time.time()-self.start_time))}"


def Thr_getFrames(start_time, videoMetaData, frame, frameMetaData, display, save):
    RGBarray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    frame = Frame(RGBarray, frameMetaData, videoMetaData)

    if display:
        rat = 0.5
        cv2.imshow(videoMetaData[VideoEnum.NAME.value],cv2.resize(frame.RGBarray, (int(3840 * rat), int(2160 * rat))))
    if save:
        frame.getTiles(start_time)
        
    return


if __name__ == "__main__":
    videoIndex = 1
    videoFormat = "mp4"
    frameFormat = "png"
    video = Video(videoIndex, videoFormat)
    video.getFrames(frameFormat, False, True, True)