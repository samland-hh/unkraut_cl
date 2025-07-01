.PHONY: install run test clean

install:
	pip install -r requirements.txt
	@echo "✅ Installation abgeschlossen"

run:
	python run.py

test:
	@echo "🧪 Teste Hardware-Module..."
	@python -c "from hardware.motors import motor_controller; print('✅ Motors:', motor_controller.get_status())"
	@python -c "from hardware.sensors import get_sensor_data; print('✅ Sensors verfügbar')"
	@python -c "from ai.weed_detection import weed_detector; print('✅ AI geladen')"
	@echo "🧪 Teste Flask App..."
	@python -c "from app.main import app; print('✅ Flask App funktioniert')"

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf logs/*.log data/images/* 2>/dev/null || true

status:
	@curl -s http://localhost:5000/api/system/status | python -m json.tool 2>/dev/null || echo "❌ Server nicht erreichbar"
