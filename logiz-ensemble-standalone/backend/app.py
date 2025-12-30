from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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

# ssh_monitor removed - using agent-based monitoring

# ==================== MODEL CACHE (Performance) ====================
# Load models once at startup instead of per-request
MODEL_CACHE = {}

def get_detector(dataset_type="SAMET"):
    """Get or create a cached EnsembleDetector instance."""
    if dataset_type not in MODEL_CACHE:
        print(f"📦 Loading model for {dataset_type} (first time)...")
        MODEL_CACHE[dataset_type] = EnsembleDetector(dataset_type)
        print(f"✅ Model {dataset_type} cached successfully.")
    return MODEL_CACHE[dataset_type]

# Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# ==================== IN-MEMORY STORAGE ====================
# Data persists only while the application is running
JOBS_STORE = [] 
ATTACKS_STORE = {} # Key: job_id, Value: list of attack dicts

# ==================== SECURITY CONFIG ====================
# API Keys for agent authentication (Key -> Agent Name)
API_KEYS = {
    "anomi-agent-key-001": "DefaultAgent",
    "anomi-test-key-999": "TestAgent",
    # Add more keys as needed
}

# Rate Limiting (Simple in-memory implementation)
RATE_LIMIT_STORE = {}  # IP -> {count, reset_time}
RATE_LIMIT_MAX = 1000   # Max requests per window (increased for high-frequency logging)
RATE_LIMIT_WINDOW = 60 # Window in seconds

def check_rate_limit(ip_address):
    """Returns True if request is allowed, False if rate limited."""
    now = time.time()
    
    if ip_address not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[ip_address] = {'count': 1, 'reset_time': now + RATE_LIMIT_WINDOW}
        return True
    
    entry = RATE_LIMIT_STORE[ip_address]
    
    # Reset window if expired
    if now > entry['reset_time']:
        RATE_LIMIT_STORE[ip_address] = {'count': 1, 'reset_time': now + RATE_LIMIT_WINDOW}
        return True
    
    # Check limit
    if entry['count'] >= RATE_LIMIT_MAX:
        return False
    
    entry['count'] += 1
    return True

def validate_api_key(request):
    """Validates API key from request headers. Returns agent name or None."""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return None
    return API_KEYS.get(api_key)

