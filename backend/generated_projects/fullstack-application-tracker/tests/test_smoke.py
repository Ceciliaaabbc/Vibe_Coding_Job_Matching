from src.main import analyze, AnalyzeRequest

def test_analyze_returns_score():
    result = analyze(AnalyzeRequest(text='React project'))
    assert result['score'] > 0
