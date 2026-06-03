"""Patch ADK telemetry to avoid JSON serialization errors with bytes in tool responses."""

from __future__ import annotations

import json
from typing import Any

import google.adk.telemetry as adk_telemetry


def _sanitize_for_json(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {str(k): _sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_for_json(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _safe_json_dumps(value: Any) -> str:
    return json.dumps(_sanitize_for_json(value), default=str)


def _patch_build_llm_request_for_trace(llm_request) -> dict[str, Any]:
    result = {
        "model": llm_request.model,
        "config": llm_request.config.model_dump(
            exclude_none=True, exclude="response_schema"
        ),
        "contents": [],
    }
    for content in llm_request.contents:
        safe_parts = []
        for part in content.parts or []:
            if getattr(part, "inline_data", None):
                continue
            dumped = part.model_dump(exclude_none=True)
            safe_parts.append(_sanitize_for_json(dumped))
        result["contents"].append({"role": content.role, "parts": safe_parts})
    return result


def apply() -> None:
    adk_telemetry._build_llm_request_for_trace = _patch_build_llm_request_for_trace

    original_trace_call_llm = adk_telemetry.trace_call_llm

    def safe_trace_call_llm(invocation_context, event_id, llm_request, llm_response):
        try:
            original_trace_call_llm(
                invocation_context, event_id, llm_request, llm_response
            )
        except (TypeError, ValueError):
            pass

    adk_telemetry.trace_call_llm = safe_trace_call_llm

    original_trace_tool_call = adk_telemetry.trace_tool_call

    def safe_trace_tool_call(args):
        try:
            original_trace_tool_call(args)
        except (TypeError, ValueError):
            pass

    adk_telemetry.trace_tool_call = safe_trace_tool_call

    original_trace_send_data = adk_telemetry.trace_send_data

    def safe_trace_send_data(invocation_context, event_id, data):
        try:
            original_trace_send_data(invocation_context, event_id, data)
        except (TypeError, ValueError):
            pass

    adk_telemetry.trace_send_data = safe_trace_send_data
