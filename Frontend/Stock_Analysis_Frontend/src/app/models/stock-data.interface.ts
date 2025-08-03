export interface StockData {
  symbol: string;
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export interface OptionData {
  contractSymbol: string;
  lastTradeDate: string;
  expirationDate: string;
  strike: number | null;
  lastPrice: number | null;
  bid: number | null;
  ask: number | null;
  change: number | null;
  percentChange: number | null;
  volume: number | null;
  openInterest: number | null;
  impliedVolatility: number | null;
  inTheMoney: boolean | null;
  contractSize: string;
  currency: string;
  StockName: string;
}

export interface ApiResponse<T> {
  status: string;
  data: T;
  message?: string;
}

export interface StockDataResponse {
  stock_data: StockData[];
  total_db1_rows: number;
}

export interface OptionsDataResponse {
  put_options: OptionData[];
  call_options: OptionData[];
}

export interface SearchResponse {
  stock_data: StockData[];
  put_options: OptionData[];
  call_options: OptionData[];
  realtime_data: StockData[];
  total_stock_rows: number;
  total_put_rows: number;
  total_call_rows: number;
  total_realtime_rows: number;
}

export interface StockNamesResponse {
  stock_data: { stocknames: string }[];
  total_stock_rows: number;
}