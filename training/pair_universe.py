"""100+ trading pairs for rotating DogEye curriculum."""

# Deriv demo/public symbols (~100)
DERIV_PAIRS_100: tuple[str, ...] = (
    # Synthetic indices
    "R_10", "R_25", "R_50", "R_75", "R_100",
    "RDBULL", "RDBEAR", "BOOM1000", "BOOM500", "CRASH1000", "CRASH500",
    "JD10", "JD25", "JD50", "JD75", "JD100",
    "stpRNG", "stpRNG2", "stpRNG3", "stpRNG4", "stpRNG5",
    # Crypto
    "cryBTCUSD", "cryETHUSD", "cryLTCUSD", "cryBCHUSD", "cryXRPUSD",
    "cryXLMUSD", "cryADAUSD", "cryDOGUSD", "cryDOTUSD", "cryLNKUSD",
    "cryMIXUSD", "cryUNIUSD", "cryXMRUSD", "cryEOSUSD", "cryTRXUSD",
    # Forex majors + minors
    "frxEURUSD", "frxGBPUSD", "frxUSDJPY", "frxAUDUSD", "frxUSDCAD",
    "frxUSDCHF", "frxNZDUSD", "frxEURGBP", "frxEURJPY", "frxGBPJPY",
    "frxAUDJPY", "frxEURAUD", "frxEURCAD", "frxEURCHF", "frxGBPAUD",
    "frxGBPCAD", "frxGBPCHF", "frxAUDCAD", "frxAUDCHF", "frxCADCHF",
    "frxNZDJPY", "frxEURSEK", "frxEURNOK", "frxUSDSEK", "frxUSDNOK",
    "frxUSDMXN", "frxUSDPLN", "frxUSDZAR", "frxUSDSGD", "frxUSDHKD",
    # Metals & commodities (Deriv codes)
    "frxXAUUSD", "frxXAGUSD", "frxXPTUSD", "frxXPDUSD",
    # Extra synthetics / volatility
    "R_150", "R_200", "WLDAUD", "WLDEUR", "WLDGBP", "WLDUSD",
    "1HZ10V", "1HZ25V", "1HZ50V", "1HZ75V", "1HZ100V",
    # More crypto alts
    "cryBTCLTC", "cryETHBTC", "cryLTCBTC", "cryBCHBTC",
    "cryDSHUSD", "cryIOTUSD", "cryNEOUSD", "cryOMGUSD",
    "cryZECUSD", "cryALGUSD", "cryAVAXUSD", "crySOLUSD",
    "cryMATICUSD", "cryFTMUSD", "cryAPEUSD", "cryBNBUSD",
    "crySHIBUSD", "cryNEARUSD", "cryATOMUSD", "cryFILUSD",
    "cryETCUSD", "cryXTZUSD", "crySANDUSD", "cryMANAUSD",
)

# Binance USDT spot (~100) — testnet/mainnet ticker compatible
BINANCE_PAIRS_100: tuple[str, ...] = (
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
    "MATICUSDT", "LTCUSDT", "TRXUSDT", "SHIBUSDT", "ATOMUSDT",
    "UNIUSDT", "ETCUSDT", "XLMUSDT", "BCHUSDT", "FILUSDT",
    "NEARUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "INJUSDT",
    "SUIUSDT", "SEIUSDT", "TIAUSDT", "PEPEUSDT", "WIFUSDT",
    "FETUSDT", "RNDRUSDT", "GRTUSDT", "AAVEUSDT", "MKRUSDT",
    "SNXUSDT", "CRVUSDT", "LDOUSDT", "RUNEUSDT", "ICPUSDT",
    "ALGOUSDT", "VETUSDT", "HBARUSDT", "FTMUSDT", "SANDUSDT",
    "MANAUSDT", "AXSUSDT", "GALAUSDT", "ENJUSDT", "CHZUSDT",
    "THETAUSDT", "EOSUSDT", "XTZUSDT", "KAVAUSDT", "ZECUSDT",
    "DASHUSDT", "NEOUSDT", "IOTAUSDT", "EGLDUSDT", "FLOWUSDT",
    "MINAUSDT", "ROSEUSDT", "KSMUSDT", "WAVESUSDT", "ZILUSDT",
    "ONEUSDT", "CELOUSDT", "COMPUSDT", "YFIUSDT", "SUSHIUSDT",
    "1INCHUSDT", "BATUSDT", "ZRXUSDT", "ANKRUSDT", "SKLUSDT",
    "STXUSDT", "CFXUSDT", "JASMYUSDT", "GMTUSDT", "APEUSDT",
    "LRCUSDT", "IMXUSDT", "QNTUSDT", "DYDXUSDT", "GMXUSDT",
    "PENDLEUSDT", "JUPUSDT", "PYTHUSDT", "ONDOUSDT", "WLDUSDT",
    "ORDIUSDT", "BONKUSDT", "FLOKIUSDT", "CAKEUSDT", "XMRUSDT",
    "TONUSDT", "NOTUSDT", "PEOPLEUSDT", "BLURUSDT", "STRKUSDT",
)

BATCH_SIZE = 10


def batches(pairs: tuple[str, ...], size: int = BATCH_SIZE) -> list[tuple[str, ...]]:
    return [tuple(pairs[i : i + size]) for i in range(0, len(pairs), size)]


def batch_at(pairs: tuple[str, ...], index: int, size: int = BATCH_SIZE) -> tuple[str, ...]:
    all_batches = batches(pairs, size)
    if not all_batches:
        return ()
    return all_batches[index % len(all_batches)]
