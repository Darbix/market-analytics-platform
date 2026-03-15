from pytest import approx

from app.services.analysis_service import compute_analysis


def test_compute_analysis():
    data = []
    for i in range(20):
        price = 100 + i
        # Fields: [OT, OP, HP, LP, CP, V, CT, _, _, _, _, _]
        data.append([i*1000, price, price+1, price-1, price, 100, i*1000+999, 0, 0, 0, 0, 0])

    result = compute_analysis(data, 10)

    assert "volatility" in result
    assert "monte_carlo_mean" in result
    assert result["rsi_last"] == approx(100.0)
