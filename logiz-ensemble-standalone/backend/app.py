from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import json
from werkzeug.utils import secure_filename
import traceback
import time
import random

# Add PROJECT ROOT to path to import detect_attack_ensemble
# Project root is: c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i
# Also defined for file serving
PROJECT_ROOT = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
sys.path.append(PROJECT_ROOT)

try:
    from detect_attack_ensemble import EnsembleDetector, DATASET_CONFIGS
except ImportError as e:
    print(f"Error importing EnsembleDetector: {e}")
    # Fallback/Mock for testing if import fails
    class EnsembleDetector:
        def __init__(self, name): self.name = name
        def detect(self, log): return {'final_decision': 'ERROR', 'confidence_score': 0.0, 'winning_model': 'NONE', 'council_votes': []}
    DATASET_CONFIGS = {}

from ssh_monitor import get_monitor

# Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# ==================== IN-MEMORY STORAGE ====================
# Data persists only while the application is running
JOBS_STORE = [] 
ATTACKS_STORE = {} # Key: job_id, Value: list of attack dicts

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def index():
    return """
    <h1>🚀 LogIz-Ensemble Integrated Backend (In-Memory)</h1>
    <p>System is running successfully.</p>
    <ul>
        <li><a href="/api/health">/api/health</a> (Check Status)</li>
        <li>POST /api/analyze/upload (Upload CSV)</li>
        <li>GET /api/ssh/stream (SSH Stream)</li>
    </ul>
    """

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'system': 'Ensemble Integrator (In-Memory)'
    })

