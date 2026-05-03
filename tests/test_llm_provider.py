import pytest
from unittest.mock import MagicMock, patch
from src.providers.llm import LLMProvider
from src.config import Settings

@pytest.fixture
def mock_openai():
    with patch("src.providers.llm.OpenAI") as mock:
        yield mock

def test_llm_provider_init(mock_openai):
    # Test that it uses Settings defaults when no args provided
    provider = LLMProvider()
    
    mock_openai.assert_called_once_with(
        base_url=Settings.LLM_BASE_URL,
        api_key=Settings.LLM_API_KEY
    )
    assert provider._model == Settings.LLM_MODEL

def test_llm_provider_init_overrides(mock_openai):
    # Test that it respects overrides
    custom_url = "https://custom.api/v1"
    custom_key = "sk-custom-123"
    custom_model = "custom-model-x"
    
    provider = LLMProvider(base_url=custom_url, api_key=custom_key, model=custom_model)
    
    mock_openai.assert_called_once_with(
        base_url=custom_url,
        api_key=custom_key
    )
    assert provider._model == custom_model

def test_llm_provider_call(mock_openai):
    provider = LLMProvider()
    
    # Mock the response
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="  Mocked Response  "))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    result = provider.call(system="sys", user="usr")
    
    # Verify parameters passed to create()
    mock_client.chat.completions.create.assert_called_once_with(
        model=Settings.LLM_MODEL,
        temperature=Settings.LLM_TEMPERATURE,
        max_tokens=Settings.LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ]
    )
    
    assert result == "Mocked Response"

def test_llm_provider_call_overrides(mock_openai):
    provider = LLMProvider()
    mock_client = mock_openai.return_value
    
    provider.call(system="sys", user="usr", temperature=0.9, max_tokens=100)
    
    # Verify overrides are respected
    mock_client.chat.completions.create.assert_called_once_with(
        model=Settings.LLM_MODEL,
        temperature=0.9,
        max_tokens=100,
        messages=[
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ]
    )
