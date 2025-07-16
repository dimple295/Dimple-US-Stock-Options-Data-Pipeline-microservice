CREATE TABLE IF NOT EXISTS "StockData" (
    "StockName" VARCHAR(10),
    "Date" DATE,
    "Open" DOUBLE PRECISION,
    "High" DOUBLE PRECISION,
    "Low" DOUBLE PRECISION,
    "Close" DOUBLE PRECISION,
    "Volume" BIGINT,
    PRIMARY KEY ("StockName", "Date")
);

CREATE TABLE IF NOT EXISTS "call_options" (
    "contractSymbol" VARCHAR(50) NOT NULL,
    "lastTradeDate" TIMESTAMP NOT NULL,
    "expirationDate" DATE NOT NULL,
    "strike" DECIMAL(10,2) NOT NULL,
    "lastPrice" DECIMAL(10,2),
    "bid" DECIMAL(10,2),
    "ask" DECIMAL(10,2),
    "change" DECIMAL(10,2),
    "percentChange" DECIMAL(10,4),
    "volume" BIGINT,
    "openInterest" BIGINT,
    "impliedVolatility" DECIMAL(10,4),
    "inTheMoney" BOOLEAN,
    "contractSize" VARCHAR(20) NOT NULL,
    "currency" VARCHAR(3) NOT NULL,
    "StockName" VARCHAR(10) NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("contractSymbol", "lastTradeDate", "StockName", "expirationDate")
);

CREATE TABLE IF NOT EXISTS "put_options" (
    "contractSymbol" VARCHAR(50) NOT NULL,
    "lastTradeDate" TIMESTAMP NOT NULL,
    "expirationDate" DATE NOT NULL,
    "strike" DECIMAL(10,2) NOT NULL,
    "lastPrice" DECIMAL(10,2),
    "bid" DECIMAL(10,2),
    "ask" DECIMAL(10,2),
    "change" DECIMAL(10,2),
    "percentChange" DECIMAL(10,4),
    "volume" BIGINT,
    "openInterest" BIGINT,
    "impliedVolatility" DECIMAL(10,4),
    "inTheMoney" BOOLEAN,
    "contractSize" VARCHAR(20) NOT NULL,
    "currency" VARCHAR(3) NOT NULL,
    "StockName" VARCHAR(10) NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("contractSymbol", "lastTradeDate", "StockName", "expirationDate")
);