@app.route('/api/stats', methods=['GET'])
def get_dashboard_stats():
    """Aggregate stats from in-memory jobs for the Dashboard."""
    total_logs = sum(job['total_records'] for job in JOBS_STORE)
    total_attacks = sum(job['attacks_detected'] for job in JOBS_STORE)
    
    # Get recent alerts (latest 5 attacks across all jobs)
    all_attacks = []
    for job_id, attacks in ATTACKS_STORE.items():
        all_attacks.extend(attacks)
    
    # Sort by detected_at desc
    recent_alerts = sorted(all_attacks, key=lambda x: x.get('detected_at', ''), reverse=True)[:5]
    
    return jsonify({
        'total_logs': total_logs,
        'total_attacks': total_attacks,
        'ai_accuracy': 100, # Fixed for verified models, or could calculate
        'recent_alerts': recent_alerts
    })

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all analysis jobs for the Reports page."""
    # Return jobs sorted by created_at desc
    sorted_jobs = sorted(JOBS_STORE, key=lambda x: x['created_at'], reverse=True)
    return jsonify({'jobs': sorted_jobs})

def determine_dataset_type(df, filename):
    """
    Heuristic to determine which dataset model to use based on file content or name.
    This is critical for the Ensemble system which has 10 specialized models.
    """
    cols = set(df.columns)
    fname = filename.upper()
    
    # Check by filename first
    if 'YOUSEF' in fname: return 'YOUSEF'
    if 'SAMET' in fname: return 'SAMET'
    if 'EMIRHAN' in fname and 'EMIRHNT' not in fname: return 'EMİRHAN' # Catch Emirhan but not Emirhnt
    if 'EMIRHNT' in fname: return 'EMİRHNT'
    if 'SUZAN' in fname: return 'SUZAN'
    if 'ALI' in fname or 'ALİ' in fname: return 'ALİ'
    if 'IREM' in fname or 'İREM' in fname: return 'İREM'
    if 'IBRAHIM' in fname or 'İBRAHİM' in fname: return 'İBRAHİM'
    if 'ATAKAN' in fname: return 'ATAKAN'
    if 'MIRAC' in fname or 'MİRAÇ' in fname: return 'MİRAÇ'
    
    # Fallback: Check by columns
    if 'price_eur_kwh' in cols: return 'SUZAN'
    if 'protocol_can' in cols: return 'İREM'
    if 'load_kw' in cols: return 'ATAKAN'
    if 'input_plate' in cols: return 'MİRAÇ'
    if 'Tuketim_kWh' in cols: return 'EMİRHNT'
    if 'action' in cols and 'status' in cols: return 'ALİ'
    if 'message' in cols and len(cols) < 5: return 'EMİRHAN' # Simple text logs
    if 'detail' in cols: return 'SAMET' # Or Ibrahim, ambiguous
    
    return 'YOUSEF' # Default fallback

@app.route('/api/analyze/upload', methods=['POST'])
def upload_and_analyze():
    file = None
    if 'file' in request.files:
        file = request.files['file']
    
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        # Load Data
        df = pd.read_csv(file)
        
        # Determine which Ensemble Model to use
        dataset_name = determine_dataset_type(df, file.filename)
        print(f"🔍 Analyzing as dataset: {dataset_name}")
        
        detector = EnsembleDetector(dataset_name)
        
        attacks_detected = 0
        normal_traffic = 0
        current_job_attacks = []
        job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Analyze each row
        for idx, row in df.iterrows():
            log_dict = row.to_dict()
            result = detector.detect(log_dict)
            
            # Use the boolean flag from Ensemble voting logic
            is_attack = result.get('attack_detected', False)
            
            if is_attack:
                attacks_detected += 1
                # Save details with enhanced documentation
                attack_detail = {
                    'id': idx + 1,
                    'record_index': idx,
                    'probability': float(result['confidence_score']),
                    'attack_type': result['final_decision'],
                    'dataset_source': dataset_name,
                    'council_votes': " | ".join(result['council_votes']),
                    'winning_model': result.get('winning_model', 'ENSEMBLE'),
                    'raw_log_data': json.dumps(log_dict, default=str, ensure_ascii=False)[:1000],  # Store first 1000 chars
                    'detected_at': datetime.utcnow().isoformat()
                }
                current_job_attacks.append(attack_detail)
            else:
                normal_traffic += 1

        total_records = len(df)
        attack_percentage = (attacks_detected / total_records * 100) if total_records > 0 else 0

        # Create Job Dict
        job_data = {
            'job_id': job_id,
            'filename': secure_filename(file.filename),
            'status': 'completed',
            'total_records': total_records,
            'attacks_detected': attacks_detected,
            'normal_traffic': normal_traffic,
            'attack_percentage': attack_percentage,
            'created_at': datetime.utcnow().isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        # Save to In-Memory Stores
        JOBS_STORE.append(job_data)
        if current_job_attacks:
            ATTACKS_STORE[job_id] = current_job_attacks

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Analysis completed using model: {dataset_name}',
            'results': {
                'total_records': total_records,
                'attacks_detected': attacks_detected,
                'normal_traffic': normal_traffic,
                'model_used': dataset_name
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/results/<job_id>', methods=['GET'])
def get_job_results(job_id):
    # Find job in list
    job = next((item for item in JOBS_STORE if item['job_id'] == job_id), None)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    # Get attacks from dict
    attacks = ATTACKS_STORE.get(job_id, [])
    
    # Pagination limit (optional, simple list for now)
    return jsonify({
        'job': job,
        'attacks': attacks
    })

# ==================== LIVE MONITORING (AGENT ARCHITECTURE) ====================

AGENTS_STORE = {} # Key: hostname, Value: {last_seen, ip, status}
LIVE_LOGS_BUFFER = [] # Circular buffer for last 100 logs
MAX_LIVE_LOGS = 100

@app.route('/api/ingest', methods=['POST'])
def ingest_log():
    """Receives logs from remote agents."""
    try:
        data = request.json
        log_line = data.get('log', '')
        source = data.get('source', 'unknown')
        timestamp = data.get('timestamp', time.time())
        
        # Update Agent Status
        AGENTS_STORE[source] = {
            'last_seen': datetime.utcnow().isoformat(),
            'ip': request.remote_addr,
            'status': 'online'
        }
        print(f"DEBUG INGEST: Updated Agent {source}. Store Size: {len(AGENTS_STORE)}")
        
        # Immediate Ensemble Analysis
        # We'll use a generic model (e.g., SAMET) since we don't know the exact type 
        # or we could try to detect it. For now, defaulting to SAMET for broad coverage.
        detector = EnsembleDetector("SAMET") 
        log_dict = {'detail': log_line, 'message': log_line} # detailed dict format
        
        result = detector.detect(log_dict)
        
        # Construct Log Record
        log_record = {
            'id': f"log_{int(time.time()*1000)}_{random.randint(1000,9999)}",
            'timestamp': datetime.utcnow().isoformat(),
            'source': source,
            'content': log_line,
            'analysis': {
                'decision': result['final_decision'],
                'confidence': float(result['confidence_score']),
                'votes': result['council_votes'],
                'winning_model': result.get('winning_model', 'ENSEMBLE'),
                'is_attack': bool(result.get('attack_detected', False))
            }
        }
        
        # Add to Buffer
        LIVE_LOGS_BUFFER.append(log_record)
        if len(LIVE_LOGS_BUFFER) > MAX_LIVE_LOGS:
            LIVE_LOGS_BUFFER.pop(0)
            
        # Also add to Stats if it's an attack (optional, to persist high severity events)
        if result.get('attack_detected', False):
            # We could add to ATTACKS_STORE if we want these to appear in reports too
            pass

        return jsonify({'status': 'success', 'analysis': result['final_decision']}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/agent', methods=['GET'])
def download_agent():
    """Serve the Linux agent simulation script."""
    script_path = "UNKNOWN"
    try:
        # Path relative to backend/app.py: ../real_agent_linux.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.abspath(os.path.join(current_dir, '..', 'real_agent_linux.py'))
        
        if not os.path.exists(script_path):
            return jsonify({'error': 'File not found on server', 'path_checked': script_path}), 404
            
        return send_file(script_path, as_attachment=True, download_name="agent.py")
    except Exception as e:
        return jsonify({'error': str(e), 'attempted_path': script_path}), 500

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all connected agents."""
    # Clean up old agents (timeout > 5 mins)
    now = datetime.utcnow()
    active_agents = []
    
    print(f"DEBUG AGENTS API: Checking Agents. Store Size: {len(AGENTS_STORE)}")
    for hostname, info in AGENTS_STORE.items():
        last_seen = datetime.fromisoformat(info['last_seen'])
        diff = (now - last_seen).total_seconds()
        print(f"DEBUG AGENTS API: Agent {hostname} seen {diff:.1f}s ago")
        if diff < 300: # 5 min timeout
            active_agents.append({
                'hostname': hostname,
                **info
            })
            
    return jsonify({'agents': active_agents})

