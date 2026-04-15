from open_deep_research.pytest_support import (
    get_optional_pytest_option,
    get_report_quality_test_skip_reason,
)


class _FakeConfig:
    def __init__(self, value=None, raises=False):
        self._value = value
        self._raises = raises

    def getoption(self, option_name):
        if self._raises:
            raise ValueError(f"no option named {option_name!r}")
        return self._value


class _FakeRequest:
    def __init__(self, config):
        self.config = config


def test_get_optional_pytest_option_returns_none_for_undeclared_options():
    request = _FakeRequest(_FakeConfig(raises=True))

    assert get_optional_pytest_option(request, "--research-agent") is None


def test_get_optional_pytest_option_returns_declared_value():
    request = _FakeRequest(_FakeConfig(value="multi_agent"))

    assert get_optional_pytest_option(request, "--research-agent") == "multi_agent"


def test_report_quality_test_requires_explicit_opt_in():
    reason = get_report_quality_test_skip_reason(
        research_agent="multi_agent",
        search_api="tavily",
        models={
            "supervisor_model": "anthropic:claude-3-7-sonnet-latest",
            "researcher_model": "anthropic:claude-3-5-sonnet-latest",
        },
        eval_model="anthropic:claude-3-7-sonnet-latest",
        env={},
    )

    assert reason == "Set RUN_LANGSMITH_INTEGRATION_TESTS=true to run LangSmith-backed integration tests."


def test_report_quality_test_runs_when_required_env_is_present():
    reason = get_report_quality_test_skip_reason(
        research_agent="multi_agent",
        search_api="tavily",
        models={
            "supervisor_model": "anthropic:claude-3-7-sonnet-latest",
            "researcher_model": "anthropic:claude-3-5-sonnet-latest",
        },
        eval_model="anthropic:claude-3-7-sonnet-latest",
        env={
            "RUN_LANGSMITH_INTEGRATION_TESTS": "true",
            "LANGSMITH_API_KEY": "ls-key",
            "TAVILY_API_KEY": "tvly-key",
            "ANTHROPIC_API_KEY": "anth-key",
        },
    )

    assert reason is None
