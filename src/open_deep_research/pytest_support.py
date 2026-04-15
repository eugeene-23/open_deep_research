"""Helpers for keeping environment-dependent pytest suites predictable."""

from __future__ import annotations

import os
from typing import Any, Mapping, Optional


def get_optional_pytest_option(request: Any, option_name: str) -> Optional[str]:
    """Return a pytest option when declared, otherwise return ``None``."""
    try:
        return request.config.getoption(option_name)
    except ValueError:
        return None


def get_report_quality_test_skip_reason(
    research_agent: str,
    search_api: str,
    models: Mapping[str, Any],
    eval_model: str,
    env: Optional[Mapping[str, str]] = None,
) -> Optional[str]:
    """Return a skip reason for the legacy report-quality integration test."""
    env_vars = dict(os.environ if env is None else env)
    if env_vars.get("RUN_LANGSMITH_INTEGRATION_TESTS", "").lower() != "true":
        return "Set RUN_LANGSMITH_INTEGRATION_TESTS=true to run LangSmith-backed integration tests."

    missing_vars = []
    if not env_vars.get("LANGSMITH_API_KEY"):
        missing_vars.append("LANGSMITH_API_KEY")
    if search_api == "tavily" and not env_vars.get("TAVILY_API_KEY"):
        missing_vars.append("TAVILY_API_KEY")

    model_names = [eval_model]
    if research_agent == "multi_agent":
        model_names.extend(
            [
                models.get("supervisor_model"),
                models.get("researcher_model"),
            ]
        )
    elif research_agent == "graph":
        planner_provider = models.get("planner_provider")
        planner_model = models.get("planner_model")
        writer_provider = models.get("writer_provider")
        writer_model = models.get("writer_model")
        if planner_provider and planner_model:
            model_names.append(f"{planner_provider}:{planner_model}")
        if writer_provider and writer_model:
            model_names.append(f"{writer_provider}:{writer_model}")

    required_vars = {
        required_env_var
        for model_name in model_names
        if (required_env_var := _provider_api_key_env_var(model_name)) is not None
    }
    for variable_name in sorted(required_vars):
        if not env_vars.get(variable_name):
            missing_vars.append(variable_name)

    if missing_vars:
        missing_display = ", ".join(sorted(set(missing_vars)))
        return f"Missing required integration test environment variables: {missing_display}"
    return None


def _provider_api_key_env_var(model_name: Any) -> Optional[str]:
    """Map a model identifier to its expected API key environment variable."""
    normalized = str(model_name or "").lower()
    if normalized.startswith("anthropic:"):
        return "ANTHROPIC_API_KEY"
    if normalized.startswith("openai:"):
        return "OPENAI_API_KEY"
    if normalized.startswith("google"):
        return "GOOGLE_API_KEY"
    if normalized.startswith("groq:"):
        return "GROQ_API_KEY"
    return None