def validate_ingest_payload(data):
    """Validates the ingest payload. Returns (is_valid, error_message)."""
    if not data:
        return False, "Empty payload"
    if 'log' not in data:
        return False, "Missing 'log' field"
    if not isinstance(data.get('log'), str):
        return False, "'log' must be a string"
    if len(data.get('log', '')) > 10000:
        return False, "'log' exceeds max length (10000 chars)"
    return True, None

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def index():
    return """
    <h1>🚀 Anomi-Ensemble Integrated Backend (In-Memory)</h1>
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
        'recent_alerts': recent_alerts,
        'traffic_trend': calculate_traffic_trend()
    })

def calculate_traffic_trend():
    """Calculates hourly traffic trend based on Job submission times."""
    try:
        now = datetime.utcnow()
        # Initialize last 12 buckets (Reverse order: Now -> Past)
        trend_map = {}
        time_labels = []
        
        for i in range(11, -1, -1):
            dt = now - pd.Timedelta(hours=i)
            label = f"{dt.hour:02d}:00"
            trend_map[label] = {'normal': 0, 'attack': 0}
            time_labels.append(label)
            
        # Aggregate Job Data
        for job in JOBS_STORE:
            try:
                # Use job creation time as the "event time" for the bulk upload
                job_time = datetime.fromisoformat(job['created_at'])
                # Only if within last 24h (approx)
                if (now - job_time).total_seconds() < 43200: # 12 hours
                    label = f"{job_time.hour:02d}:00"
                    if label in trend_map:
                        trend_map[label]['normal'] += job.get('normal_traffic', 0)
                        trend_map[label]['attack'] += job.get('attacks_detected', 0)
            except Exception as e:
                print(f"Error parsing job time: {e}")
                continue
                
        # Aggregate Live Logs (Real-time updates)
        for log in LIVE_LOGS_BUFFER:
            try:
                log_time = datetime.fromisoformat(log['timestamp'])
                if (now - log_time).total_seconds() < 43200:
                   label = f"{log_time.hour:02d}:00"
                   if label in trend_map:
                       if log.get('analysis', {}).get('is_attack', False):
                           trend_map[label]['attack'] += 1
                       else:
                           trend_map[label]['normal'] += 1
            except: pass

        # Format for Frontend: [{time, normal, attack}, ...]
        result = []
        for label in time_labels:
            result.append({
                'time': label,
                'normal': trend_map[label]['normal'],
                'attack': trend_map[label]['attack']
            })
            
        return result
    except Exception as e:
        print(f"Error calculating trend: {e}")
        return []

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
    
    # Fallback: Check by columns (unique identifiers first)
    if 'ocp_namespace' in cols or 'ocp_pod' in cols: return 'EMİRHAN'  # OpenShift/K8s logs
    if 'price_eur_kwh' in cols: return 'SUZAN'
    if 'protocol_can' in cols: return 'İREM'
    if 'load_kw' in cols: return 'ATAKAN'
    if 'input_plate' in cols: return 'MİRAÇ'
    if 'Tuketim_kWh' in cols: return 'EMİRHNT'
    if 'action' in cols and 'status' in cols and 'message' not in cols: return 'ALİ'
    if 'message' in cols and 'severity' in cols: return 'EMİRHAN'  # Alternative check
    if 'detail' in cols and 'id' in cols: return 'SAMET'  # IDS logs with hex IDs
    if 'detail' in cols: return 'İBRAHİM'  # CSMS logs
    
    return 'YOUSEF' # Default fallback only if nothing else matches

@app.route('/api/analyze/upload', methods=['POST'])
def upload_and_analyze():
    file = None
    if 'file' in request.files:
        file = request.files['file']
    
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        # Load Data - Handle TXT files specially
        filename_lower = file.filename.lower()
        
        if filename_lower.endswith('.txt'):
            # TXT files: Each line is a log entry
            content = file.read().decode('utf-8', errors='replace')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Smart Parsing for Comma Separated TXT (User Request: Show Attributes)
            if lines and ',' in lines[0]:
                print("📄 Smart Parsing: Detected CSV-like structure in TXT")
                data_list = []
                for line in lines:
                    parts = [p.strip() for p in line.split(',')]
                    # Auto-assign headers based on content heuristics
                    row = {'message': line} # Keep full message
                    for i, part in enumerate(parts):
                        header = f"Attribute_{i+1}"
                        # Simple heuristics for headers
                        if i == 0 and (':' in part or '-' in part): header = "Zaman Damgası"
                        elif part in ['NORMAL', 'SALDIRI', 'ATTACK']: header = "Etiket/Durum"
                        elif part in ['INFO', 'WARN', 'ERROR', 'CRITICAL']: header = "Seviye"
                        elif '0x' in part: header = "Hata Kodu"
                        elif part in ['OK', 'FAIL']: header = "İşlem Sonucu"
                            
                        # Avoid duplicates
                        if header in row: header = f"{header}_{i}"
                        row[header] = part
                    data_list.append(row)
                df = pd.DataFrame(data_list)
            else:
                df = pd.DataFrame({'message': lines, 'detail': lines})
                
            print(f"📄 Loaded TXT file with {len(lines)} lines")
        else:
            # CSV files: Standard parsing
            try:
                df = pd.read_csv(file, on_bad_lines='skip', encoding='utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, on_bad_lines='skip', encoding='latin-1')
        
        # Determine which Ensemble Model to use
        dataset_name = determine_dataset_type(df, file.filename)
        print(f"🔍 Analyzing as dataset: {dataset_name}")
        
        # Use cached detector for this dataset type
        detector = get_detector(dataset_name)
        
        attacks_detected = 0
        normal_traffic = 0
        current_job_attacks = []
        job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Collect detailed results for quick analysis (first 100 max)
        detailed_logs = []
        
        # Analyze logs in batch (Vectorized - Fast)
        logs_list = df.to_dict(orient='records')
        batch_results = detector.detect_batch(logs_list)
        
        # Process Results
        for idx, result in enumerate(batch_results):
            # Use the boolean flag from Ensemble voting logic
            is_attack = result.get('attack_detected', False)
            
            # Add to detailed logs list
            if idx < 100:
                detailed_logs.append({
                    'index': idx,
                    'decision': result['final_decision'],
                    'confidence': float(result['confidence_score']),
                    'attack_detected': is_attack,
                    'winning_model': result.get('winning_model', 'ENSEMBLE'),
                    'reason': result.get('reason', 'Analiz Detayı Mevcut Değil'), # Add Reason
                    'raw_data': {k: str(v) for k, v in logs_list[idx].items()} # Safe string conversion
                })
            
            if is_attack:
                attacks_detected += 1
                # Save details with enhanced documentation
                # Note: 'raw_log_data' needs to be retrieved from original log
                original_log = logs_list[idx]
                
                attack_detail = {
                    'id': idx + 1,
                    'record_index': idx,
                    'probability': float(result['confidence_score']),
                    'attack_type': result['final_decision'],
                    'dataset_source': dataset_name,
                    'council_votes': " | ".join(result['council_votes']),
                    'winning_model': result.get('winning_model', 'ENSEMBLE'),
                    'raw_log_data': json.dumps(original_log, default=str, ensure_ascii=False)[:1000],  # Store first 1000 chars
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
                'model_used': dataset_name,
                'detailed_logs': detailed_logs
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
    
    # Limit to first 100 attacks for performance
    limited_attacks = attacks[:100]
    
    return jsonify({
        'job': job,
        'attacks': limited_attacks,
        'total_attacks_count': len(attacks),
        'showing': len(limited_attacks)
    })

# ==================== LIVE MONITORING (AGENT ARCHITECTURE) ====================

AGENTS_STORE = {} # Key: hostname, Value: {last_seen, ip, status}
LIVE_LOGS_BUFFER = [] # Circular buffer for last 100 logs
MAX_LIVE_LOGS = 100

@app.route('/api/ingest', methods=['POST'])
def ingest_log():
    """Receives logs from remote agents with security checks."""
    try:
        # === SECURITY LAYER ===
        
        # 1. Rate Limiting
        client_ip = request.remote_addr
        if not check_rate_limit(client_ip):
            return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
        
        # 2. API Key Authentication (Optional - can be disabled for testing)
        # Uncomment the following to enforce API keys:
        # agent_name = validate_api_key(request)
        # if not agent_name:
        #     return jsonify({'error': 'Invalid or missing API key'}), 401
        
        # 3. Input Validation
        data = request.json
        is_valid, error_msg = validate_ingest_payload(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # === END SECURITY LAYER ===
        
        log_line = data.get('log', '')
        source = data.get('source', 'unknown')
        timestamp = data.get('timestamp', time.time())
        
        # Update Agent Status
        AGENTS_STORE[source] = {
            'last_seen': datetime.utcnow().isoformat(),
            'ip': client_ip,
            'status': 'online'
        }
        print(f"DEBUG INGEST: Updated Agent {source}. Store Size: {len(AGENTS_STORE)}")
        
        # Immediate Ensemble Analysis (Using Cached Model)
        detector = get_detector("SAMET")  # Uses cached model
        log_dict = {'detail': log_line, 'message': log_line}
        
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
            
        # Track and Alert on Attacks
        if result.get('attack_detected', False):
            attack_detail = {
                'id': log_record['id'],
                'timestamp': log_record['timestamp'],
                'source': source,
                'attack_type': result['final_decision'],
                'confidence': float(result['confidence_score']),
                'winning_model': result.get('winning_model', 'ENSEMBLE'),
                'log_preview': log_line[:200],
                'detected_at': datetime.utcnow().isoformat()
            }
            
            # Store in live attacks
            if 'live_monitor' not in ATTACKS_STORE:
                ATTACKS_STORE['live_monitor'] = []
            ATTACKS_STORE['live_monitor'].append(attack_detail)
            
            # Keep only last 100 live attacks
            if len(ATTACKS_STORE['live_monitor']) > 100:
                ATTACKS_STORE['live_monitor'] = ATTACKS_STORE['live_monitor'][-100:]
            
            # Console Alert
            print(f"🚨 ATTACK DETECTED! Source: {source} | Type: {result['final_decision']} | Confidence: {result['confidence_score']:.2f}")

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
            
    return Response(
        generate(), 
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'X-Accel-Buffering': 'no'
        }
    )

# ==================== EXPORT ENDPOINTS ====================

@app.route('/api/export/attacks', methods=['GET'])
def export_attacks_csv():
    """Export all detected attacks as CSV."""
    import io
    import csv
    
    # Collect all attacks from all jobs + live monitor
    all_attacks = []
    
    # From file uploads
    for job_id, attacks in ATTACKS_STORE.items():
        for attack in attacks:
            attack_copy = attack.copy()
            attack_copy['source_job'] = job_id
            all_attacks.append(attack_copy)
    
    if not all_attacks:
        return jsonify({'error': 'No attacks to export'}), 404
    
    # Create CSV in memory
    output = io.StringIO()
    
    # Get all unique keys for headers
    all_keys = set()
    for attack in all_attacks:
        all_keys.update(attack.keys())
    fieldnames = sorted(list(all_keys))
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for attack in all_attacks:
        writer.writerow(attack)
    
    # Return as downloadable file
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attacks_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'}
    )

@app.route('/api/export/logs', methods=['GET'])
def export_logs_csv():
    """Export live logs buffer as CSV."""
    import io
    import csv
    
    if not LIVE_LOGS_BUFFER:
        return jsonify({'error': 'No logs to export'}), 404
    
    output = io.StringIO()
    
    # Flatten the log records for CSV
    flattened_logs = []
    for log in LIVE_LOGS_BUFFER:
        flat = {
            'id': log['id'],
            'timestamp': log['timestamp'],
            'source': log['source'],
            'content': log['content'],
            'decision': log['analysis']['decision'],
            'confidence': log['analysis']['confidence'],
            'is_attack': log['analysis']['is_attack'],
            'winning_model': log['analysis']['winning_model']
        }
        flattened_logs.append(flat)
    
    fieldnames = ['id', 'timestamp', 'source', 'content', 'decision', 'confidence', 'is_attack', 'winning_model']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(flattened_logs)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=logs_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'}
    )

# ==================== SSH STREAMING (REMOVED) ====================
# SSH-based streaming has been replaced by Agent-based architecture.
# Use /api/ingest and /api/monitor/stream instead.
# Endpoints removed: /api/ssh/connect, /api/ssh/stream

if __name__ == '__main__':
    print("🚀 Starting In-Memory Backend on port 5050 (Accessible Externally)...")
    # Disable reloader to prevent duplicate processes/state issues
    app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=False)
