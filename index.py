import mysql.connector
from datetime import date, datetime
import speech_recognition as sr
import cv2
import os
import re
import numpy as np
import face_recognition
from os import system, name
from fpdf import FPDF
from time import sleep
def clear():
	if name == 'nt': 
		_ = system('cls') 

	else: 
		_ = system('clear') 

PATH = 'C:\\Users\\punya\\Documents\\Sneha\\Voter Identification Automation\\images'
PATH_PDF = 'C:\\Users\\punya\\Documents\\Sneha\\Voter Identification Automation\\PDFDocs\\'

def printToPDF(dictionary, imageName):
    pdf = FPDF() 
    pdf.add_page() 
    pdf.set_font("Courier", 'B', size = 15) 
    pdf.cell(200, 5, txt = "----------------------------------------------------------------------------------------------------------", ln = 1, align = 'C')
    pdf.cell(200, 5, txt = "Election Commision of India", ln = 2, align = 'C')
    pdf.cell(200, 5, txt = "Voter's ID", ln = 3, align = 'C')
    pdf.cell(200, 10, txt = "---------------------------------------------------------------------------------------------------------", ln = 4, align = 'C')

    pdf.set_font("Courier", size = 12) 
    line = 5
    for i in dictionary:
        if i != 'Address' and i != 'photoSet':
            pdf.cell(200, 5, txt = str(i) + ": " + str(dictionary[i]), ln = line, align = 'L')
            line += 1
        elif i == 'Address':
            pdf.set_font("Courier", 'U', size = 12) 
            pdf.cell(200, 8, txt = 'Address:', ln = line, align = 'L')
            line += 1
            pdf.set_font("Courier", size = 12) 
            for j in dictionary[i]:
                pdf.cell(200, 5, txt = str(j) + ": " + str(dictionary[i][j]), ln = line, align = 'L')
                line += 1

    pdf.set_font("Courier", 'B', size = 12)
    pdf.cell(190, 10, txt = "Authorized signature", ln = line, align = 'R')
    pdf.cell(190, 5, txt = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ln = line + 1, align = 'R')
    pdf.image(name = imageName, x = 145, y = 35, w = 50, h = 40, type = 'JPG')
    pdf.output(PATH_PDF + dictionary['Name']+'.pdf')

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)

def capturePhoto(name):
    print("Points to note before taking photo: ")
    print("Make sure that there is enough light on face\n \
            Take off spectacles if any and look straight into the camera\n \
            Press space bar to capture the photo\n \
            Take atleast 6 photos and maximum of 10\n \
            Press escape to close the camera\n")

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Voter Photo Capture")
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Voter Photo Capture", frame)
        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "{}.jpg".format(name)
            cv2.imwrite(os.path.join(PATH, img_name), frame)
            print("{} written!".format(img_name))
    cam.release()
    cv2.destroyAllWindows()
    return PATH +'\\' + img_name
    

def calculateAge(birthDate):
    birthDate = datetime.strptime(birthDate, '%Y/%m/%d').date()
    today = date.today() 
    age = today.year - birthDate.year - \
         ((today.month, today.day) < \
         (birthDate.month, birthDate.day))
    return age

def register():
    dob = input("Elector's DoB (YYYY/MM/DD): ")
    if calculateAge(dob) < 18:
        print("Candidate not eligible to vote")
        return
    voter = {}
    voter['DoB'] = dob
    voter['Name'] = input("Elector's name: ")
    voter['Father_name'] = input("Father's name: ")
    voter['Gender'] = input("Gender (Enter 'M' for male and 'F' for female): ")
    voter['Address'] = {}
    voter['Address']['DoorNo'] = input("Address\nDoor number: ")
    voter['Address']['Street'] = input("Street: ")
    voter['Address']['Area'] = input("Area / Locality: ")
    voter['Address']['Landmark'] = input("Landmark: ")
    voter['Address']['City'] = input("City / Town / Village: ")
    voter['Address']['District'] = input("District: ")
    voter['Address']['State'] = input("State: ")
    voter['Address']['Pin'] = input("PIN code: ")
    voter['Phone'] = input("Enter phone number (10 digits): ")
    voter['Voter ID'] = voter['Address']['State'][0] \
                        + voter['Address']['District'][0] \
                        + voter['Address']['City'][0] \
                        + voter['Address']['Pin']
    voter['photoSet'] = capturePhoto(voter['Name'].split()[0])
    imagePath = voter['photoSet']
    voter['photoSet'] = convertToBinaryData(voter['photoSet'])
    try:
        recordTuple = (voter['Voter ID'], voter['Name'], dob, voter['Father_name'], voter['Gender'], voter['photoSet'])
        query = "insert into `voter` (`voterId`, `voterName`, `dob`, `fatherName`, `gender`, `photoSet`) values (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, recordTuple)
        db.commit()

        recordTuple = (voter['Voter ID'], voter['Address']['DoorNo'], \
                                voter['Address']['Street'], voter['Address']['Area'], \
                                voter['Address']['Landmark'], voter['Address']['City'], \
                                voter['Address']['District'], voter['Address']['State'], \
                                voter['Address']['Pin'], voter['Phone'])
        query = "insert into `address` (`voterId`, `door`, `street`, `area`, `landmark`, `city`, `district`, `state`, `pin`, `phone`) \
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, recordTuple)
        db.commit()
        printToPDF(voter, imagePath)
        print("Successfully inserted! Check PDF for Voter's ID")
        sleep(5)
    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))

