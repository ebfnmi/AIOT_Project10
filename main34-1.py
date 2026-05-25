import cv2 # 실시간 영상 처리를 위한 OpenCV 라이브러리를 불러옵니다.
from gpiozero import Buzzer # 라즈베리파이 GPIO 핀으로 부저를 제어하기 위한 라이브러리를 불러옵니다.
import time # 시간 지연 등의 기능을 사용하기 위해 내장 time 라이브러리를 불러옵니다.

buzzerPin = Buzzer(16) # 라즈베리파이 GPIO 16번 핀에 연결된 능동부저 객체를 생성합니다.

def main(): # 프로그램의 메인 로직을 수행할 main 함수를 정의합니다.
    camera = cv2.VideoCapture(-1) # 시스템에 연결된 기본 카메라 디바이스(-1)를 활성화합니다.
    camera.set(3,640) # 웹캠 입력 영상의 가로 해상도를 640 픽셀로 설정합니다.
    camera.set(4,480) # 웹캠 입력 영상의 세로 해상도를 480 픽셀로 설정합니다.
    
    face_xml = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml' # OpenCV가 제공하는 기본 얼굴 검출 모델 파일의 경로를 지정합니다.
    eye_xml = cv2.data.haarcascades + 'haarcascade_eye.xml' # OpenCV가 제공하는 기본 눈 검출 모델 파일의 경로를 지정합니다.
    face_cascade = cv2.CascadeClassifier(face_xml) # 얼굴 검출 모델 정보를 기반으로 얼굴 분류기 객체를 생성합니다.
    eye_cascade = cv2.CascadeClassifier(eye_xml) # 눈 검출 모델 정보를 기반으로 눈 분류기 객체를 생성합니다.
    
    while( camera.isOpened() ): # 카메라 장치가 정상적으로 열려 있고 연결된 동안 반복 루프를 실행합니다.
        _, image = camera.read() # 카메라로부터 실시간 영상의 현재 프레임(image)을 읽어옵니다.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 객체 검출 연산 속도를 높이기 위해 컬러 영상을 흑백 이미지로 변환합니다.

        faces = face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(100,100),flags=cv2.CASCADE_SCALE_IMAGE) # 흑백 영상에서 설정한 파라미터 조건에 맞는 얼굴 영역들을 탐지합니다.
        print("faces detected Number: " + str(len(faces))) # 현재 프레임에서 탐지된 얼굴의 총 개수를 터미널 창에 실시간 출력합니다.

        if len(faces): # 탐지된 얼굴이 최소 1개 이상 존재할 경우 내부 조건문을 실행합니다.
            for (x,y,w,h) in faces: # 탐지된 얼굴들의 위치 좌표와 크기(x, y, 가로, 세로)를 하나씩 꺼내옵니다.
                cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2) # 원본 컬러 영상의 얼굴 위치에 파란색(255,0,0) 사각형 테두리를 그립니다.
                
                face_gray = gray[y:y+h, x:x+w] # 얼굴 구역에 해당하는 흑백 이미지 영역을 눈 검출용 관심 영역(ROI)으로 잘라냅니다.
                face_color = image[y:y+h, x:x+w] # 얼굴 구역에 해당하는 컬러 이미지 영역을 사각형 시각화용 관심 영역(ROI)으로 잘라냅니다.
                
                eyes = eye_cascade.detectMultiScale(face_gray,scaleFactor=1.1,minNeighbors=5) # 잘라낸 얼굴 내부의 흑백 관심 영역에서 눈 구역들을 탐지합니다.
                
                if len(eyes) <= 1: # 눈이 감기거나 가려져 감지된 눈의 개수가 1개 이하가 되면 졸음 상태로 판단합니다.
                    buzzerPin.on() # 졸음 상태이므로 라즈베리파이 GPIO 핀을 활성화하여 능동부저를 울립니다.
                else: # 감지된 눈의 개수가 2개 이상으로 정상적인 상태라면 실행합니다.
                    buzzerPin.off() # 정상 상태이므로 라즈베리파이 GPIO 핀을 비활성화하여 부저를 끕니다.
                
                for (ex,ey,ew,eh) in eyes: # 탐지된 눈들의 얼굴 기준 상대 좌표와 크기를 하나씩 꺼내옵니다.
                    cv2.rectangle(face_color, (ex, ey), (ex+ew, ey+eh), (0,255,0), 2) # 얼굴 컬러 영역 내의 눈 위치에 초록색(0,255,0) 사각형 테두리를 그립니다.
        
        cv2.imshow('result', image) # 최종 사각형들이 시각화된 결과 영상 화면을 'result'라는 이름의 GUI 창에 표시합니다.
        
        if cv2.waitKey(1) == ord('q'): # 매 프레임마다 1ms 동안 키보드 입력을 대기하며, 사용자가 'q' 키를 누르면 루프를 탈락합니다.
            break # 'q' 키가 입력되었으므로 프레임을 읽어오는 while 반복 루프를 종료합니다.
    
    cv2.destroyAllWindows() # 프로그램이 생성한 모든 OpenCV GUI 이미지 출력 창을 닫습니다.
    buzzerPin.off() # 프로그램이 최종 종료되기 전에 회로의 부저가 켜져 있다면 안전하게 니다.

if __name__ == '__main__': # 프로그램이 최종 종료되기 전에 회로의 부저가 켜져 있다면 안전하게 니다.
    main() # 조건이 참일 경우 최상단의 main 함수를 호출하여 프로그램을 본격적으로 시작합니다.