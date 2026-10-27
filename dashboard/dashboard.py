"""AI City Traffic Command Centre — local hackathon prototype.
City-wide values are explicitly simulated; video analysis calls the existing S14.13 controller.
"""
from __future__ import annotations
import json, random, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEO_PATH = ROOT / "data" / "videos" / "traffic.mp4"
LOCK = threading.RLock()

NAMES = ["J1 · Central", "J2 · Market", "J3 · Station", "J4 · Hospital", "J5 · Tech Park", "J6 · Ring Road", "J7 · School", "J8 · Bridge", "J9 · City Exit"]
EDGES = [(0,1),(1,2),(0,3),(1,4),(2,5),(3,4),(4,5),(3,6),(4,7),(5,8),(6,7),(7,8)]
random.seed(23)
JUNCTIONS = []
for i, name in enumerate(NAMES):
    count = random.randint(8, 42)
    JUNCTIONS.append({"id": i+1, "name": name, "vehicles": count, "two_wheelers": int(count*.55), "buses": max(0,int(count*.025)), "heavy": max(1,int(count*.08)), "pedestrians": random.randint(0,18), "queue": random.randint(3,22), "wait": random.randint(12,85), "density": min(100, int(count*2.2)), "phase": "GREEN" if i % 3 == 0 else "RED", "green": random.randint(25,65), "critical_direction": "NORTH_SOUTH", "throughput": random.randint(250,900), "efficiency": random.randint(55,95), "fuel_waste_l_hr": round(random.uniform(1.0,7.5),1), "incident": None})
for _junction in JUNCTIONS:
    _junction["queue_base"] = _junction["queue"]

STATE = {"city":"Bengaluru · Demo Network", "mode":"SIMULATED CITY DATA", "weather":"Clear", "junctions":JUNCTIONS, "incidents":[], "events":[], "ambulance":None, "coordination_active":False, "green_wave":[1,2,3,6,9], "video": {"status":"Not run yet", "result":None}, "camera_screening": {"status":"Waiting for video analysis", "candidate_events":[], "series":[]}, "forecast":[], "analytics":[], "fuel_analytics":[], "performance_history":[], "optimization_summary":None, "forecast_summary":None, "density_history":[], "last_update":time.time()}

def event(msg):
    STATE["events"].insert(0, {"time":time.strftime("%H:%M:%S"), "message":msg})
    STATE["events"][:] = STATE["events"][:30]

def totals():
    js=STATE["junctions"]
    congested=sum(1 for j in js if j["density"]>=65)
    return {"junctions":len(js),"congested":congested,"vehicles":sum(j["vehicles"] for j in js),"avg_wait":round(sum(j["wait"] for j in js)/len(js)),"incidents":len(STATE["incidents"]),"fuel_l_day":round(sum(j["vehicles"]*j["wait"] for j in js)*0.018),"throughput":sum(j["throughput"] for j in js),"avg_efficiency":round(sum(j["efficiency"] for j in js)/len(js)),"fuel_waste_l_hr":round(sum(j["fuel_waste_l_hr"] for j in js),1)}

def analyze_performance():
    """Rank demo junctions using the current simulated metrics; recommendations are estimates."""
    js = STATE["junctions"]
    avg_wait = sum(j["wait"] for j in js) / max(1, len(js))
    avg_queue = sum(j["queue"] for j in js) / max(1, len(js))
    ranked = []
    for j in js:
        wait_gap = j["wait"] - avg_wait
        queue_gap = j["queue"] - avg_queue
        score = (j["wait"] / 180 * 40) + (j["queue"] / 40 * 35) + ((100-j["efficiency"]) * 0.25)
        if wait_gap > 5 and queue_gap > 2:
            delta = max(3, min(12, round(wait_gap * 0.12 + queue_gap * 0.22)))
            recommendation = f"Test +{delta}s green on {j['critical_direction'].replace('_', ' ')}; re-measure wait and queue"
            action = f"+{delta}s"
        elif wait_gap < -5 and j["efficiency"] >= 75:
            recommendation = "Hold current timing; compare throughput before changing"
            action = "HOLD"
        else:
            recommendation = "Monitor queue trend; avoid a timing change without another sample"
            action = "MONITOR"
        ranked.append({"id":j["id"], "name":j["name"], "wait":j["wait"], "queue":j["queue"], "efficiency":j["efficiency"], "fuel_waste_l_hr":j["fuel_waste_l_hr"], "score":round(score,1), "action":action, "recommendation":recommendation})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    STATE["analytics"] = ranked[:5]
    return STATE["analytics"]

def analyze_fuel_hotspots():
    """Rank simulated fuel-waste hotspots; all outputs are estimates, not measured fuel use."""
    ranked = []
    for j in STATE["junctions"]:
        hourly = max(0.0, float(j.get("fuel_waste_l_hr", 0)))
        daily = hourly * 8  # explicit demo assumption: 8 operating hours per day
        ranked.append({
            "id": j["id"], "name": j["name"], "vehicles": j["vehicles"],
            "queue": j["queue"], "wait": j["wait"],
            "fuel_l_hr": round(hourly, 2), "fuel_l_day": round(daily, 2),
            "potential_saving_l_day": round(daily * 0.10, 2),
            "action": "Review queue + signal split" if j["queue"] >= 15 or j["wait"] >= 55 else "Monitor trend"
        })
    ranked.sort(key=lambda x: x["fuel_l_hr"], reverse=True)
    STATE["fuel_analytics"] = ranked[:5]
    total_hourly = sum(x["fuel_l_hr"] for x in ranked)
    return {"top_hotspots": STATE["fuel_analytics"], "estimated_city_l_hr": round(total_hourly, 2),
            "estimated_city_l_day": round(total_hourly * 8, 2),
            "illustrative_10pct_saving_l_day": round(total_hourly * 8 * 0.10, 2),
            "assumption": "8 operating hours/day; 10% scenario saving is illustrative, not measured."}

