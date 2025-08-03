import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map, BehaviorSubject, timeout, catchError, of } from 'rxjs';
import { 
  ApiResponse, 
  StockDataResponse, 
  OptionsDataResponse, 
  SearchResponse, 
  StockNamesResponse 
} from '../models/stock-data.interface';

export interface TopPerformingStock {
  symbol: string;
  name: string;
  currentPrice: number;
  previousClose: number;
  change: number;
  changePercent: number;
}

@Injectable({
  providedIn: 'root'
})
export class StockDataService {
  private readonly API_BASE_URL = 'http://localhost:8006';
  private cachedTopStocks: TopPerformingStock[] = [];
  private isDataLoaded = false;
  private isLoading = false;
  private topStocksSubject = new BehaviorSubject<TopPerformingStock[]>([]);

  constructor(private http: HttpClient) {}

  /**
   * Get all stock data with timeout
   */
  getAllStockData(): Observable<ApiResponse<StockDataResponse>> {
    return this.http.get<ApiResponse<StockDataResponse>>(`${this.API_BASE_URL}/api/stock-data/`);
  }

  /**
   * Get all stock data with timeout (for background loading only)
   */
  getAllStockDataWithTimeout(): Observable<ApiResponse<StockDataResponse>> {
    return this.http.get<ApiResponse<StockDataResponse>>(`${this.API_BASE_URL}/api/stock-data/`)
      .pipe(
        timeout(5000), // 5 second timeout
        catchError(error => {
          console.error('API timeout or error:', error);
          return of({ 
            status: 'error', 
            data: { stock_data: [], total_db1_rows: 0 }, 
            message: 'Request timeout' 
          } as ApiResponse<StockDataResponse>);
        })
      );
  }

  /**
   * Get top 8 performing stocks with caching
   */
  getTopPerformingStocks(): Observable<TopPerformingStock[]> {
    // If data is already loaded, return cached data immediately
    if (this.isDataLoaded && this.cachedTopStocks.length > 0) {
      return new Observable(observer => {
        observer.next(this.cachedTopStocks);
        observer.complete();
      });
    }

    // If already loading, return the subject
    if (this.isLoading) {
      return this.topStocksSubject.asObservable();
    }

    // Start loading
    this.isLoading = true;
    
    return this.getAllStockData().pipe(
      map(response => {
        if (response.status !== 'success' || !response.data.stock_data) {
          this.isLoading = false;
          return [];
        }

        const stockData = response.data.stock_data;
        const stockPerformanceMap = new Map<string, { 
          currentPrice: number, 
          previousClose: number, 
          change: number, 
          changePercent: number,
          latestDate: string 
        }>();

        // Group data by symbol and find the latest and previous day data
        stockData.forEach(stock => {
          const existing = stockPerformanceMap.get(stock.symbol);
          
          if (!existing || new Date(stock.date) > new Date(existing.latestDate)) {
            // Find previous day data for this stock
            const previousDayData = stockData.find(s => 
              s.symbol === stock.symbol && 
              s.date !== stock.date &&
              new Date(s.date) < new Date(stock.date)
            );

            if (stock.close && previousDayData?.close) {
              const change = stock.close - previousDayData.close;
              const changePercent = (change / previousDayData.close) * 100;
              
              stockPerformanceMap.set(stock.symbol, {
                currentPrice: stock.close,
                previousClose: previousDayData.close,
                change: change,
                changePercent: changePercent,
                latestDate: stock.date
              });
            }
          }
        });

        // Convert to array and sort by percentage change (descending)
        const topStocks = Array.from(stockPerformanceMap.entries())
          .map(([symbol, data]) => ({
            symbol,
            name: this.getStockName(symbol),
            currentPrice: data.currentPrice,
            previousClose: data.previousClose,
            change: data.change,
            changePercent: data.changePercent
          }))
          .sort((a, b) => b.changePercent - a.changePercent)
          .slice(0, 8);

        // Cache the data
        this.cachedTopStocks = topStocks;
        this.isDataLoaded = true;
        this.isLoading = false;
        
        // Update the subject
        this.topStocksSubject.next(topStocks);
        
        return topStocks;
      })
    );
  }

  /**
   * Clear cached data (useful for testing or when you want to refresh)
   */
  clearTopStocksCache(): void {
    this.cachedTopStocks = [];
    this.isDataLoaded = false;
    this.isLoading = false;
    this.topStocksSubject.next([]);
  }

