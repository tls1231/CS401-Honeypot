#!/usr/bin/env python3
import socket
import threading
import datetime
import sqlite3
import atexit
import os

# Set up database connection
DATABASE = 'honeypot_logs.db'
LOGFILE = 'honeypot_logs.txt'

def exit_handler():
    print('\n[*] Honeypot is shutting down!')

atexit.register(exit_handler)

def char_remove(data):
    return data.decode('utf-8').strip()

def write_log(client, data='', user='', pas=''):
    timestamp = datetime.datetime.now().isoformat()
    source_ip = client.getpeername()[0]
    destination_ip = '127.0.0.1'
    log_data = f'User: {user}, Password: {pas}, Data: {data}'

    try:
        # Log to database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, source_ip, destination_ip, data)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, source_ip, destination_ip, log_data))
        conn.commit()
        conn.close()

        # Log to text file
        with open(LOGFILE, 'a') as f:
            f.write(f'{timestamp} - {source_ip} -> {destination_ip} : {log_data}\n')
        print(f"Logged: {log_data}")
    except Exception as e:
        print(f"Error writing to log: {e}")

def send_cmd_prompt(c, user_dict):
    cmd_prompts = [
        '\n┌──(root💀CS401)-[/home/CS401]└─#',
        '\n┌──(root💀CS401)-[/home/CS401/Desktop]└─#',
        '\n┌──(root💀CS401)-[/home/CS401/Documents]└─#',
        '\n┌──(root💀CS401)-[/home/CS401/Downloads]└─#',
        '\n┌──(root💀CS401)-[/home/CS401/Pictures]└─#',
        '\n┌──(root💀CS401)-[/home/CS401/Public]└─#',
        '\n┌──(root💀CS401)-[/home/CS401/Videos]└─#',
        '\n┌──(root💀CS401)-[/home/CS401/Database]└─#'
    ]
    c.sendall(bytes(cmd_prompts[user_dict], 'utf-8'))

def handle_commands(user_cmd, c, user_dict):
    if 'ls' in user_cmd:
        ls_output = 'Desktop\t\tDocuments\t\tDownloads\t\tPictures\t\tPublic\t\tVideos\t\tDatabase'
        c.sendall(bytes(ls_output, 'utf-8'))
        send_cmd_prompt(c, 0)
    elif 'cd' in user_cmd:
        directories = ['Desktop', 'Documents', 'Downloads', 'Pictures', 'Public', 'Videos', 'Database']
        for idx, dir_name in enumerate(directories):
            if dir_name in user_cmd:
                user_dict = idx + 1
                break
        send_cmd_prompt(c, user_dict)
    elif 'cat Password.txt' in user_cmd:
        user_dict = 7
        c.sendall(bytes('966b28d4f5b0a4e5f996dfededdb13d1c98019e7f16c7032c2a96c161c200922\n', 'utf-8'))
        send_cmd_prompt(c, user_dict)
    elif 'whoami' in user_cmd:
        c.sendall(bytes('root', 'utf-8'))
        send_cmd_prompt(c, user_dict)
    else:
        c.sendall(bytes('Command not found', 'utf-8'))
        send_cmd_prompt(c, user_dict)
    return user_dict

def handle_client(client):
    user_dict = 0
    client.sendall(b'Kali GNU/Linux Rolling\n(')
    client.sendall(bytes('127.0.0.1', 'utf-8'))
    client.sendall(b') :anonymous\n')
    
    client.sendall(b'server login: ')
    username = char_remove(client.recv(2048))
    client.sendall(b'Password: ')
    password = char_remove(client.recv(2048))
    
    write_log(client, user=username, pas=password)
    
    if username != 'CS401' or password != 'Password':
        client.sendall(b'Login incorrect\nserver login: ')
        username = char_remove(client.recv(2048))
        client.sendall(b'Password: ')
        password = char_remove(client.recv(2048))
        write_log(client, user=username, pas=password)
        if username != 'CS401' or password != 'Password':
            client.sendall(b'Login incorrect\n')
            client.close()
            return
    
    client.sendall(b'\nWelcome to the honeypot\n')
    send_cmd_prompt(client, user_dict)
    
    while True:
        data = char_remove(client.recv(2048))
        if not data:
            break
        user_dict = handle_commands(data, client, user_dict)
        write_log(client, data=data, user=username, pas=password)
    
    client.close()

def start_honeypot():
    server_lstnr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_lstnr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_lstnr.bind(('0.0.0.0', 2222))  # Honeypot on port 2222
    server_lstnr.listen(5)
    print('Honeypot running on port 2222')

    while True:
        client, addr = server_lstnr.accept()
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    start_honeypot()