def facial_recognition(imageName, voterName):
    video_capture = cv2.VideoCapture(0)
    image = face_recognition.load_image_file(imageName)
    face_encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings = [face_encoding]
    known_face_names = [voterName]

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return True
                face_names.append(name)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            cv2.destroyAllWindows()
            return False

def authenticate():
    r = sr.Recognizer()
    r.pause_threshold = 0.7
    r.energy_threshold = 400
    message = ''
    with sr.Microphone() as source:
        inp = 'n'
        while inp == 'n':
            try:
                r.adjust_for_ambient_noise(source)
                print("Say your voterID to mic clearly: ")
                audio = r.listen(source, timeout = 3)   # Listen to the input given by the user through mic
                print("Recorded. Please wait for authentication")
                voterID = str(r.recognize_google(audio))
                voterID = re.sub(' ','',voterID)    # Remove extra spaces generated if any
                voterID = voterID.upper()
                print("You said: ", voterID)
                inp = input("Press 'y' if that is what you said or press 'n' to try again: ")
            except sr.UnknownValueError:
                print('Google Speech Recognition could not Understand audio')
            except sr.RequestError as e:
                print('Could not request result from Google Speech Recogniser Service')
            except sr.WaitTimeoutError as e:
                print("Seems like you didn't speak anything.")
    try:
        recordTuple = (voterID,)
        recordTuple = (voterID,)
        query = "select * from `voter` where `voterId` = %s"
        cursor.execute(query, recordTuple)
        voterDetails = cursor.fetchone()
        if voterDetails == None:
            print("No such user exists")
            return
        print("VoterId: ", voterDetails[0])
        print("Name: ", voterDetails[1])
        print("Date of birth: ", voterDetails[2])
        print("Father Name: ", voterDetails[3])
        print("Gender: ", voterDetails[4])
        sleep(10)
        image = voterDetails[5]
        fileName = PATH + "\\" + voterDetails[1].split()[0] + '.jpg'
        write_file(image, fileName)
        try_again = 'y'
        while try_again == 'y' or try_again == 'Y':
            if facial_recognition(fileName, voterDetails[1]):
                return True
            else:
                print("Voter not recognised!")
                try_again = input("Press 'y' if you want to try again. Else, press 'n")
                if try_again == 'n' or try_again == 'N':
                    return False

    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))

if __name__ == "__main__":
    db = mysql.connector.connect(host ="localhost", database='electionAutomation', user='root', password='password', auth_plugin='mysql_native_password')
    if db.is_connected():
        cursor = db.cursor()
    else:
        print("Unable to connect to database!")
        exit(0)
    while True:
        clear()
        print("\n\n\n")
        print("----------Welcome to voter management system----------")
        print("Press 1 for Registering new user")
        print("Press 2 for Authenticating")
        print("Press 3 to exit")
        n = int(input("Enter the input: "))
        if n == 1:
            register()
        elif n == 2:
            if authenticate():
                clear()
                print("Voter authenticated! Thanks for being a responsible citizen by choosing to vote! Go ahead and exercise your right!")
                sleep(10)
                clear()
            else:
                clear()
                print("Voter not recognised")
                sleep(10)
                clear()
        elif n == 3:
            clear()
            exit(0)
        else:
            print("Invalid input! Try again!")