import asyncio
import json
import os
import subprocess
import time
import urllib.request
import websockets
import base64

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTPUT_DIR = "/Users/chiraglamba/Documents/antigravity/SkillBridge/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def send_cmd(ws, method, params=None, msg_id=1):
    msg = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data

async def evaluate(ws, expr, msg_id=100):
    return await send_cmd(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True}, msg_id)

async def capture_screen(ws, filename, msg_id=200):
    params = {"format": "png"}
    resp = await send_cmd(ws, "Page.captureScreenshot", params, msg_id)
    img_data = base64.b64decode(resp["result"]["data"])
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(img_data)
    print(f"Saved: {filename} ({len(img_data)} bytes)")

async def main():
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--user-data-dir=/tmp/chrome_test_profile_4",
        "--remote-debugging-port=9222",
        "--window-size=1400,1050",
        "--disable-gpu",
        "--no-sandbox"
    ])
    
    tabs = None
    for attempt in range(15):
        time.sleep(0.5)
        try:
            req = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2)
            tabs = json.loads(req.read().decode())
            break
        except Exception:
            pass
            
    if not tabs:
        print("Could not connect to Chrome debugging port!")
        chrome_proc.terminate()
        return

    try:
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        ws_url = page_tabs[0]["webSocketDebuggerUrl"]
        print(f"Connecting to: {ws_url}")
        
        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            await send_cmd(ws, "Page.enable", msg_id=1)
            await send_cmd(ws, "DOM.enable", msg_id=2)
            
            # Navigate to SkillBridge
            await send_cmd(ws, "Page.navigate", {"url": "http://127.0.0.1:8000/"}, msg_id=3)
            await asyncio.sleep(2.5)
            
            # 1. Main input screen
            await capture_screen(ws, "01_main_input_screen.png", msg_id=10)
            
            # 2. Click "Sample: ML Engineer"
            click_ml = """
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const b = btns.find(x => x.textContent.includes('Sample: ML Engineer'));
                if (b) { b.click(); return 'Clicked Sample: ML Engineer'; }
                return 'Not found';
            })()
            """
            await evaluate(ws, click_ml, msg_id=11)
            await asyncio.sleep(0.5)
            
            # 3. Click "Execute Skill Gap Audit"
            click_audit = """
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const b = btns.find(x => x.textContent.includes('Execute Skill Gap Audit'));
                if (b) { b.click(); return 'Clicked Execute Skill Gap Audit'; }
                return 'Not found';
            })()
            """
            await evaluate(ws, click_audit, msg_id=12)
            
            # Wait for backend API response and Vis.js stabilization
            await asyncio.sleep(4.5)
            
            # 4. Top Executive Summary & 3-Column Compatibility Matrix
            await capture_screen(ws, "02_executive_summary_matrix.png", msg_id=13)
            
            # Helper function to switch tabs and capture
            tabs_info = [
                ("network", "03_interactive_knowledge_graph.png"),
                ("categories", "04_category_breakdown.png"),
                ("radar", "05_career_readiness_radar.png"),
                ("roadmap", "06_12_week_study_roadmap.png"),
                ("peers", "07_gaussian_peer_percentile.png"),
                ("rewriter", "08_google_xyz_bullet_rewriter.png"),
                ("rubric", "09_ats_readability_rubric.png")
            ]
            
            for tab_id, filename in tabs_info:
                switch_tab_script = f"""
                (() => {{
                    const tabBtn = Array.from(document.querySelectorAll('nav button')).find(b => b.textContent.toLowerCase().includes('{tab_id}'));
                    if (tabBtn) {{ tabBtn.click(); return 'Clicked tab {tab_id}'; }}
                    return 'Tab {tab_id} not found';
                }})()
                """
                await evaluate(ws, switch_tab_script, msg_id=30)
                await asyncio.sleep(1.0)
                
                # Scroll tab into view
                scroll_script = """
                (() => {
                    const nav = document.querySelector('nav');
                    if (nav) { nav.scrollIntoView({ behavior: 'instant', block: 'start' }); }
                })()
                """
                await evaluate(ws, scroll_script, msg_id=31)
                await asyncio.sleep(0.8)
                await capture_screen(ws, filename, msg_id=32)

    finally:
        chrome_proc.terminate()
        chrome_proc.wait()
        print("Chrome finished.")

if __name__ == "__main__":
    asyncio.run(main())
