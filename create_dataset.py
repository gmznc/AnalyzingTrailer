import pandas as pd
from pytube import YouTube
import os
import googleapiclient.discovery
from pytube import YouTube
import moviepy.editor as mp
import cv2
import numpy as np
import matplotlib.pyplot as plt



def get_youtube_video_url(search_keyword):
    api_key = 'AIzaSyAmLor-B8sbSo_JflHnvcrY5ZyEUyc8W4E'

    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    search_response = youtube.search().list(
        q=search_keyword,
        type='video',
        part='id,snippet',
        maxResults=1
    ).execute()

  
    video_id = search_response['items'][0]['id']['videoId']

    video_url = f'https://www.youtube.com/watch?v={video_id}'

    return video_url


data = pd.DataFrame(columns=["name","rate","image","sound"])
csv_path = 'movie.csv'
df = pd.read_csv(csv_path, sep=';')

for i in range(len(df)):
    search_keyword = df.iloc[i,0]
    
    video_url = get_youtube_video_url(search_keyword+" trailer")
    
    yt = YouTube(video_url)
    yr = yt.streams.get_highest_resolution()

    print("downloading...")
    wait = 1
    for j in range(3):
        print("{}/3".format(wait))
        wait +=1

    yr.download(filename=search_keyword+".mp4")
    
    # -------------------
    
    video_path = search_keyword +'.mp4'
    video_clip = mp.VideoFileClip(video_path)

    toplam_sure = video_clip.duration

    birinci_kisim = video_clip.subclip(0, 5)
    ikinci_kisim = video_clip.subclip((toplam_sure/2)-5, toplam_sure/2)
    ucuncu_kisim = video_clip.subclip(toplam_sure-5, toplam_sure)

    birlesik_klip = mp.concatenate_videoclips([birinci_kisim, ikinci_kisim, ucuncu_kisim])

    birlesik_klip.write_videofile('cropped_video.mp4', codec='libx264', audio_codec='aac')

    video_clip.close()
    
    # ------------------------
    
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    istenen_fps = 1 

    frame_adimi = int(fps / istenen_fps)

    ret, frame = cap.read()
    frame_sayaci = 1

    array_frame = []

    while ret:
        for _ in range(frame_adimi - 1):
            ret, _ = cap.read()

        
        frame2 = cv2.resize(frame, (128,128))
        frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        frame2 = np.array(frame2)
        array_frame.append(frame2)
        
        #cv2.imshow('Frame', frame2)
        cv2.waitKey(0)

        ret, frame = cap.read()

        frame_sayaci += 1
        

    # cap.release()
    # cv2.destroyAllWindows()
    
    
    clip = mp.VideoFileClip(video_path)

    audio = clip.audio.to_soundarray()

    plt.specgram(audio[:, 0], Fs=clip.audio.fps)
    plt.savefig("spektrogra.png")
    plt.show()

    grafik = cv2.imread("spektrogra.png")
    grafik = cv2.resize(grafik, (128,128))


    
    new_data = {'name': search_keyword, 'rate': df.iloc[i,1], 'image': array_frame, 'sound': grafik}
    data = data.append(new_data, ignore_index=True)

data['image'] = data['image'].apply(lambda arr_list: np.concatenate(arr_list).flatten())
data['sound'] = data['sound'].apply(lambda arr_list: [arr.flatten().tolist() for arr in arr_list])

data.to_csv('output_data.csv', index=False)

