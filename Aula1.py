import csv
import datetime
import os
import random
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

def get_creds():
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def send_email(service, subject, body, to, gmail_user):
    message = MIMEText(body)
    message['to'] = to
    message['from'] = gmail_user
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    message = {'raw': raw_message}

    try:
        message = (service.users().messages().send(userId="me", body=message).execute())
        print(f"Message Id: {message['id']} sent to {to}")
    except HttpError as error:
        print(f"An error occurred: {error}")

def collect_user_data():
    data = []
    num_participants = int(input("Enter the number of participants: "))
    for _ in range(num_participants):
        name = input("Enter name: ")
        email = input("Enter email: ")
        data.append((name, email))
    return data

def save_data_to_csv(data):
    filename = f"secret_santa_{datetime.datetime.now().strftime('%m-%d-%Y')}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email"])
        writer.writerows(data)
    return filename

def assign_secret_santas(data):
    participants = data[:]
    assignments = []
    
    while participants:
        giver = participants.pop(0)
        
        while True:
            potential_receivers = [p for p in data if p != giver and p not in [assignment[1] for assignment in assignments]]
            if not potential_receivers:
                assignments = []
                participants = data[:]
                break
            receiver = random.choice(potential_receivers)
            if receiver != giver:
                assignments.append((giver, receiver))
                break

    return assignments

def send_secret_santa_emails(assignments, gmail_user, service):
    for giver, receiver in assignments:
        subject = "Secret Santa Assignment"
        body = f"Hello {giver[0]}, you need to buy a gift for {receiver[0]} ({receiver[1]})."
        send_email(service, subject, body, giver[1], gmail_user)

def rename_and_move_file(filename):
    new_filename = f"processed_{filename}"
    destination_path = r"C:\Users\mateu\OneDrive\Desktop\Python Course Bootcamp\processed_files"
    os.makedirs(destination_path, exist_ok=True)
    os.rename(filename, new_filename)
    os.replace(new_filename, os.path.join(destination_path, new_filename))
    print(f"File renamed to {new_filename} and moved to {destination_path}")

def main():
    creds = get_creds()
    service = build('gmail', 'v1', credentials=creds)

    data = collect_user_data()
    filename = save_data_to_csv(data)
    assignments = assign_secret_santas(data)
    gmail_user = 'mateus.16.veloso1@gmail.com'

    send_secret_santa_emails(assignments, gmail_user, service)
    rename_and_move_file(filename)

if __name__ == "__main__":
    main()
