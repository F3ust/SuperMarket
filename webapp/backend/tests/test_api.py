from fastapi.testclient import TestClient

from app.main import app

c = TestClient(app)


def test_health_and_sections():
    assert c.get("/api/health").json()["sections"] == 12
    ids = [s["id"] for s in c.get("/api/sections").json()]
    assert ids[0] == "nguon" and "du-bao" in ids
    s = c.get("/api/sections/gia").json()
    assert s["findings"] and s["findings"][0]["charts"][0]["chart"] == "cElastic"
    assert c.get("/api/sections/khong-co").status_code == 404


def test_charts_and_meta():
    d = c.get("/api/charts").json()
    assert "D" in d and "D2" in d and len(d["D"]["elasticity"]) == 11
    m = c.get("/api/meta").json()
    assert len(m["sources"]) == 5 and len(m["fields"]) == 17


def test_promotion_matches_offline_grid():
    # khớp lưới mô phỏng đã tính offline: ngũ cốc, biên 30%, giảm 10%, có trưng bày → +35,5%
    r = c.post("/api/simulate/promotion", json={"category": "COLD CEREAL", "margin": 0.3, "cut": 0.1, "display": True,
                                                "feature": False, "rival_share": 0, "include_post": False}).json()
    assert abs(r["profit_change"] - 0.3547) < 1e-3
    assert len(r["curve"]) == 41
    assert c.post("/api/simulate/promotion", json={"category": "X"}).status_code == 422
    assert c.post("/api/simulate/promotion", json={"cut": 0.9}).status_code == 422


def test_price():
    r = c.post("/api/simulate/price", json={"source": "batf", "category": "FROZEN PIZZA", "change": 0.05}).json()
    assert r["units_change"] < -0.1 and r["revenue_change"] < 0
    r = c.post("/api/simulate/price", json={"source": "m5", "category": "FOODS", "change": 0.05}).json()
    assert r["revenue_change"] > 0  # ít co giãn → tăng giá tăng doanh thu


def test_explorer():
    o = c.get("/api/explorer/m5/options").json()
    assert len(o["stores"]) == 10 and len(o["depts"]) == 7
    r = c.get("/api/explorer/m5", params={"state": "WI", "cat": "FOODS", "freq": "day"}).json()
    assert r["snap"]["raw_lift"] > 0.1 and len(r["series"]) > 1800
    t = c.get("/api/explorer/m5", params={"freq": "month"}).json()
    assert abs(t["summary"]["units"] - 66927176) < 50  # float32 khi tổng hợp
    cj = c.get("/api/explorer/cj", params=[("department", "GROCERY"), ("department", "MEAT")]).json()
    assert len(cj["series"]) == 102 and len(cj["mix"]) == 2


def test_dashboard():
    p = c.get("/api/dashboard/periods").json()
    assert p["default"] == {"grain": "month", "key": "2016-04"} and "2015" in p["year"] and "2016-05" not in p["month"]
    d = c.get("/api/dashboard", params={"grain": "month", "key": "2016-04"}).json()
    assert len(d["stores"]) == 10 and d["kpis"]["stores"] == 10
    assert abs(sum(s["revenue"] for s in d["stores"]) - d["kpis"]["revenue"]["value"]) < 1
    assert abs(sum(x["revenue"] for x in d["depts"]) - d["kpis"]["revenue"]["value"]) < 1
    assert d["kpis"]["revenue"]["yoy"] is not None and d["news"]
    first = c.get("/api/dashboard", params={"grain": "month", "key": "2011-02"}).json()
    assert first["kpis"]["revenue"]["yoy"] is None
    assert c.get("/api/dashboard", params={"grain": "month", "key": "2030-01"}).status_code == 422
    one = c.get("/api/dashboard", params={"grain": "year", "key": "2015", "store": "TX_1"}).json()
    assert len(one["stores"]) == 1


def test_env_defaults():
    from app import config
    assert config.APP_ENV == "development" and config.ENABLE_DOCS
    assert c.get("/docs").status_code == 200
