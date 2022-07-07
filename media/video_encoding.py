from logging.config import valid_ident
import os
import time
import subprocess
from multiprocessing import Process
import socket

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

def h264_encoding(videoName):
    videoPath = './raw'
    savePath = './h264'
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
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8')
    for line in process.stdout:
        # 콘솔에 time 정보가 나오면
        if 'time=' in line:
            t = line.split('time=')[1][:8]
            h, m, s = map(int, t.split(':'))
            t = 3600*h + 60*m + s
            progress = int(t/data['duration']*100) # 진행률
            
            current = time.time()
            if progress:
                expectEnd = int((current-start)*((100/progress)-1))
                print(videoName, '-', progress, expectEnd, '초 남음', end='\r')
    print('\n', int(time.time() - start), '초 소요')

    if not os.path.isdir(os.path.join('./dash', videoName[:-4])):
        os.makedirs(os.path.join('./dash', videoName[:-4]))
    message(videoName[:-4]+".mp4")
    out, err = process.communicate()
    exitcode = process.returncode
    if exitcode != 0:
        print(exitcode, out.decode('utf8'), err.decode('utf8'))

def dash_encoding(videoName, width, height):
    videoPath = './h264'
    savePath = './dash'
    savePath = os.path.join(savePath, videoName[:-4])    
    savePath = f'{os.path.join(savePath,videoName[:-4])}_{width}x{height}'
    if not os.path.isdir(savePath):
        os.makedirs(savePath)
    data = get_length(os.path.join(videoPath, videoName))

    command = [ 'ffmpeg',
                '-y', '-i', os.path.join(videoPath,videoName),
                '-vf', f'scale={width}:{height}',
                '-seg_duration', '10',
                '-keyint_min', '150',
                '-g', '150',
                '-f', 'dash',
                f'{os.path.join(savePath,videoName[:-4])}_{width}x{height}.mpd'
            ]
    start = time.time()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    out, err = process.communicate()
    exitcode = process.returncode
    if exitcode != 0:
        print(exitcode, out, err)

def message(videoName):
    Host = '127.0.0.1' # 연결할 서버의 외부 IP 주소
    Port = 4000        # 연결할 서버의 포트번호

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((Host, Port))

    client_socket.sendall(('p'+videoName).encode())
    client_socket.close()

#h264_encoding()

#p1 = Process(target=x264_encoding, args=())
#p2 = Process(target=x264_encoding, args=())

#p1.start()
#p2.start()

#p1.join()
#p2.join()
