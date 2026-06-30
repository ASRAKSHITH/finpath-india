import json
import logging
from datetime import datetime
from pathlib import Path


class ProductionLogger:
    def __init__(self, log_dir: str = "finpath_logs"):
        self.traces = {}
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "agent_calls": {},
            "tool_calls": {},
            "response_times_ms": [],
        }

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        self.logger = logging.getLogger("FinPathIndia")

    def start_trace(self, user_query: str) -> str:
        trace_id = f"trace{len(self.traces)+1:04d}{datetime.now().strftime('%H%M%S')}"
        event = {
            "trace_id": trace_id,
            "query": user_query,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
        }
        self.traces[trace_id] = event
        self.traces[trace_id]["events"] = []
        self.metrics["total_requests"] += 1
        
        # Structured log for observability platform
        self.logger.info(json.dumps({"event_type": "START_TRACE", **event}))
        return trace_id

    def log_agent_event(self, trace_id: str, agent_name: str, output: str):
        if trace_id in self.traces:
            event = {
                "type": "agent",
                "agent": agent_name,
                "output": output[:500], # truncating for log size
                "timestamp": datetime.now().isoformat(),
                "trace_id": trace_id
            }
            self.traces[trace_id]["events"].append(event)
            self.metrics["agent_calls"][agent_name] = self.metrics["agent_calls"].get(agent_name, 0) + 1
            self.logger.info(json.dumps({"event_type": "AGENT_CALL", **event}))

    def log_tool_call(self, trace_id: str, tool_name: str, result: dict):
        if trace_id in self.traces:
            event = {
                "type": "tool",
                "tool": tool_name,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "trace_id": trace_id
            }
            self.traces[trace_id]["events"].append(event)
            self.metrics["tool_calls"][tool_name] = self.metrics["tool_calls"].get(tool_name, 0) + 1
            self.logger.info(json.dumps({"event_type": "TOOL_CALL", **event}))

    def complete_trace(self, trace_id: str, duration_ms: float, success: bool = True):
        if trace_id in self.traces:
            self.traces[trace_id]["status"] = "success" if success else "failed"
            self.traces[trace_id]["end_time"] = datetime.now().isoformat()
            self.traces[trace_id]["total_duration_ms"] = round(duration_ms, 2)
            
            self.logger.info(json.dumps({
                "event_type": "COMPLETE_TRACE",
                "trace_id": trace_id,
                "status": self.traces[trace_id]["status"],
                "duration_ms": self.traces[trace_id]["total_duration_ms"]
            }))

        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

        self.metrics["response_times_ms"].append(duration_ms)

    def export(self):
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        traces_file = self.log_dir / f"traces_{ts}.json"
        metrics_file = self.log_dir / f"metrics_{ts}.json"

        with open(traces_file, "w", encoding="utf-8") as f:
            json.dump(self.traces, f, indent=2, ensure_ascii=False)

        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)

        return {"traces": str(traces_file), "metrics": str(metrics_file)}