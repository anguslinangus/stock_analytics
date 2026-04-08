import pytest

from stock_analytics.indicators.valuation import compute_valuation_indicators


def test_pe_ttm(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # market_cap 3T / net_income 50B = 60
    assert ind.pe_ttm == pytest.approx(60.0)


def test_ps(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # 3T / 100B = 30
    assert ind.ps == pytest.approx(30.0)


def test_ev_ebitda(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # EV = 3T + 10B debt - 30B cash = 2980B; /65B EBITDA = 45.85
    assert ind.ev_ebitda == pytest.approx(45.846, rel=1e-3)


def test_pb(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    # 3T / 50B book = 60
    assert ind.pb == pytest.approx(60.0)


def test_dcf_assumptions_recorded(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    assert ind.dcf_assumptions["wacc"] == 0.09
    assert ind.dcf_assumptions["terminal_growth"] == 0.03
    assert ind.dcf_assumptions["growth_path"] == [0.25, 0.20, 0.16, 0.12, 0.08]


def test_dcf_produces_positive_fair_value(sample_nvda_raw):
    ind = compute_valuation_indicators(sample_nvda_raw)
    assert ind.dcf_fair_value is not None
    assert ind.dcf_fair_value > 0
    # upside_pct should be a real number (positive or negative)
    assert ind.dcf_upside_pct is not None
