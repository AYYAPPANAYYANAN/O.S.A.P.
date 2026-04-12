from celery import Celery
import os
import requests
import time

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
ZAP_URL = os.environ.get("ZAP_URL", "http://zap_judge:8080")

app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

@app.task(bind=True, max_retries=3)
def execute_background_audit(self, url):
    try:
        # 1. Trigger ZAP Spider
        requests.get(f"{ZAP_URL}/JSON/spider/action/scan/?url={url}")
        time.sleep(2)
        
        # 2. Fetch Alerts
        res = requests.get(f"{ZAP_URL}/JSON/core/view/alerts/?baseurl={url}")
        alerts = res.json().get('alerts', [])
        
        total_reward = sum([100 for a in alerts if a['risk'] == 'High'])
        
        return {
            "status": "Vulnerable" if alerts else "Secure",
            "tech": alerts[0]['name'] if alerts else "Clean",
            "reward": total_reward if total_reward > 0 else -1,
            "explanation": f"Found {len(alerts)} vulnerabilities via ZAP API."
        }
    except Exception as e:
        return {"status": "Error", "tech": str(e), "reward": -10}