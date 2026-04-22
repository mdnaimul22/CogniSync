from src.helpers.masking import mask_sensitive_data

def test_mask_sensitive_data():
    test_str = 'key=nvapi-abc123def456ghijk and sk-proj-abcdefghijklmnopqrstuv and token="ghp_abcdefghijklmnopqrstuvwxyz1234567890"'
    masked = mask_sensitive_data(test_str)
    
    assert "nvapi-abc123def456ghijk" not in masked
    assert "sk-proj-abcdefghijklmnopqrstuv" not in masked
    assert "ghp_abcdefghijklmnopqrstuvwxyz1234567890" not in masked
    assert "[REDACTED]" in masked
