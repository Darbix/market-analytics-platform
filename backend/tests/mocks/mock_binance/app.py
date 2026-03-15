from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v3/klines")
def klines(symbol: str, interval: str, limit: int = 10):
    data = []

    base_price = 100

    for i in range(limit):
        price = base_price + i

        data.append([
            1700000000000 + i * 60000,
            str(price),
            str(price + 50),
            str(price - 50),
            str(price + 20),
            "1000",
            0,0,0,0,0,0
        ])

    return data
