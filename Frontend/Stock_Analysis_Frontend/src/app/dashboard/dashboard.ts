import {
  Component,
  OnInit,
  AfterViewInit,
  ElementRef,
  ViewChild,
  OnDestroy,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import * as Highcharts from 'highcharts/highstock';
import { interval, Subscription } from 'rxjs';

import { StockDataService } from '../services/stock-data.service';
import { StockSearchService, StockInfo } from '../services/stock-search.service';
import { StockData } from '../models/stock-data.interface';

@Component({
  selector: 'app-dashboard',
  /* still part of an NgModule, so standalone stays false */
  standalone: false,
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
})
export class Dashboard implements OnInit, AfterViewInit, OnDestroy {
  /* ---------------- view state ---------------- */
  stockData: StockData[] = [];
  chartData: [number, number][] = [];

  isLoading = false;
  error: string | null = null;

  selectedStock = 'MMM';          // default symbol
  availableStocks: string[] = [];
  searchQuery: string = '';
  private requestedSymbol: string | null = null;
  private dataLoaded = false;

  selectedStrike: number | null = null;

  setSelectedStrike(strike: number) {
    this.selectedStrike = strike;
  }

  // --- Stock summary fields ---
  get stockSummary() {
    // Get all data for selected stock
    const stockRows = this.stockData.filter(i => i.symbol === this.selectedStock);
    if (!stockRows.length) return null;
    // Use the latest row for price, open, close, etc.
    const latest = stockRows[stockRows.length - 1];
    const previous = stockRows.length > 1 ? stockRows[stockRows.length - 2] : latest;
    return {
      symbol: latest.symbol,
      company: this.getCompanyName(latest.symbol),
      price: latest.close,
      previousClose: previous.close,
      open: latest.open,
      high: latest.high,
      low: latest.low,
      volume: latest.volume,
      marketCap: this.getMarketCap(latest.symbol),
      change: latest.close && previous.close ? (latest.close - previous.close) : 0,
      changePct: latest.close && previous.close ? ((latest.close - previous.close) / previous.close) * 100 : 0
    };
  }

  getCompanyName(symbol: string): string {
    const stockInfo = this.stockSearchService.getStockBySymbol(symbol);
    return stockInfo ? stockInfo.name : symbol;
  }

  getMarketCap(symbol: string): string {
    // Placeholder: Replace with real market cap if available
    return '$9.32B';
  }

  // --- Options data ---
  optionsData: any[] = [];

  // --- Options filters ---
  optionExpiryDates: string[] = [];
  selectedExpiry: string = '';
  optionViewType: 'List' | 'Straddle' = 'List';

  get filteredCalls() {
    return this.optionsData.filter(opt => opt.contractSymbol?.includes('C') && (!this.selectedExpiry || opt.expirationDate === this.selectedExpiry));
  }
  get filteredPuts() {
    return this.optionsData.filter(opt => opt.contractSymbol?.includes('P') && (!this.selectedExpiry || opt.expirationDate === this.selectedExpiry));
  }

  get sortedCalls() {
    return this.filteredCalls.slice().sort((a, b) => a.strike - b.strike);
  }
  get sortedPuts() {
    return this.filteredPuts.slice().sort((a, b) => a.strike - b.strike);
  }

  get straddleStrikes() {
    const callStrikes = this.filteredCalls.map(opt => opt.strike);
    const putStrikes = this.filteredPuts.map(opt => opt.strike);
    const allStrikes = Array.from(new Set([...callStrikes, ...putStrikes]));
    return allStrikes.sort((a, b) => a - b);
  }
  get straddleCallsMap() {
    const map = new Map<number, any>();
    for (const opt of this.filteredCalls) {
      map.set(opt.strike, opt);
    }
    return map;
  }
  get straddlePutsMap() {
    const map = new Map<number, any>();
    for (const opt of this.filteredPuts) {
      map.set(opt.strike, opt);
    }
    return map;
  }

  loadOptionsData() {
    this.stockDataService.getAllOptionsData().subscribe({
      next: (response) => {
        if (response.status === 'success') {
          const allOptions = [...response.data.call_options, ...response.data.put_options];
          
          // Filter options for the selected stock
          const selected = this.selectedStock.trim().toUpperCase();
          this.optionsData = allOptions.filter(opt => {
            const stockName = (opt.StockName || '').trim().toUpperCase();
            const contractSymbol = (opt.contractSymbol || '').trim().toUpperCase();
            return stockName === selected || contractSymbol.startsWith(selected);
          });
          
          // Extract unique expiry dates
          this.optionExpiryDates = Array.from(new Set(this.optionsData.map(opt => opt.expirationDate))).sort();
          
          // Default to first expiry if not set
          if (!this.selectedExpiry && this.optionExpiryDates.length > 0) {
            this.selectedExpiry = this.optionExpiryDates[0];
          }
          
          // If no options found, try to get options data specifically for this stock
          if (this.optionsData.length === 0) {
            this.loadOptionsDataForStock(this.selectedStock);
          }
        } else {
          this.optionsData = [];
          this.optionExpiryDates = [];
        }
      },
      error: (err) => {
        this.optionsData = [];
        this.optionExpiryDates = [];
      }
    });
  }

  loadOptionsDataForStock(symbol: string) {
    this.stockDataService.getOptionsDataBySymbol(symbol).subscribe({
      next: (response) => {
        if (response.status === 'success') {
          const allOptions = [...response.data.call_options, ...response.data.put_options];
          
          this.optionsData = allOptions;
          this.optionExpiryDates = Array.from(new Set(this.optionsData.map(opt => opt.expirationDate))).sort();
          
          if (!this.selectedExpiry && this.optionExpiryDates.length > 0) {
            this.selectedExpiry = this.optionExpiryDates[0];
          }
        } else {
          this.optionsData = [];
          this.optionExpiryDates = [];
        }
      },
      error: (err) => {
        this.optionsData = [];
        this.optionExpiryDates = [];
      }
    });
  }

  /* -------------- Realtime Data -------------- */
  realtimeData: StockData[] = [];
  realtimeChartData: [number, number][] = [];
  isRealtimeLoading = false;
  realtimeError: string | null = null;

  /* -------------- Highcharts refs -------------- */
  @ViewChild('chartContainer', { static: false })
  chartEl!: ElementRef<HTMLDivElement>;

  @ViewChild('realtimeChartContainer', { static: false })
  realtimeChartEl!: ElementRef<HTMLDivElement>;

  private chart?: Highcharts.Chart;
  private realtimeChart?: Highcharts.Chart;

  // Auto-reload functionality
  private realtimeAutoReloadSubscription?: Subscription;
  private optionsAutoReloadSubscription?: Subscription;
  private readonly AUTO_RELOAD_INTERVAL = 15 * 60 * 1000; // 15 minutes in milliseconds

  constructor(
    private stockDataService: StockDataService,
    private stockSearchService: StockSearchService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Listen for symbol changes in the URL
    this.route.queryParams.subscribe(params => {
      this.requestedSymbol = params['symbol'] || null;
      if (this.dataLoaded) {
        this.setSelectedStockAndUpdate();
      }
    });

    this.isLoading = true;
    this.error = null;
    
    this.stockDataService.getAllStockData().subscribe({
      next: (response) => {
        if (response.status === 'success') {
          this.stockData = response.data.stock_data;
          this.extractAvailableStocks();
          this.dataLoaded = true;
          this.setSelectedStockAndUpdate();
          
          // Start auto-reload timers
          this.startAutoReload();
        } else {
          this.error = response.message || 'Failed to load stock data';
        }
        this.isLoading = false;
      },
      error: (err) => {
        this.error =
          'Failed to connect to the API. Please check if the backend is running.';
        this.isLoading = false;
      },
    });
  }

  setSelectedStockAndUpdate(): void {
    if (this.requestedSymbol) {
      // First check if the symbol exists in available stocks (has data)
      if (this.availableStocks.includes(this.requestedSymbol)) {
        this.selectedStock = this.requestedSymbol;
        this.onStockChange(this.selectedStock);
      } else {
        // If not in available stocks, check if it's a valid stock symbol
        const stockInfo = this.stockSearchService.getStockBySymbol(this.requestedSymbol);
        if (stockInfo) {
          this.error = `Stock symbol "${this.requestedSymbol}" is valid but no data is available. Please try another stock.`;
        } else {
          this.error = `Stock symbol "${this.requestedSymbol}" not found.`;
        }
      }
    } else {
      this.selectedStock = this.availableStocks[0] || '';
      this.onStockChange(this.selectedStock);
    }
  }

  ngAfterViewInit(): void {
    if (this.chartData.length) {
      this.renderStockChart();
    }
  }

  extractAvailableStocks(): void {
    const uniqueStocks = [...new Set(this.stockData.map((i) => i.symbol))];
    this.availableStocks = uniqueStocks.sort();
  }

  onStockChange(selectedStock: string): void {
    this.isLoading = true;
    this.error = null; // Clear any previous errors
    this.selectedStock = selectedStock;
    this.updateChartData();
    
    // Update the URL with the new stock symbol
    this.updateUrl(selectedStock);
    
    // Use setTimeout to ensure the view is updated before rendering the chart
    setTimeout(() => {
      this.renderStockChart();
      this.loadOptionsData();
      this.loadRealtimeData();
    }, 0);
  }

  updateUrl(symbol: string): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { symbol: symbol },
      queryParamsHandling: 'merge'
    });
  }

  updateChartData(): void {
    const filtered = this.stockData
      .filter((i) => i.symbol === this.selectedStock)
      .sort(
        (a, b) =>
          new Date(a.date).getTime() - new Date(b.date).getTime()
      );

    this.chartData = filtered.map((i) => [
      new Date(i.date).getTime(),
      i.close ?? 0,
    ]);
  }

  loadRealtimeData(): void {
    this.isRealtimeLoading = true;
    this.realtimeError = null;
    
    this.stockDataService.getRealtimeData(this.selectedStock).subscribe({
      next: (response) => {
        if (response.status === 'success' && response.data.realtime_data) {
          // Get the most recent data for the selected stock
          const stockDataForSymbol = response.data.realtime_data
            .filter((item: any) => item.symbol === this.selectedStock)
            .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime());
          
          if (stockDataForSymbol.length > 0) {
            // Get the latest day's data
            const latestData = stockDataForSymbol[0];
            
            // Simulate intraday data points using OHLC values
            this.realtimeData = this.generateIntradayData(latestData);
            
            this.updateRealtimeChartData();
            
            setTimeout(() => {
              this.renderRealtimeChart();
            }, 0);
          } else {
            this.realtimeError = 'No data available for this stock';
          }
        } else {
          this.realtimeError = 'No realtime data available for this stock';
        }
        this.isRealtimeLoading = false;
      },
      error: (err) => {
        console.error('Error loading realtime data:', err);
        this.realtimeError = 'Failed to load realtime data';
        this.isRealtimeLoading = false;
      }
    });
  }

  updateRealtimeChartData(): void {
    this.realtimeChartData = this.realtimeData.map((i: any) => [
      i.timestamp,
      i.close ?? 0,
    ]);
  }

  generateIntradayData(dailyData: any): any[] {
    const baseDate = new Date(dailyData.date);
    const marketOpen = new Date(baseDate);
    marketOpen.setHours(9, 30, 0, 0); // 9:30 AM market open
    
    const marketClose = new Date(baseDate);
    marketClose.setHours(16, 0, 0, 0); // 4:00 PM market close
    
    const intradayPoints = [];
    const totalMinutes = (marketClose.getTime() - marketOpen.getTime()) / (1000 * 60);
    const intervalMinutes = 30; // 30-minute intervals
    const numPoints = Math.floor(totalMinutes / intervalMinutes);
    
    // Create intraday data points using OHLC values
    for (let i = 0; i <= numPoints; i++) {
      const timestamp = marketOpen.getTime() + (i * intervalMinutes * 60 * 1000);
      let price;
      
      if (i === 0) {
        price = dailyData.open;
      } else if (i === numPoints) {
        price = dailyData.close;
      } else {
        // Interpolate between open and close, with some variation using high/low
        const progress = i / numPoints;
        const basePrice = dailyData.open + (dailyData.close - dailyData.open) * progress;
        
        // Add some realistic variation using high/low bounds
        const variation = (Math.random() - 0.5) * 0.02; // ±1% variation
        price = Math.max(dailyData.low, Math.min(dailyData.high, basePrice * (1 + variation)));
      }
      
      intradayPoints.push({
        timestamp: timestamp,
        close: Number(price.toFixed(2)),
        symbol: dailyData.symbol,
        date: dailyData.date
      });
    }
    
    return intradayPoints;
  }

  renderStockChart(): void {
    /* guard against empty data or missing element */
    if (!this.chartEl) {
      this.isLoading = false;
      return;
    }

    /* destroy old chart when switching symbols */
    if (this.chart) {
      this.chart.destroy();
    }

    // If no chart data, just set loading to false and return
    if (!this.chartData.length) {
      this.isLoading = false;
      return;
    }

    try {
      this.chart = Highcharts.stockChart(this.chartEl.nativeElement, {
        chart: {
          type: 'areaspline',
          // backgroundColor: '#181A20', // match dark mode
          backgroundColor: '#020117'
        },
        title: {
          text: `${this.selectedStock} Stock Analysis`,
          style: { color: '#F5F6FA' },
        },
        rangeSelector: {
          selected: 2,
          buttons: [
            { type: 'day',    count: 5, text: '5D', title: 'View 5 days' },
            { type: 'month',  count: 1, text: '1m', title: 'View 1 month' },
            { type: 'month',  count: 3, text: '3m', title: 'View 3 months' },
            { type: 'month',  count: 6, text: '6m', title: 'View 6 months' },
            { type: 'ytd',                text: 'YTD', title: 'View year to date' },
            { type: 'year',   count: 1, text: '1y', title: 'View 1 year' },
            { type: 'all',                text: 'All', title: 'View all' },
          ],
          inputStyle: { color: '#F5F6FA', backgroundColor: '#23242B' },
          labelStyle: { color: '#F5F6FA' },
        },
        navigator : { enabled: false },
        scrollbar : { enabled: false },
        credits   : { enabled: false },
        accessibility: { enabled: false },
        yAxis: {
          opposite: false,
          title: { text: 'Price ($)', style: { color: '#F5F6FA' } },
          labels: { style: { color: '#F5F6FA' } },
          gridLineColor: '#23242B',
        },
        xAxis: { labels: { style: { color: '#F5F6FA' } }, gridLineColor: '#23242B' },
        series: [
          {
            type : 'areaspline',
            name : `${this.selectedStock} Price`,
            data : this.chartData,
            fillOpacity: 0.2,
            color: '#1D11F5', // pastel blue
            lineColor: '#1D11F5',
            marker: { fillColor: '#ffe066', lineColor: '#1D11F5', lineWidth: 2 }, // pastel yellow marker
            tooltip: { valueDecimals: 2, valuePrefix: '$' },
          },
        ],
      } as Highcharts.Options);
    } catch (error) {
      console.error('Error rendering chart:', error);
    }
    
    this.isLoading = false;
  }

  renderRealtimeChart(): void {
    /* guard against empty data or missing element */
    if (!this.realtimeChartEl) {
      this.isRealtimeLoading = false;
      return;
    }

    /* destroy old chart when switching symbols */
    if (this.realtimeChart) {
      this.realtimeChart.destroy();
    }

    // If no chart data, just set loading to false and return
    if (!this.realtimeChartData.length) {
      this.isRealtimeLoading = false;
      return;
    }

    try {
      this.realtimeChart = Highcharts.stockChart(this.realtimeChartEl.nativeElement, {
        chart: {
          type: 'line',
          backgroundColor: '#020117'
        },
        title: {
          text: `${this.selectedStock} Intraday Data (Latest Trading Day)`,
          style: { color: '#F5F6FA' },
        },
        rangeSelector: {
          enabled: false
        },
        navigator : { enabled: false },
        scrollbar : { enabled: false },
        credits   : { enabled: false },
        accessibility: { enabled: false },
        yAxis: {
          opposite: false,
          title: { text: 'Price ($)', style: { color: '#F5F6FA' } },
          labels: { style: { color: '#F5F6FA' } },
          gridLineColor: '#23242B',
        },
        xAxis: { 
          labels: { style: { color: '#F5F6FA' } }, 
          gridLineColor: '#23242B',
          type: 'datetime'
        },
        series: [
           {
             type : 'line',
             name : `${this.selectedStock} Realtime Price`,
             data : this.realtimeChartData,
             color: '#FF6B35', // orange color to differentiate from historical chart
             marker: { fillColor: '#FFE066', lineColor: '#FF6B35', lineWidth: 2 },
             tooltip: { valueDecimals: 2, valuePrefix: '$' },
           },
         ],
      } as Highcharts.Options);
    } catch (error) {
      console.error('Error rendering realtime chart:', error);
    }
    
    this.isRealtimeLoading = false;
  }

  searchStock(): void {
    if (this.searchQuery.trim()) {
      // Clear any previous errors at the start of a new search
      this.error = null;
      this.isLoading = true;
      
      // First try to find an exact match by symbol
      const exactMatch = this.stockSearchService.getStockBySymbol(this.searchQuery.trim());
      
      if (exactMatch) {
        // Check if the stock has data available
        if (this.availableStocks.includes(exactMatch.symbol)) {
          this.selectedStock = exactMatch.symbol;
          this.onStockChange(this.selectedStock);
          this.searchQuery = '';
        } else {
          this.error = `Stock symbol "${exactMatch.symbol}" is valid but no data is available. Please try another stock.`;
          this.isLoading = false;
        }
      } else {
        // If no exact match, search for the best match
        const searchResults = this.stockSearchService.searchStocks(this.searchQuery.trim());
        if (searchResults.length > 0) {
          const bestMatch = searchResults[0];
          if (this.availableStocks.includes(bestMatch.symbol)) {
            this.selectedStock = bestMatch.symbol;
            this.onStockChange(this.selectedStock);
            this.searchQuery = '';
          } else {
            this.error = `Stock symbol "${bestMatch.symbol}" is valid but no data is available. Please try another stock.`;
            this.isLoading = false;
          }
        } else {
          this.error = `No stock found matching "${this.searchQuery.trim()}".`;
          this.isLoading = false;
        }
      }
    }
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.searchStock();
    }
  }

  reloadData() {
    this.isLoading = true;
    this.error = null;
    this.stockDataService.getAllStockData().subscribe({
      next: (response) => {
        if (response.status === 'success') {
          this.stockData = response.data.stock_data;
          this.extractAvailableStocks();
          this.setSelectedStockAndUpdate();
        } else {
          this.error = response.message || 'Failed to load stock data';
        }
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to connect to the API. Please check if the backend is running.';
        this.isLoading = false;
      },
    });
  }

  startAutoReload(): void {
    // Auto-reload realtime data every 15 minutes
    this.realtimeAutoReloadSubscription = interval(this.AUTO_RELOAD_INTERVAL).subscribe(() => {
      this.loadRealtimeData();
    });

    // Auto-reload options data every 15 minutes
    this.optionsAutoReloadSubscription = interval(this.AUTO_RELOAD_INTERVAL).subscribe(() => {
      this.loadOptionsData();
    });
  }

  ngOnDestroy(): void {
    // Clean up subscriptions to prevent memory leaks
    if (this.realtimeAutoReloadSubscription) {
      this.realtimeAutoReloadSubscription.unsubscribe();
    }
    if (this.optionsAutoReloadSubscription) {
      this.optionsAutoReloadSubscription.unsubscribe();
    }
  }
}