def capture_performance_sample(source="periodic"):
    """Keep bounded in-memory demo snapshots for trend comparisons during this run."""
    js = STATE["junctions"]
    sample = {"time": time.strftime("%H:%M:%S"), "epoch": time.time(),
              "avg_wait": round(sum(j["wait"] for j in js) / max(1, len(js)), 1),
              "avg_queue": round(sum(j["queue"] for j in js) / max(1, len(js)), 1),
              "avg_density": round(sum(j["density"] for j in js) / max(1, len(js)), 1),
              "throughput": sum(j["throughput"] for j in js),
              "efficiency": round(sum(j["efficiency"] for j in js) / max(1, len(js)), 1),
              "fuel_l_hr": round(sum(j.get("fuel_waste_l_hr", 0) for j in js), 1),
              "source": source}
    hist = STATE.setdefault("performance_history", [])
    if not hist or time.time() - hist[-1].get("epoch", 0) >= 8 or source != "periodic":
        hist.append(sample)
        del hist[:-60]
    dh = STATE.setdefault("density_history", [])
    if not dh or time.time() - dh[-1].get("epoch", 0) >= 8:
        dh.append({"epoch": sample["epoch"], "density": sample["avg_density"]})
        del dh[:-60]
    return sample

def build_density_forecast():
    """Trend-extrapolation baseline; explicitly not a trained prediction model."""
    hist = STATE.get("density_history", [])
    current = round(sum(j["density"] for j in STATE["junctions"]) / max(1, len(STATE["junctions"])), 1)
    if len(hist) >= 2:
        elapsed = max(1.0, hist[-1]["epoch"] - hist[0]["epoch"])
        slope_per_min = (hist[-1]["density"] - hist[0]["density"]) / (elapsed / 60.0)
        # Dampen noisy short-run changes; never project beyond plausible density bounds.
        slope_per_min = max(-1.5, min(1.5, slope_per_min * 0.35))
        basis = "recent simulated density trend (damped linear baseline)"
    else:
        slope_per_min = 0.0
        basis = "current simulated density; trend warm-up needs more samples"
    points = []
    for minute in (5, 10, 15, 20, 25, 30):
        projected = max(0, min(100, round(current + slope_per_min * minute, 1)))
        points.append({"minute": minute, "density": projected})
    STATE["forecast_summary"] = {"basis": basis, "current_density": current,
                                  "trend_per_min": round(slope_per_min, 3),
                                  "horizon_minutes": 30,
                                  "caveat": "Prototype trend baseline, not a trained/validated real-world prediction model."}
    return points

def run_closed_loop_optimization():
    """Simulated Detect→Analyze→Decide→Act→Measure cycle with explicit before/after estimates."""
    before = capture_performance_sample("before optimization")
    changes = []
    for j in STATE["junctions"]:
        old_wait, old_queue, old_green = j["wait"], j["queue"], j["green"]
        # Allocate modest extra green only to high-pressure nodes; cap the intervention.
        pressure = (j["density"] * .45) + (j["queue"] / 40 * 35) + (j["wait"] / 180 * 20)
        delta = 5 if pressure >= 55 else (2 if pressure >= 38 else 0)
        j["green"] = max(20, min(90, old_green + delta))
        # Transparent demo response assumptions, not an empirical traffic simulator.
        if delta:
            j["queue"] = max(0, j["queue"] - (2 if delta >= 5 else 1))
            j["wait"] = max(5, j["wait"] - (4 if delta >= 5 else 2))
            j["density"] = max(0, j["density"] - (2 if delta >= 5 else 1))
            j["throughput"] = round(j["throughput"] * (1.04 if delta >= 5 else 1.02))
            j["efficiency"] = min(99, j["efficiency"] + (3 if delta >= 5 else 1))
            j["fuel_waste_l_hr"] = round(max(0, j["fuel_waste_l_hr"] * (0.94 if delta >= 5 else 0.98)), 1)
        changes.append({"id":j["id"], "green_before":old_green, "green_after":j["green"], "delta":j["green"]-old_green,
                        "queue_before":old_queue, "queue_after":j["queue"], "wait_before":old_wait, "wait_after":j["wait"]})
    after = capture_performance_sample("after optimization")
    def pct(a, b): return round((a-b)/a*100, 1) if a else 0.0
    STATE["optimization_summary"] = {
        "before": before, "after": after, "wait_reduction_pct": pct(before["avg_wait"], after["avg_wait"]),
        "queue_reduction_pct": pct(before["avg_queue"], after["avg_queue"]),
        "fuel_estimate_reduction_pct": pct(before["fuel_l_hr"], after["fuel_l_hr"]),
        "throughput_change_pct": round((after["throughput"]-before["throughput"])/before["throughput"]*100,1) if before["throughput"] else 0,
        "junctions_adjusted": sum(1 for x in changes if x["delta"]), "changes": changes,
        "note": "Before/after values are simulated model outputs, not field-measured outcomes. Repeat samples are needed for validation."}
    event("Closed-loop demo cycle completed: detect → analyze → decide → act → measure; before/after metrics are simulated")
    return STATE["optimization_summary"]

