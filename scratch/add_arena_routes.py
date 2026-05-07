import sys

file_path = "/Users/asilbek/Desktop/AI-Projects/quiz-js/routes/arena.py"

with open(file_path, 'r') as f:
    content = f.read()

new_routes = """
@arena_bp.route('/report_violation', methods=['POST'])
@arena_required
def report_violation():
    \"\"\"Qoidabuzarlikni qayd etish (Arena).\"\"\"
    data = request.get_json(silent=True) or {}
    violation_type = data.get('type', 'Unknown')
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).timestamp()
    existing_end = session.get('arena_violation_end_time', 0)
    if existing_end > now:
        violation_end_time = existing_end + 5 
    else:
        violation_end_time = now + 15
    session['arena_violation_end_time'] = violation_end_time
    session.permanent = True
    return jsonify({
        'success': True,
        'violation_end_time': violation_end_time
    })

@arena_bp.route('/clear_violation', methods=['POST'])
@arena_required
def clear_violation():
    \"\"\"Jazoni tugatish (Arena).\"\"\"
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).timestamp()
    end_time = session.get('arena_violation_end_time', 0)
    if now >= end_time:
        session.pop('arena_violation_end_time', None)
        return jsonify({'success': True})
    return jsonify({'success': False, 'time_left': end_time - now})
"""

# Insert before @arena_bp.route('/problems/<int:pid>/submit'
marker = "@arena_bp.route('/problems/<int:pid>/submit'"
if marker in content:
    content = content.replace(marker, new_routes + "\n\n" + marker)
    with open(file_path, 'w') as f:
        f.write(content)
    print("Routes added successfully.")
else:
    print("Marker not found.")