  /**
   * Get cached top stocks without loading (for immediate access)
   */
  getCachedTopStocks(): TopPerformingStock[] {
    return this.cachedTopStocks;
  }

  /**
   * Check if data is loaded
   */
  isTopStocksLoaded(): boolean {
    return this.isDataLoaded;
  }

  /**
   * Helper method to get stock name from symbol
   */
  private getStockName(symbol: string): string {
    // This is a simple mapping - you might want to enhance this
    const stockNames: { [key: string]: string } = {
      'AAPL': 'Apple Inc.',
      'MSFT': 'Microsoft Corporation',
      'NVDA': 'NVIDIA Corporation',
      'AMZN': 'Amazon.com Inc.',
      'META': 'Meta Platforms Inc.',
      'GOOGL': 'Alphabet Inc.',
      'GOOG': 'Alphabet Inc.',
      'BRK-B': 'Berkshire Hathaway Inc.',
      'TSLA': 'Tesla Inc.',
      'JPM': 'JPMorgan Chase & Co.',
      'WMT': 'Walmart Inc.',
      'UNH': 'UnitedHealth Group Incorporated',
      'V': 'Visa Inc.',
      'MA': 'Mastercard Incorporated',
      'XOM': 'Exxon Mobil Corporation',
      'LLY': 'Eli Lilly and Company',
      'PG': 'Procter & Gamble Co.',
      'HD': 'The Home Depot Inc.',
      'KO': 'The Coca-Cola Company',
      'COST': 'Costco Wholesale Corporation',
      'ADBE': 'Adobe Inc.',
      'BAC': 'Bank of America Corp.',
      'PEP': 'PepsiCo Inc.',
      'CSCO': 'Cisco Systems Inc.',
      'NFLX': 'Netflix Inc.',
      'CRM': 'Salesforce Inc.',
      'ORCL': 'Oracle Corporation',
      'INTC': 'Intel Corporation',
      'AMD': 'Advanced Micro Devices Inc.',
      'TMO': 'Thermo Fisher Scientific Inc.',
      'MCD': 'McDonald\'s Corporation',
      'ABT': 'Abbott Laboratories',
      'CVX': 'Chevron Corporation',
      'DIS': 'The Walt Disney Company',
      'WFC': 'Wells Fargo & Company',
      'IBM': 'International Business Machines Corporation',
      'QCOM': 'QUALCOMM Incorporated',
      'CAT': 'Caterpillar Inc.',
      'GS': 'The Goldman Sachs Group Inc.',
      'AMGN': 'Amgen Inc.',
      'DHR': 'Danaher Corporation',
      'NKE': 'NIKE Inc.',
      'LOW': 'Lowe\'s Companies Inc.',
      'INTU': 'Intuit Inc.',
      'TXN': 'Texas Instruments Incorporated',
      'UPS': 'United Parcel Service Inc.',
      'CMCSA': 'Comcast Corporation',
      'SPGI': 'S&P Global Inc.',
      'HON': 'Honeywell International Inc.',
      'RTX': 'Raytheon Technologies Corporation',
      'BA': 'Boeing Company',
      'C': 'Citigroup Inc.',
      'PFE': 'Pfizer Inc.',
      'T': 'AT&T Inc.',
      'GE': 'General Electric Company',
      'MMM': '3M Company',
      'DE': 'Deere & Company',
      'LMT': 'Lockheed Martin Corporation',
      'SCHW': 'Charles Schwab Corporation',
      'MDT': 'Medtronic plc',
      'CB': 'Chubb Limited',
      'ELV': 'Elevance Health Inc.',
      'BLK': 'BlackRock Inc.',
      'AXP': 'American Express Company',
      'CI': 'Cigna Corporation',
      'SBUX': 'Starbucks Corporation',
      'BMY': 'Bristol-Myers Squibb Company',
      'GILD': 'Gilead Sciences Inc.',
      'SYK': 'Stryker Corporation',
      'ADP': 'Automatic Data Processing Inc.',
      'PLD': 'Prologis Inc.',
      'MMC': 'Marsh & McLennan Companies Inc.',
      'MO': 'Altria Group Inc.',
      'COP': 'ConocoPhillips',
      'TJX': 'The TJX Companies Inc.',
      'NEE': 'NextEra Energy Inc.',
      'SO': 'Southern Company',
      'DUK': 'Duke Energy Corporation',
      'ZTS': 'Zoetis Inc.',
      'EOG': 'EOG Resources Inc.',
      'SLB': 'Schlumberger Limited',
      'VRTX': 'Vertex Pharmaceuticals Incorporated',
      'REGN': 'Regeneron Pharmaceuticals Inc.',
      'BSX': 'Boston Scientific Corporation',
      'ADI': 'Analog Devices Inc.',
      'KLAC': 'KLA Corporation',
      'PANW': 'Palo Alto Networks Inc.',
      'AMAT': 'Applied Materials Inc.',
      'LRCX': 'Lam Research Corporation',
      'CSX': 'CSX Corporation',
      'NSC': 'Norfolk Southern Corporation',
      'ITW': 'Illinois Tool Works Inc.',
      'SHW': 'Sherwin-Williams Company',
      'EMR': 'Emerson Electric Co.',
      'AON': 'Aon plc',
      'FDX': 'FedEx Corporation',
      'ECL': 'Ecolab Inc.',
      'TGT': 'Target Corporation',
      'MCK': 'McKesson Corporation',
      'USB': 'U.S. Bancorp',
      'CME': 'CME Group Inc.',
      'PNC': 'PNC Financial Services Group Inc.',
      'MAR': 'Marriott International Inc.',
      'PH': 'Parker-Hannifin Corporation',
      'ROP': 'Roper Technologies Inc.',
      'MCO': 'Moody\'s Corporation',
      'AFL': 'Aflac Incorporated',
      'TRV': 'Travelers Companies Inc.',
      'PSX': 'Phillips 66',
      'OXY': 'Occidental Petroleum Corporation',
      'MET': 'MetLife Inc.',
      'AIG': 'American International Group Inc.',
      'EW': 'Edwards Lifesciences Corporation',
      'HUM': 'Humana Inc.',
      'D': 'Dominion Energy Inc.',
      'AEP': 'American Electric Power Company Inc.',
      'STZ': 'Constellation Brands Inc.',
      'KMB': 'Kimberly-Clark Corporation',
      'GIS': 'General Mills Inc.',
      'YUM': 'Yum! Brands Inc.'
    };

    return stockNames[symbol] || symbol;
  }