def snapshot():
    with LOCK:
        # Simulated sensor feed. All city-wide values remain clearly labelled as demo data.
        now = time.time()
        for j in STATE["junctions"]:
            previous_vehicles=j["vehicles"]
            delta=random.randint(-8,4)
            j["vehicles"]=max(0,min(65,j["vehicles"]+delta))
            # Lightweight anomaly rule over the simulated feed; this is not camera-based incident recognition.
            if previous_vehicles-j["vehicles"]>=6 and j["queue"]>=18 and not any(x.get("source")=="SIMULATED_AI_RULE" and x.get("junction")==j["id"] and x.get("status")=="OPEN" for x in STATE["incidents"]):
                alert={"id":int(now*1000)%1000000,"type":"Possible sudden traffic drop (simulated anomaly)","junction":j["id"],"time":time.strftime("%H:%M:%S"),"status":"OPEN","source":"SIMULATED_AI_RULE"}
                STATE["incidents"].insert(0,alert); STATE["incidents"][:]=STATE["incidents"][:20]
                event(f"Simulated anomaly alert at J{j['id']}: vehicle count dropped while queue remained high")
            j["queue_base"]=max(0,min(40,j.get("queue_base",j["queue"])+random.randint(-2,3)))
            j["queue"]=j["queue_base"]
            j["two_wheelers"]=int(j["vehicles"]*.55)
            j["buses"]=max(0,int(j["vehicles"]*.025))
            j["heavy"]=max(0,int(j["vehicles"]*.08))
            j["pedestrians"]=max(0,min(35,j.get("pedestrians",5)+random.randint(-2,3)))
            # Multi-factor adaptive timing: density, queue, waiting time and vulnerable road users.
            j["density"]=max(0,min(100,int(j["vehicles"]*1.25+j["queue"]*1.15)))
            j["wait"]=max(5,min(180,int(j["queue"]*2.1+j["density"]*.42)))
            score=.42*j["density"] + .34*(j["queue"]/40*100) + .18*(j["wait"]/180*100) + .06*min(100,j["pedestrians"]*3)
            j["green"]=max(20,min(90,round(20+score*.70)))
            j["critical_direction"]="NORTH_SOUTH" if (j["queue"]+j["vehicles"]*.35) >= (j["vehicles"]*.65) else "EAST_WEST"
            # Explicitly illustrative model outputs, not measurements from municipal sensors.
            j["throughput"]=max(60,round(j["vehicles"]*60*(1-j["density"]/160)))
            j["efficiency"]=max(10,min(99,round(100-j["wait"]*.32-j["queue"]*.35)))
            j["fuel_waste_l_hr"]=round(max(0,j["queue"]*.12+j["wait"]*.025),1)
        # Weather/road impact is an explicit, repeatable demo model, not a live forecast.
        impacts = {
            "Clear": {"capacity_loss_pct": 0, "queue_factor": 1.00, "wait_add": 0, "note": "Normal demo road capacity"},
            "Light rain": {"capacity_loss_pct": 5, "queue_factor": 1.05, "wait_add": 3, "note": "Reduced traction; modest speed reduction"},
            "Heavy rain": {"capacity_loss_pct": 15, "queue_factor": 1.15, "wait_add": 8, "note": "Lower speeds and longer queues expected"},
            "Waterlogging risk": {"capacity_loss_pct": 30, "queue_factor": 1.30, "wait_add": 15, "note": "High-delay scenario; consider diversion review"},
            "Road works": {"capacity_loss_pct": 20, "queue_factor": 1.20, "wait_add": 10, "note": "Lane capacity reduced by work zone"},
            "Dense fog": {"capacity_loss_pct": 25, "queue_factor": 1.18, "wait_add": 12, "note": "Lower visibility; cautious speed assumptions"},
            "Road closure": {"capacity_loss_pct": 45, "queue_factor": 1.45, "wait_add": 20, "note": "Severe capacity restriction; operator should review rerouting"},
        }
        impact = impacts.get(STATE["weather"], impacts["Clear"])
        for j in STATE["junctions"]:
            j["queue"] = min(40, round(j["queue"] * impact["queue_factor"]))
            j["density"] = min(100, j["density"] + round(impact["capacity_loss_pct"] * 0.35))
            j["wait"] = min(180, j["wait"] + impact["wait_add"])
            if impact["capacity_loss_pct"]:
                j["green"] = max(20, min(90, j["green"] + round(impact["capacity_loss_pct"] / 10)))
            j["throughput"] = max(0, round(j["throughput"] * (1 - impact["capacity_loss_pct"] / 100)))
            j["fuel_waste_l_hr"] = round(j["fuel_waste_l_hr"] * (1 + impact["capacity_loss_pct"] / 100), 1)
        STATE["weather_impact"] = {"condition": STATE["weather"], "estimated_capacity_loss_pct": impact["capacity_loss_pct"], "estimated_capacity_remaining_pct": 100-impact["capacity_loss_pct"], "note": impact["note"]}
        # Reported incidents affect the simulated capacity/queue of their junction.
        for inc in STATE["incidents"]:
            if inc.get("status")=="OPEN":
                target=next((x for x in STATE["junctions"] if x["id"]==inc["junction"]),None)
                if target:
                    target["density"]=min(100,target["density"]+12); target["wait"]=min(180,target["wait"]+10)
        # Coordinate the network: prioritize a sequence of connected junctions as a green wave.
        if STATE.get("coordination_active"):
            wave=STATE.get("green_wave",[1,2,3,6,9])
            phase_index=int(now/5)%len(wave)
            for idx,jid in enumerate(wave):
                j=STATE["junctions"][jid-1]
                j["phase"]="GREEN" if idx==phase_index else ("YELLOW" if idx==(phase_index+1)%len(wave) else "RED")
        # Emergency corridor progresses automatically and normal control resumes at destination.
        amb=STATE.get("ambulance")
        if amb and now-amb.get("last_step_at",now)>=6:
            amb["step"]+=1; amb["last_step_at"]=now
            if amb["step"]>=len(amb["route"]):
                completed=amb["route"][-1]
                STATE["ambulance"]=None
                event(f"Ambulance reached J{completed}; normal adaptive signal control resumed")
                amb=None
            else:
                amb["current"]=amb["route"][amb["step"]]
                event(f"Ambulance corridor advanced to J{amb['current']}")
        if amb:
            route=amb.get("route",[]); current=amb.get("current")
            for j in STATE["junctions"]:
                if j["id"]==current: j["phase"]="GREEN"
                elif j["id"] in route and j["id"]==route[amb.get("step",0)+1 if amb.get("step",0)+1<len(route) else 0]: j["phase"]="YELLOW"
                elif j["id"] in route: j["phase"]="RED"
                else: j["phase"]="GREEN" if (int(now/8)+j["id"])%3==0 else ("YELLOW" if (int(now/8)+j["id"])%3==1 else "RED")
        elif not STATE.get("coordination_active"):
            for j in STATE["junctions"]:
                j["phase"]="GREEN" if (int(now/8)+j["id"])%3==0 else ("YELLOW" if (int(now/8)+j["id"])%3==1 else "RED")
        STATE["last_update"]=now
        capture_performance_sample("periodic")
        forecast = build_density_forecast()
        return {**STATE,"metrics":totals(),"edges":EDGES,"forecast":forecast}

