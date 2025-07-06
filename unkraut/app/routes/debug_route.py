# app/routes/debug_routes.py
"""
Debug-Routes für Mobile und Netzwerk-Probleme
"""
from flask import Blueprint, render_template, jsonify, request
import socket
import platform
import psutil
import os

bp = Blueprint('debug', __name__)

@bp.route('/debug')
def debug_info():
    """Debug-Informationen anzeigen"""
    return render_template('debug.html')

@bp.route('/api/debug/network')
def debug_network():
    """Netzwerk-Debug-Informationen"""
    try:
        # Server-IP-Adressen ermitteln
        hostname = socket.gethostname()
        ip_addresses = []
        
        # Alle Netzwerk-Interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_addresses.append({
                        'interface': interface,
                        'ip': addr.address,
                        'netmask': addr.netmask
                    })
        
        # Client-Informationen
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Server-Informationen
        server_info = {
            'hostname': hostname,
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'server_port': request.environ.get('SERVER_PORT'),
            'server_name': request.environ.get('SERVER_NAME')
        }
        
        return jsonify({
            'server': server_info,
            'ip_addresses': ip_addresses,
            'client': {
                'ip': client_ip,
                'user_agent': user_agent,
                'host': request.host,
                'url': request.url,
                'method': request.method
            },
            'headers': dict(request.headers)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/debug/routes')
def debug_routes():
    """Alle verfügbaren Routes anzeigen"""
    try:
        from flask import current_app
        
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        return jsonify({'routes': routes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500