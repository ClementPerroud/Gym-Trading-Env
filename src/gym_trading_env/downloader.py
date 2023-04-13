import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import datetime
import numpy as np
import nest_asyncio
nest_asyncio.apply()

EXCHANGE_LIMIT_RATES = {
    "bitfinex2": {
        "limit":10_000,
        "pause_every": 1,
        "pause" : 3, #seconds
    },
    "binance": {
        "limit":1_000,
        "pause_every": 10,
        "pause" : 1, #seconds
    },
    "huobi": {
        "limit":1_000,
        "pause_every": 10,
        "pause" : 1, #seconds
    }
}

async def _ohlcv(exchange, symbol, timeframe, limit, step_since, timedelta):
    result = await exchange.fetch_ohlcv(symbol = symbol, timeframe= timeframe, limit= limit, since=step_since)
    result_df = pd.DataFrame(result, columns=["timestamp_open", "open", "high", "low", "close", "volume"])
    for col in ["open", "high", "low", "close", "volume"]:
        result_df[col] = pd.to_numeric(result_df[col])
    result_df["date_open"] = pd.to_datetime(result_df["timestamp_open"], unit= "ms")
    result_df["date_close"] = pd.to_datetime(result_df["timestamp_open"] + timedelta, unit= "ms")

    return result_df

async def _download_symbol(exchange, symbol, timeframe = '5m', since = int(datetime.datetime(year=2020, month= 1, day= 1).timestamp()*1E3), until = int(datetime.datetime.now().timestamp()*1E3), limit = 1000, pause_every = 10, pause = 1):
    timedelta = int(pd.Timedelta(timeframe).to_timedelta64()/1E6)
    tasks = []
    results = []
    for step_since in range(since, until, limit * timedelta):
        tasks.append(
            asyncio.create_task(_ohlcv(exchange, symbol, timeframe, limit, step_since, timedelta))
        )
        if len(tasks) >= pause_every:
            results.extend(await asyncio.gather(*tasks))
            await asyncio.sleep(pause)
            tasks = []
    if len(tasks) > 0 :
        results.extend(await asyncio.gather(*tasks))
    final_df = pd.concat(results, ignore_index= True)
    final_df = final_df.loc[(since < final_df["timestamp_open"]) & (final_df["timestamp_open"] < until), :]
    del final_df["timestamp_open"]
    final_df.set_index('date_open', drop=True, inplace=True)
    final_df.sort_index(inplace= True)
    final_df.dropna(inplace=True)
    final_df.drop_duplicates(inplace=True)
    return final_df

async def _download_symbols(exchange_name, symbols, dir, timeframe,  **kwargs):
    exchange = getattr(ccxt, exchange_name)({ 'enableRateLimit': True })
    for symbol in symbols:
        df = await _download_symbol(exchange = exchange, symbol = symbol, timeframe= timeframe, **kwargs)
        save_file = f"{dir}/{exchange_name}-{symbol.replace('/', '')}-{timeframe}.pkl"
        print(f"{symbol} downloaded from {exchange_name} and stored at {save_file}")
        df.to_pickle(save_file)
    await exchange.close()

async def _download(exchange_names, symbols, timeframe, dir, since : datetime.datetime, until : datetime.datetime = datetime.datetime.now()):
    tasks = []
    for exchange_name in exchange_names:
        
        limit = EXCHANGE_LIMIT_RATES[exchange_name]["limit"]
        pause_every = EXCHANGE_LIMIT_RATES[exchange_name]["pause_every"]
        pause = EXCHANGE_LIMIT_RATES[exchange_name]["pause"]
        tasks.append(
            _download_symbols(
                exchange_name = exchange_name, symbols= symbols, timeframe= timeframe, dir = dir,
                limit = limit, pause_every = pause_every, pause = pause,
                since = int(since.timestamp()*1E3), until = int(until.timestamp()*1E3)
            )
        )
    await asyncio.gather(*tasks)
def download(*args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _download(*args, **kwargs)
    )

async def main():
    await _download(
        ["binance", "bitfinex2", "huobi"],
        symbols= ["BTC/USDT", "ETH/USDT"],
        timeframe= "30m",
        dir = "test/data",
        since= datetime.datetime(year= 2019, month= 1, day=1),
    )



if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