def find_route(start, end):
    graph={i:[] for i in range(1,10)}
    for a,b in EDGES: graph[a+1].append(b+1); graph[b+1].append(a+1)
    queue=[(start,[start])]; seen={start}
    while queue:
        node,path=queue.pop(0)
        if node==end:return path
        for nxt in graph[node]:
            if nxt not in seen: seen.add(nxt); queue.append((nxt,path+[nxt]))
    return [start,end]

def run_video():
    with LOCK:
        STATE["video"]={"status":"Running S14.13 YOLO analysis…", "result":None}
        event("Video analysis started using existing S14.13 controller")
    try:
        import sys
        if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
        from app.detection.realtime_signal_controller import RealtimeSignalController
        if not VIDEO_PATH.exists(): raise FileNotFoundError(f"Video not found: {VIDEO_PATH}")
        controller=RealtimeSignalController(video_path=str(VIDEO_PATH), confidence=0.40, process_every_n_frames=10)
        result=controller.run()
        decisions=result.get("decisions",[])
        # Keep a compact, explainable decision series from the real video-controller output.
        series=[]
        for d in decisions:
            series.append({"frame":int(d.get("frame",0) or 0),"timestamp":round(float(d.get("timestamp",0) or 0),2),"vehicle_count":int(d.get("vehicle_count",0) or 0),"green_time":int(d.get("green_time",0) or 0),"traffic_level":str(d.get("traffic_level","UNKNOWN")),"direction":str(d.get("direction","UNKNOWN"))})
        counts=[x["vehicle_count"] for x in series]
        # Explainable temporal screening is kept in the existing detection package.
        # These are operator-review candidates, not confirmed incidents.
        from app.detection.incident_detector import IncidentDetector
        candidates=IncidentDetector().detect_from_decisions(series)
        summary={"total_frames":result.get("total_frames",0),"decision_count":len(decisions),"processing_time":round(float(result.get("processing_time",0) or 0),2),"first":decisions[0] if decisions else None,"last":decisions[-1] if decisions else None,"mean_vehicle_count":round(sum(counts)/len(counts),1) if counts else 0,"min_vehicle_count":min(counts) if counts else 0,"max_vehicle_count":max(counts) if counts else 0,"candidate_event_count":len(candidates)}
        with LOCK:
            STATE["video"]={"status":"Completed", "result":summary}
            STATE["camera_screening"]={"status":"Completed · heuristic review only","candidate_events":candidates[:20],"series":series[-60:]}
            event(f"Video analysis complete · {summary['total_frames']} frames · {summary['decision_count']} AI decisions")
            if candidates:
                event(f"Camera review flagged {len(candidates)} abrupt count-change candidate(s); operator verification required")
            else:
                event("Camera review found no abrupt count-drop candidates in sampled decisions")
    except Exception as exc:
        with LOCK:
            STATE["video"]={"status":"Failed: "+str(exc), "result":None}
            event("Video analysis failed; see status for details")

HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Traffic Command Centre</title><style>
:root{--bg:#080d17;--panel:#101a2a;--line:#20334c;--text:#edf5ff;--muted:#8da3bd;--cyan:#4de4f0;--green:#42e6a4;--amber:#ffbf69;--red:#ff667a}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 20% 0%,#11243a 0,transparent 42%),var(--bg);color:var(--text);font:14px/1.45 Segoe UI,Arial,sans-serif}header{display:flex;justify-content:space-between;align-items:center;padding:22px 3vw;border-bottom:1px solid var(--line);gap:15px;flex-wrap:wrap}h1{font-size:clamp(22px,3vw,34px);letter-spacing:.04em;margin:0;font-weight:800}h1 span{color:var(--cyan)}.sub{color:var(--muted);margin-top:4px}.pill{border:1px solid #31516d;border-radius:99px;padding:7px 12px;color:var(--cyan);font-size:11px;letter-spacing:.08em}.wrap{padding:22px 3vw 40px;max-width:1600px;margin:auto}.metrics{display:grid;grid-template-columns:repeat(6,minmax(130px,1fr));gap:12px}.panel,.metric{background:linear-gradient(145deg,#111e30,#0c1421);border:1px solid var(--line);border-radius:13px;padding:16px;box-shadow:0 8px 25px #0002}.metric label{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.1em}.metric strong{display:block;font-size:28px;margin-top:8px}.metric small{color:var(--muted)}.layout{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,1fr);gap:14px;margin-top:14px}.panel h2{font-size:14px;letter-spacing:.1em;text-transform:uppercase;margin:0 0 14px}.network{position:relative;min-height:390px;background:radial-gradient(ellipse at center,#10283b,#0a1220 75%);border-radius:10px;overflow:hidden}.network svg{position:absolute;inset:0;width:100%;height:100%}.road{stroke:#2c3f55;stroke-width:7;stroke-linecap:round}.road2{stroke:#4d6276;stroke-width:1.4;stroke-dasharray:6 7}.node{cursor:pointer}.node circle{stroke-width:3;fill:#101b2b}.node text{fill:#fff;font-size:12px;font-weight:700;text-anchor:middle}.node .tiny{font-size:9px;fill:#a9bfd4;font-weight:400}.signal-green circle{stroke:var(--green)}.signal-red circle{stroke:var(--red)}.signal-yellow circle{stroke:var(--amber)}.node.active circle{fill:#153c4a;filter:drop-shadow(0 0 8px #4de4f0)}.legend{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:11px;margin-top:10px}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px}.controls{display:grid;grid-template-columns:1fr 1fr;gap:8px}.btn,select{background:#17283a;border:1px solid #34506a;color:var(--text);padding:10px 12px;border-radius:8px;cursor:pointer;font:inherit}.btn:hover{border-color:var(--cyan);color:var(--cyan)}.btn.primary{background:#123c49;border-color:#287887;color:#b7fbff}.btn.danger{border-color:#7b3c4d;color:#ffb3bf}.field{display:grid;gap:5px;color:var(--muted);font-size:12px;margin-bottom:10px}.field select{width:100%}.table{width:100%;border-collapse:collapse;font-size:12px}.table th,.table td{text-align:left;padding:10px 7px;border-bottom:1px solid #1d2c40}.table th{color:var(--muted);font-weight:500}.status{font-size:10px;letter-spacing:.06em;border-radius:5px;padding:4px 6px;background:#152a36;color:var(--green)}.status.red{color:var(--red);background:#321c2b}.status.yellow{color:var(--amber);background:#332a1c}.scroll{overflow:auto;max-height:310px}.bars{display:flex;align-items:end;gap:8px;height:130px;padding:12px 5px 0}.barwrap{flex:1;text-align:center;color:var(--muted);font-size:10px}.bar{margin:0 auto 7px;width:65%;min-width:14px;max-width:42px;border-radius:5px 5px 0 0;background:linear-gradient(#4de4f0,#2465a3);min-height:6px}.log{color:var(--muted);font-size:12px}.log div{padding:8px 0;border-bottom:1px solid #1d2c40}.log time{color:var(--cyan);margin-right:8px}.small{color:var(--muted);font-size:11px}.videoresult{margin-top:12px;padding:10px;border:1px solid var(--line);border-radius:8px;color:var(--muted);white-space:pre-wrap;overflow-wrap:anywhere}.foot{margin-top:18px;color:#71869f;font-size:11px;text-align:center}@media(max-width:1000px){.metrics{grid-template-columns:repeat(3,1fr)}.layout{grid-template-columns:1fr}}@media(max-width:550px){.metrics{grid-template-columns:repeat(2,1fr)}.wrap{padding:14px}.network{min-height:320px}}
</style></head><body><header><div><h1>AI CITY <span>TRAFFIC</span> COMMAND</h1><div class="sub">Adaptive mobility · emergency priority · network intelligence</div></div><div class="pill">● LOCAL PROTOTYPE / SIMULATED CITY FEED</div></header><main class="wrap"><section class="metrics" id="metrics"></section><div class="layout"><section class="panel"><h2>01 / City junction network <span class="small">— select a node</span></h2><div class="network"><svg id="map" viewBox="0 0 700 390" preserveAspectRatio="xMidYMid meet"></svg></div><div class="legend"><span><i class="dot" style="background:var(--green)"></i>Green phase</span><span><i class="dot" style="background:var(--amber)"></i>Yellow phase</span><span><i class="dot" style="background:var(--red)"></i>Red phase</span><span id="selected">Selected: J1</span></div><div class="scroll"><table class="table"><thead><tr><th>Junction</th><th>Vehicles</th><th>Queue</th><th>Wait</th><th>Signal</th><th>Green</th><th>Critical approach</th><th>Flow/hr*</th><th>Efficiency*</th></tr></thead><tbody id="junctionRows"></tbody></table></div></section><aside class="panel"><h2>02 / Command actions</h2><label class="field">Dispatch from <select id="start"></select></label><label class="field">Destination <select id="end"></select></label><button class="btn primary" style="width:100%" onclick="action('ambulance')">🚑 Dispatch ambulance corridor</button><button class="btn" style="width:100%;margin-top:8px" onclick="action('optimize')">⚡ Optimize signal network</button><button class="btn" style="width:100%;margin-top:8px" onclick="action('coordinate')">🔗 Activate coordinated green wave</button><hr style="border:0;border-top:1px solid var(--line);margin:16px 0"><label class="field">Report incident <select id="incidentType"><option>Accident</option><option>Vehicle breakdown</option><option>Road blockage</option><option>Waterlogging</option><option>Illegal parking / encroachment</option><option>Construction</option><option>Sudden traffic stop</option></select></label><label class="field">Affected junction <select id="incidentJ"></select></label><button class="btn danger" style="width:100%" onclick="action('incident')">＋ Log incident</button><label class="field" style="margin-top:12px">Weather / road condition <select id="weather"><option>Clear</option><option>Light rain</option><option>Heavy rain</option><option>Waterlogging risk</option><option>Road works</option><option>Dense fog</option><option>Road closure</option></select></label><button class="btn" style="width:100%" onclick="action('weather')">Apply conditions</button><div class="videoresult" id="roadImpact">Weather/road scenario not applied.</div><hr style="border:0;border-top:1px solid var(--line);margin:16px 0"><h2>03 / OpenCV + YOLO</h2><div class="small">Runs your existing S14.13 controller against data/videos/traffic.mp4.</div><button class="btn primary" style="width:100%;margin-top:10px" onclick="action('video')">▶ Run video analysis</button><div class="videoresult" id="videoResult">Video analysis not started.</div></aside></div><div class="layout"><section class="panel"><h2>04 / Camera evidence & event screening</h2><div class="small">Uses the sampled vehicle-count decisions from the actual video run. Abrupt changes receive a heuristic review score only—not a probability or confirmed accident, breakdown, or blockage.</div><div id="cameraSummary" class="videoresult">Run video analysis to populate camera evidence.</div><div class="scroll"><table class="table"><thead><tr><th>Timestamp</th><th>Frame</th><th>Previous count</th><th>Current count</th><th>Change</th><th>Review score*</th><th>Review</th></tr></thead><tbody id="cameraEvents"><tr><td colspan="7">No camera review results yet.</td></tr></tbody></table></div></section></div><div class="layout"><section class="panel"><h2>05 / Density outlook · next 30 min</h2><div class="small">Damped trend baseline using recent simulated density samples; not a trained/validated real-world forecast.</div><div class="bars" id="forecast"></div></section><section class="panel"><h2>06 / Signal performance analytics</h2><div class="small">Ranks simulated junctions by wait, queue and efficiency. Recommendations are advisory estimates, not measured improvements.</div><button class="btn primary" style="margin:10px 0;width:100%" onclick="action('analytics')">📊 Analyze underperforming junctions</button><div class="scroll"><table class="table"><thead><tr><th>Junction</th><th>Wait</th><th>Queue</th><th>Efficiency*</th><th>Suggested action</th></tr></thead><tbody id="analyticsRows"><tr><td colspan="5">Click Analyze to calculate recommendations.</td></tr></tbody></table></div></section></div><div class="layout"><section class="panel"><h2>07 / Fuel waste hotspots · estimate</h2><div class="small">Ranks junctions by the prototype's queue/wait-based fuel-waste estimate. Daily values assume 8 operating hours; the 10% savings figure is a scenario, not a measured reduction.</div><button class="btn primary" style="margin:10px 0;width:100%" onclick="action('fuel')">⛽ Analyze fuel-waste hotspots</button><div id="fuelSummary" class="videoresult">Click Analyze to rank fuel-waste hotspots.</div><div class="scroll"><table class="table"><thead><tr><th>Junction</th><th>Est. L/hr</th><th>Est. L/day</th><th>Queue</th><th>Wait</th><th>10% scenario saving</th><th>Suggested review</th></tr></thead><tbody id="fuelRows"><tr><td colspan="7">Click Analyze to calculate estimated hotspots.</td></tr></tbody></table></div></section></div><div class="layout"><section class="panel"><h2>08 / Performance history & trend</h2><div class="small">Rolling snapshots are held in memory while this dashboard process runs. Compare waiting time, queue, throughput, efficiency and fuel estimates across samples.</div><div class="videoresult" id="historySummary">Collecting performance samples…</div><div class="scroll"><table class="table"><thead><tr><th>Time</th><th>Avg wait</th><th>Avg queue</th><th>Avg density</th><th>Throughput/hr*</th><th>Efficiency*</th><th>Fuel est. L/hr</th></tr></thead><tbody id="historyRows"><tr><td colspan="7">Samples appear as the dashboard runs.</td></tr></tbody></table></div></section></div><div class="layout"><section class="panel"><h2>09 / Closed-loop optimization</h2><div class="small">Runs a demo Detect → Analyze → Decide → Act → Measure cycle and compares model metrics before and after. This is not real-world proof of improvement.</div><button class="btn primary" style="margin:10px 0;width:100%" onclick="action('closed_loop')">🔁 Run closed-loop optimization</button><div class="videoresult" id="optimizationSummary">Run the cycle to see before/after metrics.</div><div class="scroll"><table class="table"><thead><tr><th>Junction</th><th>Green change</th><th>Queue before → after</th><th>Wait before → after</th></tr></thead><tbody id="optimizationRows"><tr><td colspan="4">No optimization cycle run yet.</td></tr></tbody></table></div></section><section class="panel"><h2>10 / 30-minute traffic forecast</h2><div class="small">Uses a damped linear trend from recent simulated density snapshots. This is a transparent baseline, not a trained/validated AI forecasting model.</div><div class="videoresult" id="forecastSummary">Forecast warming up…</div><div class="bars" id="forecast"></div></section></div><div class="layout"><section class="panel"><h2>11 / Operations event stream</h2><div class="log" id="events"></div></section></div><div class="small" style="margin-top:8px">Adaptive timing uses simulated vehicle count, queue, wait and pedestrian pressure. Camera count-change screening and its review score are heuristic and require operator verification. Flow/efficiency/fuel values and closed-loop before/after results are simulated estimates, not live sensor measurements. History is in-memory for this dashboard session.</div><div class="foot">P1 HACKATHON DEMO · Simulated network metrics are not live municipal data. No real traffic signals are controlled.</div></main><script>
let state=null,selected=1;const $=id=>document.getElementById(id);async function action(type){let body={action:type,start:+$('start').value,end:+$('end').value,incidentType:$('incidentType').value,junction:+$('incidentJ').value,weather:$('weather').value};try{let r=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let d=await r.json();if(d.message)console.log(d.message);await refresh()}catch(e){alert('Dashboard server not responding: '+e)}}
function initSelects(){for(let id of ['start','end','incidentJ']){$(id).innerHTML=state.junctions.map(j=>`<option value="${j.id}">J${j.id} · ${j.name.split('·')[1]}</option>`).join('')} $('end').value='9'}function drawMap(){let p={1:[100,70],2:[275,70],3:[450,70],4:[100,195],5:[275,195],6:[450,195],7:[100,320],8:[275,320],9:[450,320]};let svg=$('map');let lines=state.edges.map(([a,b])=>{let x=p[a+1],y=p[b+1];return `<line class="road" x1="${x[0]}" y1="${x[1]}" x2="${y[0]}" y2="${y[1]}"/><line class="road2" x1="${x[0]}" y1="${x[1]}" x2="${y[0]}" y2="${y[1]}"/>`}).join('');let nodes=state.junctions.map(j=>{let [x,y]=p[j.id],cl=j.phase==='GREEN'?'signal-green':j.phase==='YELLOW'?'signal-yellow':'signal-red';return `<g class="node ${cl} ${selected===j.id?'active':''}" onclick="selected=${j.id};$('selected').textContent='Selected: J${j.id}';drawMap()"><circle cx="${x}" cy="${y}" r="24"/><text x="${x}" y="${y-2}">J${j.id}</text><text class="tiny" x="${x}" y="${y+11}">${j.density}%</text></g>`}).join('');svg.innerHTML=lines+nodes}
function render(){let ph=state.performance_history||[];let hs=ph.slice(-12);$('historyRows').innerHTML=hs.length?hs.slice().reverse().map(x=>`<tr><td>${x.time}</td><td>${x.avg_wait}s</td><td>${x.avg_queue}</td><td>${x.avg_density}%</td><td>${x.throughput}</td><td>${x.efficiency}%</td><td>${x.fuel_l_hr}</td></tr>`).join(''):'<tr><td colspan="7">Collecting samples…</td></tr>';if(hs.length>=2){let a=hs[0],b=hs[hs.length-1];$('historySummary').textContent=`Samples this run: ${ph.length} · Latest vs oldest displayed: wait ${b.avg_wait-a.avg_wait>=0?'+':''}${(b.avg_wait-a.avg_wait).toFixed(1)}s, queue ${(b.avg_queue-a.avg_queue)>=0?'+':''}${(b.avg_queue-a.avg_queue).toFixed(1)}, efficiency ${(b.efficiency-a.efficiency)>=0?'+':''}${(b.efficiency-a.efficiency).toFixed(1)} points. Demo metrics only.`}else{$('historySummary').textContent=`Samples this run: ${ph.length}. Keep the dashboard open to collect more comparisons.`}let os=state.optimization_summary;if(os){$('optimizationSummary').textContent=`Before → after (simulated): avg wait ${os.before.avg_wait}s → ${os.after.avg_wait}s (${os.wait_reduction_pct}% change); avg queue ${os.before.avg_queue} → ${os.after.avg_queue} (${os.queue_reduction_pct}% change); fuel estimate ${os.before.fuel_l_hr} → ${os.after.fuel_l_hr} L/hr (${os.fuel_estimate_reduction_pct}% change); throughput ${os.throughput_change_pct>=0?'+':''}${os.throughput_change_pct}%. Adjusted junctions: ${os.junctions_adjusted}. ${os.note}`;$('optimizationRows').innerHTML=os.changes.map(x=>`<tr><td>J${x.id}</td><td>${x.green_before}s → ${x.green_after}s (${x.delta>=0?'+':''}${x.delta}s)</td><td>${x.queue_before} → ${x.queue_after}</td><td>${x.wait_before}s → ${x.wait_after}s</td></tr>`).join('')}let fs=state.forecast_summary||{};$('forecastSummary').textContent=`Current average density: ${fs.current_density??'—'}% · Trend: ${fs.trend_per_min??0} percentage points/min · Basis: ${fs.basis||'warming up'} · ${fs.caveat||''}`;let wi=state.weather_impact||{};$('roadImpact').textContent='Current scenario: '+(wi.condition||state.weather)+'\nEstimated capacity remaining: '+(wi.estimated_capacity_remaining_pct??100)+'% (model assumption)\nEstimated capacity reduction: '+(wi.estimated_capacity_loss_pct??0)+'%\n'+(wi.note||'Apply a condition to model its effect.');let m=state.metrics;$('metrics').innerHTML=[['JUNCTIONS',m.junctions,'connected demo nodes'],['CONGESTED',m.congested,'high-density nodes'],['VEHICLES',m.vehicles,'simulated count'],['AVG WAIT',m.avg_wait+'s','estimated network wait'],['ACTIVE INCIDENTS',m.incidents,'reported / simulated alerts'],['FUEL ESTIMATE',m.fuel_l_day+' L/day','illustrative model']].map(x=>`<div class="metric"><label>${x[0]}</label><strong>${x[1]}</strong><small>${x[2]}</small></div>`).join('');$('junctionRows').innerHTML=state.junctions.map(j=>`<tr><td>J${j.id} · ${j.name.split('·')[1]}</td><td>${j.vehicles}</td><td>${j.queue}</td><td>${j.wait}s</td><td><span class="status ${j.phase==='RED'?'red':j.phase==='YELLOW'?'yellow':''}">${j.phase}</span></td><td>${j.green}s</td><td>${j.critical_direction}</td><td>${j.throughput}</td><td>${j.efficiency}%</td></tr>`).join('');$('analyticsRows').innerHTML=state.analytics&&state.analytics.length?state.analytics.map(a=>`<tr><td>J${a.id} · ${esc(a.name.split('·')[1])}</td><td>${a.wait}s</td><td>${a.queue}</td><td>${a.efficiency}%</td><td><strong>${a.action}</strong><br><span class="small">${esc(a.recommendation)}</span></td></tr>`).join(''):'<tr><td colspan="5">Click Analyze to calculate recommendations.</td></tr>';let fa=state.fuel_analytics||[];$('fuelRows').innerHTML=fa.length?fa.map(a=>`<tr><td>J${a.id} · ${esc(a.name.split('·')[1])}</td><td>${a.fuel_l_hr}</td><td>${a.fuel_l_day}</td><td>${a.queue}</td><td>${a.wait}s</td><td>${a.potential_saving_l_day} L/day</td><td>${esc(a.action)}</td></tr>`).join(''):'<tr><td colspan="7">Click Analyze to calculate estimated hotspots.</td></tr>';let fm=state.fuel_summary||{};$('fuelSummary').textContent=fm.estimated_city_l_hr!==undefined?`Estimated network fuel waste: ${fm.estimated_city_l_hr} L/hr\nEstimated 8-hour day: ${fm.estimated_city_l_day} L/day\nIllustrative 10% scenario saving: ${fm.illustrative_10pct_saving_l_day} L/day\n${fm.assumption}`:'Click Analyze to calculate estimated hotspots.';$('forecast').innerHTML=state.forecast.map(f=>`<div class="barwrap"><div class="bar" style="height:${f.density}%" title="${f.density}% density"></div>${f.minute}m<br>${f.density}%</div>`).join('');$('events').innerHTML=state.events.length?state.events.map(e=>`<div><time>${e.time}</time>${esc(e.message)}</div>`).join(''):'No events yet.';$('videoResult').textContent=state.video.status+(state.video.result?'\n'+JSON.stringify(state.video.result,null,2):'');let cs=state.camera_screening||{};let vr=state.video.result||{};$('cameraSummary').textContent=cs.status||'Waiting for video analysis';if(vr.decision_count!==undefined){$('cameraSummary').textContent=(cs.status||'Camera review')+'\nFrames: '+(vr.total_frames??0)+' · decisions: '+vr.decision_count+' · mean detected vehicles/decision: '+(vr.mean_vehicle_count??'n/a')+' · sampled range: '+(vr.min_vehicle_count??'n/a')+'–'+(vr.max_vehicle_count??'n/a')+' · review candidates: '+(vr.candidate_event_count??0)}let ce=cs.candidate_events||[];$('cameraEvents').innerHTML=ce.length?ce.map(e=>`<tr><td>${e.timestamp}s</td><td>${e.frame}</td><td>${e.previous_count}</td><td>${e.current_count}</td><td>-${e.drop} (${e.drop_ratio_pct}%)</td><td>${e.review_score}/100*</td><td>${esc(e.label)}</td></tr>`).join(''):'<tr><td colspan="7">No abrupt count-drop candidates found in sampled decisions. This does not prove the video contains no incidents.</td></tr>';drawMap()}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}async function refresh(){let r=await fetch('/api/state');state=await r.json();if(!$('start').options.length)initSelects();render()}refresh();setInterval(refresh,3000);
</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def send_json(self,obj,status=200):
        raw=json.dumps(obj).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path in ('/','/index.html'):
            raw=HTML.encode(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
        elif self.path=='/api/state': self.send_json(snapshot())
        elif self.path=='/health': self.send_json({'ok':True,'video_exists':VIDEO_PATH.exists(),'video_path':str(VIDEO_PATH)})
        else: self.send_json({'error':'not found'},404)
    def do_POST(self):
        if self.path!='/api/action': self.send_json({'error':'not found'},404); return
        try: data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
        except Exception: self.send_json({'error':'invalid json'},400); return
        action=data.get('action')
        with LOCK:
            if action=='incident':
                incident={'id':int(time.time()*1000)%1000000,'type':str(data.get('incidentType','Incident')),'junction':int(data.get('junction',1)),'time':time.strftime('%H:%M:%S'),'status':'OPEN'}
                STATE['incidents'].insert(0,incident); STATE['incidents'][:]=STATE['incidents'][:20]; event(f"Incident reported: {incident['type']} at J{incident['junction']}"); msg='Incident logged in demo.'
            elif action=='weather':
                STATE['weather']=str(data.get('weather','Clear')); event('Road/weather scenario applied: '+STATE['weather']+'; estimated capacity impact will be reflected in simulated queue, wait, throughput and fuel metrics'); msg='Road/weather scenario applied to the simulated network; impacts are model estimates.'
            elif action=='closed_loop':
                run_closed_loop_optimization()
                analyze_performance()
                STATE['fuel_summary']=analyze_fuel_hotspots()
                msg='Closed-loop demo cycle completed; inspect before/after estimates and junction changes.'
            elif action=='fuel':
                STATE['fuel_summary']=analyze_fuel_hotspots()
                event('Fuel analytics ranked top 5 simulated fuel-waste hotspots; daily estimates assume 8 operating hours')
                msg='Fuel hotspot analysis complete; fuel and savings values are estimates.'
            elif action=='analytics':
                results=analyze_performance()
                if results:
                    event('Signal analytics ranked the top 5 underperforming demo junctions and generated advisory timing recommendations')
                msg='Performance analysis complete; recommendations are advisory model estimates.'
            elif action=='optimize':
                for j in STATE['junctions']:
                    score=.42*j['density'] + .34*(j['queue']/40*100) + .18*(j['wait']/180*100) + .06*min(100,j.get('pedestrians',0)*3)
                    j['green']=max(20,min(90,round(20+score*.70)))
                event('Adaptive signal optimizer recalculated green times from density, queue, wait and pedestrian pressure'); msg='Adaptive green times recalculated from live demo state.'
            elif action=='coordinate':
                STATE['coordination_active']=True
                STATE['green_wave']=[1,2,3,6,9]
                event('Coordinated green wave activated along J1 → J2 → J3 → J6 → J9')
                msg='Green-wave coordination activated on the demo corridor.'
            elif action=='ambulance':
                start=max(1,min(9,int(data.get('start',1)))); end=max(1,min(9,int(data.get('end',9))))
                route=find_route(start,end); STATE['coordination_active']=False; STATE['ambulance']={'id':'AMB-P1','route':route,'current':route[0],'destination':end,'step':0,'last_step_at':time.time(),'status':'CORRIDOR ACTIVE'}
                for j in STATE['junctions']:
                    if j['id'] in route: j['phase']='GREEN' if j['id']==start else 'RED'
                event('Ambulance corridor simulated: '+' → '.join('J'+str(n) for n in route)); msg='Simulated ambulance corridor activated; no real signals are controlled.'
            elif action=='video':
                if STATE['video']['status'].startswith('Running'): msg='Video analysis is already running.'
                else: threading.Thread(target=run_video,daemon=True).start(); msg='S14.13 video analysis launched in background.'
            else: self.send_json({'error':'unknown action'},400); return
        self.send_json({'ok':True,'message':msg})

def main():
    host='127.0.0.1'; port=8000
    server=ThreadingHTTPServer((host,port),Handler)
    url=f'http://{host}:{port}'
    print('\n'+'='*65+'\n AI CITY TRAFFIC COMMAND CENTRE — P1\n'+'='*65)
    print('Open in browser:',url)
    print('City network: simulated | Video analysis: existing S14.13 controller')
    print('Press Ctrl+C to stop.\n')
    threading.Timer(1.0,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print('\nStopping dashboard…')
    finally: server.server_close()

if __name__=='__main__': main()
