import json
from django.shortcuts import render

from django.views.decorators import gzip
from django.http import HttpResponseBadRequest, JsonResponse, StreamingHttpResponse
import cv2
import numpy as np
import mediapipe as mp
import base64


def angle_between(a,b,c):
    a = np.array(a)
    b= np.array(b)
    c = np.array(c)
    
    radians= np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    return angle 

def capture_video_frame(request):
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    tree_angles = {"elbow_angle_left_min":27.69,"elbow_angle_left_max":60.17,
                 "shoulder_angle_left_min":15.38,"shoulder_angle_left_max":59.76,
                 "hip_angle_left_min":106.03,"hip_angle_left_max":179.40,
                 "knee_angle_left_min":22.81,"knee_angle_left_max":178.53,
                 "elbow_angle_right_min":25.30,"elbow_angle_right_max":56.31,
                 "shoulder_angle_right_min":9.42,"shoulder_angle_right_max":54.12,
                 "hip_angle_right_min":100.3,"hip_angle_right_max":179.7,
                 "knee_angle_right_min":18.01,"knee_angle_right_max":179.83}
    p = 0.98
    q = 1.02
    angles = tree_angles
    if request.method == 'POST':
        # frame_data = json.loads(request.body.decode('utf-8')).get('frame_data')
        # frame_data = frame_data.split(',')[1]  # Remove the "data:image/jpeg;base64," prefix
        # frame_data = base64.b64decode(frame_data)
        data = json.loads(request.body)
        frame_data = base64.b64decode(data['frame_data'].split(',')[1])
        image_array = np.frombuffer(frame_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        # print(image)
        # resized_image = cv2.resize(image, (3, 2))
        cap = cv2.VideoCapture(0)
        with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
            
            # ret,frame = cap.read()
            img=image

            results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # results = pose.process(image)
            
            # image.flags.writeable = True
            # image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            
            try:
                landmarks = results.pose_landmarks.landmark
                shoulder_left = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow_left = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist_left = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                hip_left = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                ankle_left = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                knee_left = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                ankle_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                knee_right = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                
                a = angle_between(wrist_left,elbow_left,shoulder_left)
                b = angle_between(elbow_left,shoulder_left,hip_left)
                c = angle_between(shoulder_left,hip_left,knee_left)
                d = angle_between(hip_left,knee_left,ankle_left)
                e = angle_between(wrist_right,elbow_right,shoulder_right)
                f = angle_between(elbow_right,shoulder_right,hip_right)
                g = angle_between(shoulder_right,hip_right,knee_right)
                h = angle_between(hip_right,knee_right,ankle_right)
                
                
                
                if ((angles.get("elbow_angle_left_min") * p < a < angles.get("elbow_angle_left_max") * q) 
                    and (angles.get("shoulder_angle_left_min") * p  < b < angles.get("shoulder_angle_left_max") * q) 
                    and (angles.get("hip_angle_left_min") * p < c < angles.get("hip_angle_left_max")  * q )
                    and (angles.get("knee_angle_left_min") * p< d < angles.get("knee_angle_left_max") * q)
                    and (angles.get("elbow_angle_right_min") * p < e < angles.get("elbow_angle_right_max") * q)
                    and (angles.get("shoulder_angle_right_min") * p < f < angles.get("shoulder_angle_right_max") * q) 
                    and (angles.get("hip_angle_right_min") * p < g < angles.get("hip_angle_right_max") * q) 
                    and (angles.get("knee_angle_right_min") * p < h < angles.get("knee_angle_right_max") * q )):
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color =(255,81,31), thickness = 3, circle_radius =2),
                                    mp_drawing.DrawingSpec(color =(57,255,20), thickness = 3, circle_radius =2))
                else:
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color =(255,81,31), thickness = 3, circle_radius =2),
                                    mp_drawing.DrawingSpec(color =(0,0,255), thickness = 3, circle_radius =2))

                    
            except:
                pass
            
        # cv2.imwrite("X.jpg", image)
        _, processed_image_data = cv2.imencode('.jpg', image)
        processed_frame_data = base64.b64encode(processed_image_data).decode('utf-8')
        print(processed_frame_data)

        # return JsonResponse({'result': frame_data})
        return JsonResponse({'processed_frame_data': processed_frame_data})

        # if frame_data is not None:
        #     # Process the frame data
        #     # Your processing code here
        #     result = "Frame processed successfully"  # Replace with actual result
        #     return JsonResponse({'result': result})
        # else:
        #     return JsonResponse({'error': 'Invalid frame data'})
    else:
        return HttpResponseBadRequest('Invalid request method')

def Home(request):
    return render(request, 'Home.html')