@app.route('/api/monitor/stream', methods=['GET'])
def monitor_stream():
    """Server-Sent Events for Live Monitoring Page."""
    def generate():
        last_idx = len(LIVE_LOGS_BUFFER)
        
        while True:
            current_len = len(LIVE_LOGS_BUFFER)
            if current_len > last_idx:
                # Send new logs
                new_logs = LIVE_LOGS_BUFFER[last_idx:]
                yield f"data: {json.dumps({'type': 'logs', 'data': new_logs})}\n\n"
                last_idx = current_len
            
            # Send agent updates periodically (every 5 sec approx) or on change
            # For simplicity, send active agents count if needed, or frontend polls /api/agents
            
            time.sleep(1)
            
    return Response(generate(), mimetype='text/event-stream')

# ==================== SSH STREAMING (Legacy / Manual) ====================

@app.route('/api/ssh/connect', methods=['POST'])
def ssh_connect():
    # Pass-through to monitor
    data = request.get_json()
    monitor = get_monitor()
    if monitor.is_connected: monitor.disconnect()
    
    result = monitor.connect(
        host=data.get('host'), 
        username=data.get('username'), 
        password=data.get('password'), 
        port=data.get('port', 22)
    )
    return jsonify(result)

@app.route('/api/ssh/stream', methods=['GET'])
def ssh_stream():
    log_path = request.args.get('log_path', '/var/log/auth.log')
    
    def generate():
        monitor = get_monitor()
        if not monitor.is_connected:
            yield f"data: {json.dumps({'error': 'Not connected'})}\n\n"
            return
            
        # Initialize an Ensemble Detector for SSH logs (Using SAMET or similar generic)
        detector = EnsembleDetector("SAMET") 
        
        for log_entry in monitor.start_log_stream(log_path):
            raw_log = log_entry.get('raw', '')
            log_dict = {'detail': raw_log}
            
            try:
                result = detector.detect(log_dict)
                log_entry['ml_analysis'] = {
                    'decision': result['final_decision'],
                    'confidence': result['confidence_score'],
                    'votes': result['council_votes'],
                    'winning_model': result.get('winning_model', 'ENSEMBLE')
                }
                
                # If ML says attack, override severity
                if result.get('attack_detected', False):
                    log_entry['severity'] = 'CRITICAL'
                    log_entry['threat_type'] = 'ML_DETECTED_ATTACK'
                    
            except Exception as e:
                log_entry['ml_error'] = str(e)
            
            yield f"data: {json.dumps(log_entry)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("🚀 Starting In-Memory Backend on port 5050 (Accessible Externally)...")
    # Disable reloader to prevent duplicate processes/state issues
    app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=False)
