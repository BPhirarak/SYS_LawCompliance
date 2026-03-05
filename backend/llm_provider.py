"""
LLM Provider Abstraction
รองรับ: anthropic, openai, bedrock, grok, ollama, openrouter
ตั้งค่าผ่าน .env โดยใช้ LLM_PROVIDER=<provider>
"""
import os

def get_provider() -> str:
    """อ่าน provider จาก env ถ้าไม่ได้ตั้งค่าจะ auto-detect จาก key ที่มี"""
    p = os.environ.get("LLM_PROVIDER", "").lower().strip()
    if p: return p
    # Auto-detect fallback order
    if os.environ.get("ANTHROPIC_API_KEY"): return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):    return "openai"
    if os.environ.get("OPENROUTER_API_KEY"):return "openrouter"
    if os.environ.get("GROK_API_KEY"):      return "grok"
    if os.environ.get("AWS_BEDROCK_REGION"):return "bedrock"
    if os.environ.get("OLLAMA_BASE_URL"):   return "ollama"
    return "demo"

def call_llm(system: str, messages: list) -> str:
    """
    เรียก LLM ตาม provider ที่ตั้งค่าไว้
    messages: [{"role": "user"/"assistant", "content": "..."}]
    returns: reply string
    """
    provider = get_provider()

    # ── Anthropic Claude ──────────────────────────────────────────────────────
    if provider == "anthropic":
        import anthropic
        model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model=model,
            max_tokens=8096,
            system=system,
            messages=messages
        )
        return response.content[0].text

    # ── OpenAI ────────────────────────────────────────────────────────────────
    elif provider == "openai":
        import openai
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        # GPT-5.2, o3, o1 series use max_completion_tokens instead of max_tokens
        token_param = "max_completion_tokens" if any(x in model for x in ["gpt-5","o3","o1"]) else "max_tokens"
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            **{token_param: 8096}
        )
        return response.choices[0].message.content

    # ── AWS Bedrock ───────────────────────────────────────────────────────────
    elif provider == "bedrock":
        import boto3, json as _json
        region   = os.environ.get("AWS_BEDROCK_REGION", "us-east-1")
        model_id = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")
        # Support both IAM role (on EC2/ECS) and explicit key
        session_kwargs = {}
        if os.environ.get("AWS_ACCESS_KEY_ID"):
            session_kwargs = {
                "aws_access_key_id":     os.environ["AWS_ACCESS_KEY_ID"],
                "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
                "aws_session_token":     os.environ.get("AWS_SESSION_TOKEN"),
            }
        client = boto3.client("bedrock-runtime", region_name=region, **session_kwargs)
        body = _json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8096,
            "system": system,
            "messages": messages
        })
        response = client.invoke_model(modelId=model_id, body=body)
        result = _json.loads(response["body"].read())
        return result["content"][0]["text"]

    # ── Grok (xAI) ────────────────────────────────────────────────────────────
    elif provider == "grok":
        import openai  # Grok ใช้ OpenAI-compatible API
        model = os.environ.get("GROK_MODEL", "grok-3-mini")
        client = openai.OpenAI(
            api_key=os.environ["GROK_API_KEY"],
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=8096
        )
        return response.choices[0].message.content

    # ── Ollama (local) ────────────────────────────────────────────────────────
    elif provider == "ollama":
        import requests as _req
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        model    = os.environ.get("OLLAMA_MODEL", "llama3.2")
        payload  = {
            "model": model,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
            "options": {"num_predict": 8096}
        }
        r = _req.post(f"{base_url}/api/chat", json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"]

    # ── OpenRouter ────────────────────────────────────────────────────────────
    elif provider == "openrouter":
        import openai
        model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
        client = openai.OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL", "http://localhost:8000"),
                "X-Title": "Thai Law Compliance - SYS Steel"
            }
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=8096
        )
        return response.choices[0].message.content

    # ── Demo mode ─────────────────────────────────────────────────────────────
    else:
        raise ValueError("demo")


