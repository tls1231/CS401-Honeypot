from flask import Flask, render_template, jsonify, request
import sqlite3
import pandas as pd

app = Flask(__name__)
DATABASE = 'honeypot_logs.db'

# Fetch logs from the database
def fetch_logs():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs")
    logs = cursor.fetchall()
    conn.close()
    return logs

# Analyze logs
def analyze_logs(logs):
    # Debug print to check the structure of logs
    print("Fetched Logs:", logs)

    # Adjust the columns based on the actual data structure
    if logs and len(logs[0]) == 5:  # Assuming there's an extra column
        df = pd.DataFrame(logs, columns=['ID', 'Timestamp', 'Source IP', 'Destination IP', 'Data'])
    else:
        df = pd.DataFrame(logs, columns=['Timestamp', 'Source IP', 'Destination IP', 'Data'])

    # Drop the 'ID' column if it exists
    if 'ID' in df.columns:
        df.drop(columns=['ID'], inplace=True)

    # Frequency of commands executed
    command_freq = df['Data'].value_counts().to_dict()

    # Unique source and destination IP addresses
    unique_ips = {
        'Source IPs': df['Source IP'].unique().tolist(),
        'Destination IPs': df['Destination IP'].unique().tolist()
    }

    # Detect failed login attempts (example: specific command patterns)
    failed_logins = df[df['Data'].str.contains('Password') & ~df['Data'].str.contains('Password: Password')].shape[0]

    analysis_results = {
        'command_freq': command_freq,
        'unique_ips': unique_ips,
        'failed_logins': failed_logins
    }

    return analysis_results

@app.route('/analyze/', methods=['GET', 'POST'])
def analyze_logs_route():
    if request.method == 'POST':
        logs = fetch_logs()
        analysis_results = analyze_logs(logs)
        return render_template('analysis.html', analysis_results=analysis_results)

    return render_template('analyze.html')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs/')
def logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC').fetchall()
    conn.close()
    print([dict(log) for log in logs])  # Debug print statement
    return render_template('logs.html', logs=logs)

@app.route('/test/')
def test():
    return render_template('test.html')

@app.route('/api/logs/')
def api_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(log) for log in logs])

@app.route('/file_changes/')
def file_changes():
    conn = get_db_connection()
    changes = conn.execute('SELECT * FROM file_changes ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('file_changes.html', changes=changes)

@app.route('/api/file_changes/')
def api_file_changes():
    conn = get_db_connection()
    changes = conn.execute('SELECT * FROM file_changes ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(change) for change in changes])

if __name__ == "__main__":
    app.run(debug=True)
