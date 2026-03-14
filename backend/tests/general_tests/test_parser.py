from datetime import datetime

from app.services.price_data_service import parse_klines


def test_parse_klines():
    # Fields: [OT, OP, HP, LP, CP, V, CT, _, _, _, _, _]
    data = [[1000,1,2,0.5,1.5,10,2000,0,0,0,0,0]]

    rows = parse_klines("BTCUSDT","1m",data)

    assert rows[0] == {
        'symbol': 'BTCUSDT',
        'interval': '1m',
        'timestamp': datetime(1970, 1, 1, 1, 0, 1),
        'open': 1.0,
        'high': 2.0,
        'low': 0.5,
        'close': 1.5,
        'volume': 10.0
    }