  /**
   * Get all options data (both put and call options)
   */
  getAllOptionsData(): Observable<ApiResponse<OptionsDataResponse>> {
    return this.http.get<ApiResponse<OptionsDataResponse>>(`${this.API_BASE_URL}/api/options-data/`);
  }

  /**
   * Get options data for a specific stock symbol
   */
  getOptionsDataBySymbol(symbol: string): Observable<ApiResponse<OptionsDataResponse>> {
    const params = new HttpParams().set('symbol', symbol.toUpperCase());
    return this.http.get<ApiResponse<OptionsDataResponse>>(`${this.API_BASE_URL}/api/options-data/`, { params });
  }

  /**
   * Search for stocks and their options by stock name
   */
  searchStock(stockName: string): Observable<ApiResponse<SearchResponse>> {
    const params = new HttpParams().set('stock_name', stockName);
    return this.http.get<ApiResponse<SearchResponse>>(`${this.API_BASE_URL}/api/search/`, { params });
  }

  /**
   * Get realtime intraday data for a specific stock
   */
  getRealtimeData(stockName: string): Observable<ApiResponse<SearchResponse>> {
    const params = new HttpParams().set('stock_name', stockName);
    return this.http.get<ApiResponse<SearchResponse>>(`${this.API_BASE_URL}/api/search/`, { params });
  }

  /**
   * Get stock names matching a pattern
   */
  getStockNames(stockName: string): Observable<ApiResponse<StockNamesResponse>> {
    const params = new HttpParams().set('stock_name', stockName);
    return this.http.get<ApiResponse<StockNamesResponse>>(`${this.API_BASE_URL}/api/stocknames/`, { params });
  }

  /**
   * Get stock data for a specific symbol
   */
  getStockDataBySymbol(symbol: string): Observable<ApiResponse<StockDataResponse>> {
    const params = new HttpParams().set('symbol', symbol.toUpperCase());
    return this.http.get<ApiResponse<StockDataResponse>>(`${this.API_BASE_URL}/api/stock-data/`, { params });
  }
}