#!/usr/bin/env python3
import telnetlib
import time

HOST = "localhost"
PORT = 2222
USER = "CS401"
PASSWORD = "Password"

def send_command(tn, command):
    tn.write(command.encode('utf-8') + b"\n")
    time.sleep(1)
    return tn.read_very_eager().decode('utf-8')

def automated_testing():
    tn = telnetlib.Telnet(HOST, PORT)
    time.sleep(2)
    
    # Login attempt
    tn.read_until(b"server login: ")
    tn.write(USER.encode('utf-8') + b"\n")
    tn.read_until(b"Password: ")
    tn.write(PASSWORD.encode('utf-8') + b"\n")
    
    time.sleep(2)
    
    # Initial set of commands
    commands_set1 = [
        "ls",
        "cd Documents",
        "ls",
        "cat Password.txt",
        "whoami",
        "ping 127.0.0.1",
        "ifconfig",
        "netstat",
        "uname -a"
    ]
    
    # Additional commands and sequences
    commands_set2 = [
        "cd /",
        "ls -l",
        "df -h",
        "ps aux",
        "top -n 1",
        "uptime",
        "hostname",
        "last",
        "du -sh *"
    ]
    
    # Execute command sets
    for command in commands_set1:
        response = send_command(tn, command)
        print(f"Sent: {command}\nReceived: {response}")

    for command in commands_set2:
        response = send_command(tn, command)
        print(f"Sent: {command}\nReceived: {response}")

    # Additional sequences of commands
    commands_set3 = [
        "mkdir test_directory",
        "cd test_directory",
        "touch file1.txt file2.txt",
        "ls -l",
        "rm file1.txt",
        "cd ..",
        "rmdir test_directory"
    ]

    for command in commands_set3:
        response = send_command(tn, command)
        print(f"Sent: {command}\nReceived: {response}")

    tn.close()

if __name__ == "__main__":
    automated_testing()