def call_llm_with_tools(system: str, messages: list, tools: list, tools_openai: list) -> dict:
    """
    เรียก LLM พร้อม tool definitions
    คืน dict:
      {"type": "text", "content": "..."}          — ตอบตรง
      {"type": "tool_use", "calls": [{"name":..., "id":..., "input":...}]}  — ต้องการเรียก tool
    """
    provider = get_provider()

    # ── Anthropic ─────────────────────────────────────────────────────────────
    if provider == "anthropic":
        import anthropic
        model  = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model=model, max_tokens=8096,
            system=system, messages=messages,
            tools=tools
        )
        if resp.stop_reason == "tool_use":
            calls = [
                {"name": b.name, "id": b.id, "input": b.input}
                for b in resp.content if b.type == "tool_use"
            ]
            return {"type": "tool_use", "calls": calls, "raw_content": resp.content}
        text = next((b.text for b in resp.content if hasattr(b, "text")), "")
        return {"type": "text", "content": text}

    # ── OpenAI / Grok / OpenRouter (OpenAI-compatible) ────────────────────────
    elif provider in ("openai", "grok", "openrouter"):
        import openai as _oai
        if provider == "openai":
            client = _oai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            model  = os.environ.get("OPENAI_MODEL", "gpt-4o")
        elif provider == "grok":
            client = _oai.OpenAI(api_key=os.environ["GROK_API_KEY"], base_url="https://api.x.ai/v1")
            model  = os.environ.get("GROK_MODEL", "grok-3-mini")
        else:
            client = _oai.OpenAI(
                api_key=os.environ["OPENROUTER_API_KEY"],
                base_url="https://openrouter.ai/api/v1",
                default_headers={"HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL","http://localhost:8000"), "X-Title": "Thai Law Compliance"}
            )
            model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

        # GPT-5.2, o3, o1 series use max_completion_tokens
        token_param = "max_completion_tokens" if any(x in model for x in ["gpt-5","o3","o1"]) else "max_tokens"
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            tools=tools_openai, tool_choice="auto",
            **{token_param: 8096}
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            import json as _j
            calls = [
                {"name": tc.function.name, "id": tc.id, "input": _j.loads(tc.function.arguments)}
                for tc in msg.tool_calls
            ]
            return {"type": "tool_use", "calls": calls, "raw_message": msg}
        return {"type": "text", "content": msg.content or ""}

    # ── Bedrock ───────────────────────────────────────────────────────────────
    elif provider == "bedrock":
        import boto3, json as _j
        region   = os.environ.get("AWS_BEDROCK_REGION", "us-east-1")
        model_id = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")
        session_kwargs = {}
        if os.environ.get("AWS_ACCESS_KEY_ID"):
            session_kwargs = {
                "aws_access_key_id":     os.environ["AWS_ACCESS_KEY_ID"],
                "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
                "aws_session_token":     os.environ.get("AWS_SESSION_TOKEN"),
            }
        client = boto3.client("bedrock-runtime", region_name=region, **session_kwargs)
        body = _j.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8096,
            "system": system,
            "messages": messages,
            "tools": tools
        })
        response = client.invoke_model(modelId=model_id, body=body)
        result = _j.loads(response["body"].read())
        if result.get("stop_reason") == "tool_use":
            calls = [
                {"name": b["name"], "id": b["id"], "input": b["input"]}
                for b in result["content"] if b["type"] == "tool_use"
            ]
            return {"type": "tool_use", "calls": calls, "raw_content": result["content"]}
        text = next((b["text"] for b in result["content"] if b.get("type") == "text"), "")
        return {"type": "text", "content": text}

    # ── Ollama / Demo — fallback to plain call (no tool support) ──────────────
    else:
        text = call_llm(system, messages)
        return {"type": "text", "content": text}
