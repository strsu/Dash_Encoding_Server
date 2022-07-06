import os
import time
import subprocess
from multiprocessing import Process

#os.environ['path'] = r'C:\ffmpeg-4.4.1\bin\ffmpeg.exe'
#workdir = os.path.dirname(os.path.realpath(__file__))

# https://trac.ffmpeg.org/wiki/FFprobeTips
# apt install ffmpeg

def get_length(input_video):
    result = subprocess.run([
        'ffprobe', '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=width,height,duration,bit_rate', 
        '-of', 'default=noprint_wrappers=1', input_video], 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #result = result.stdout.decode()[:-2].split('\r\n') # windows
    result = result.stdout.decode()[:-2].split('\n') # linux
    data = {}
    for d in result:
        key, val = d.split('=')
        data[key] = int(float(val))
    return data

def name_refine(videoName):
    videoName = str(videoName)
    videoName = videoName.replace('[','').replace(']','')
    videoName = videoName.replace(' ','_')
    return videoName

def h264_encoding(videoName):
    videoName = name_refine(videoName)
    videoPath = './media/raw'
    savePath = './media/h264'
    data = get_length(os.path.join(videoPath, videoName))

    command = [ 'ffmpeg',
                #'-hwaccel', 'cuda', # 이유는 모르겟는데 gpu가 더 느림, cpu 평균 65 -> gpu 평균 140 ???
                '-y', '-i', os.path.join(videoPath,videoName),
                '-vcodec', 'libx264',
                '-acodec', 'aac',
                '-pix_fmt', 'yuv420p',
                f'{os.path.join(savePath,videoName[:-4]+".mp4")}'
            ]
    start = time.time()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        # 콘솔에 time 정보가 나오면
        if 'time' in line:
            t = line.split('time=')[1][:8]
            h, m, s = map(int, t.split(':'))
            t = 3600*h + 60*m + s
            progress = int(t/data['duration']*100) # 진행률
            
            current = time.time()
            if progress:
                expectEnd = int((current-start)*((100/progress)-1))
                #print(progress, expectEnd, '초 남음')
    #print(int(time.time() - start), '초 소요')
    out, err = process.communicate()
    exitcode = process.returncode
    if exitcode != 0:
        print(exitcode, out.decode('utf8'), err.decode('utf8'))

#h264_encoding()

#p1 = Process(target=x264_encoding, args=())
#p2 = Process(target=x264_encoding, args=())

#p1.start()
#p2.start()

#p1.join()
#p2.join()
