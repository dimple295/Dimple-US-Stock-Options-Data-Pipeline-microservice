import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { StockSearchService, StockInfo } from '../services/stock-search.service';
import { StockDataService, TopPerformingStock } from '../services/stock-data.service';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-home',
  standalone: false,
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home implements OnInit {
  searchQuery: string = '';
  popularStocks: TopPerformingStock[] = [];
  isLoading = true;
  error: string | null = null;
  
  constructor(
    private router: Router,
    private stockSearchService: StockSearchService,
    private stockDataService: StockDataService
  ) {}

  ngOnInit() {
    this.loadTopPerformingStocks();
  }

  loadTopPerformingStocks() {
    // Check if data is already cached
    if (this.stockDataService.isTopStocksLoaded()) {
      this.popularStocks = this.stockDataService.getCachedTopStocks();
      this.isLoading = false;
      return;
    }

    // Show loader initially
    this.isLoading = true;
    this.popularStocks = [];
    
    // Load dynamic data
    this.loadDynamicData();
  }

  private loadDynamicData() {
    // Use the timeout version for initial loading
    this.stockDataService.getAllStockDataWithTimeout().pipe(
      map(response => {
        if (response.status !== 'success' || !response.data.stock_data) {
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

        return topStocks;
      })
    ).subscribe({
      next: (stocks) => {
        this.isLoading = false;
        if (stocks.length > 0) {
          this.popularStocks = stocks;
          // Cache the data
          this.stockDataService['cachedTopStocks'] = stocks;
          this.stockDataService['isDataLoaded'] = true;
        } else {
          // Fallback to static data if no dynamic data available
          this.popularStocks = this.getStaticPopularStocks();
        }
      },
      error: (err) => {
        console.error('Error loading top performing stocks:', err);
        this.isLoading = false;
        this.error = 'Failed to load popular stocks';
        // Fallback to static data
        this.popularStocks = this.getStaticPopularStocks();
      }
    });
  }

  private getStaticPopularStocks(): TopPerformingStock[] {
    return [
      { symbol: 'AAPL', name: 'Apple Inc.', currentPrice: 185.06, previousClose: 173.54, change: 11.52, changePercent: 6.64 },
      { symbol: 'MSFT', name: 'Microsoft Corporation', currentPrice: 415.20, previousClose: 408.30, change: 6.90, changePercent: 1.69 },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', currentPrice: 185.06, previousClose: 173.54, change: 11.52, changePercent: 6.64 },
      { symbol: 'AMZN', name: 'Amazon.com Inc.', currentPrice: 175.35, previousClose: 168.20, change: 7.15, changePercent: 4.25 },
      { symbol: 'TSLA', name: 'Tesla Inc.', currentPrice: 245.20, previousClose: 229.90, change: 15.30, changePercent: 6.65 },
      { symbol: 'META', name: 'Meta Platforms Inc.', currentPrice: 485.58, previousClose: 475.20, change: 10.38, changePercent: 2.18 },
      { symbol: 'NVDA', name: 'NVIDIA Corporation', currentPrice: 890.15, previousClose: 844.90, change: 45.25, changePercent: 5.36 },
      { symbol: 'NFLX', name: 'Netflix Inc.', currentPrice: 612.45, previousClose: 598.30, change: 14.15, changePercent: 2.36 }
    ];
  }

  private getStockName(symbol: string): string {
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

  searchStock() {
    if (this.searchQuery.trim()) {
      // First try to find an exact match by symbol
      const exactMatch = this.stockSearchService.getStockBySymbol(this.searchQuery.trim());
      
      if (exactMatch) {
        this.router.navigate(['/dashboard'], { 
          queryParams: { symbol: exactMatch.symbol }
        });
      } else {
        // If no exact match, search for the best match
        const searchResults = this.stockSearchService.searchStocks(this.searchQuery.trim());
        const symbolToUse = searchResults.length > 0 ? searchResults[0].symbol : this.searchQuery.trim().toUpperCase();
        
        this.router.navigate(['/dashboard'], { 
          queryParams: { symbol: symbolToUse }
        });
      }
      
      this.clearSearch();
    }
  }

  selectPopularStock(stock: TopPerformingStock) {
    this.searchQuery = stock.symbol;
    this.router.navigate(['/dashboard'], { 
      queryParams: { symbol: stock.symbol }
    });
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.searchStock();
    }
  }

  clearSearch() {
    this.searchQuery = '';
  }
}