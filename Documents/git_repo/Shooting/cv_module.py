import cv2

cap = cv2.VideoCapture('charan_video.mts')
fps = cap.get(cv2.CAP_PROP_FPS)
No_of_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
#timestamps = [cap.get(cv2.CAP_PROP_POS_MSEC)]
print(fps)
print(No_of_frames)

#calc_timestamps = [0.0]

#while(cap.isOpened()):
#    frame_exists, curr_frame = cap.read()
#    if frame_exists:
#        timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
#        calc_timestamps.append(calc_timestamps[-1] + 1000/fps)
#    else:
#        break

#cap.release()

#for i, (ts, cts) in enumerate(zip(timestamps, calc_timestamps)):
#    print('Frame %d difference:'%i, abs(ts - cts))
