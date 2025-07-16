import {
  Component,
  OnInit,
  AfterViewInit,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import * as Highcharts from 'highcharts/highstock';

import { StockDataService } from '../services/stock-data.service';
import { StockData } from '../models/stock-data.interface';

@Component({
  selector: 'app-dashboard',
  /* still part of an NgModule, so standalone stays false */
  standalone: false,
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
})
export class Dashboard implements OnInit, AfterViewInit {
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

  // Add mapping for symbol to company name
  popularStocks = [
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corporation' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.' },
    { symbol: 'TSLA', name: 'Tesla Inc.' },
    { symbol: 'META', name: 'Meta Platforms Inc.' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation' },
    { symbol: 'NFLX', name: 'Netflix Inc.' }
  ];

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
    const found = this.popularStocks?.find((s: {symbol: string, name: string}) => s.symbol === symbol);
    return found ? found.name : symbol;
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

  loadOptionsData() {
    this.stockDataService.getAllOptionsData().subscribe({
      next: (response) => {
        if (response.status === 'success') {
          const allOptions = [...response.data.call_options, ...response.data.put_options];
          this.optionsData = allOptions.filter(opt => opt.StockName === this.selectedStock);
          // Extract unique expiry dates
          this.optionExpiryDates = Array.from(new Set(this.optionsData.map(opt => opt.expirationDate))).sort();
          // Default to first expiry if not set
          if (!this.selectedExpiry && this.optionExpiryDates.length > 0) {
            this.selectedExpiry = this.optionExpiryDates[0];
          }
        } else {
          this.optionsData = [];
          this.optionExpiryDates = [];
        }
      },
      error: () => {
        this.optionsData = [];
        this.optionExpiryDates = [];
      }
    });
  }

  /* -------------- Highcharts refs -------------- */
  @ViewChild('chartContainer', { static: false })
  chartEl!: ElementRef<HTMLDivElement>;

  private chart?: Highcharts.Chart;

  constructor(
    private stockDataService: StockDataService,
    private route: ActivatedRoute
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
        } else {
          this.error = response.message || 'Failed to load stock data';
        }
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading stock data:', err);
        this.error =
          'Failed to connect to the API. Please check if the backend is running.';
        this.isLoading = false;
      },
    });
  }

  setSelectedStockAndUpdate(): void {
    if (this.requestedSymbol) {
      if (this.availableStocks.includes(this.requestedSymbol)) {
        this.selectedStock = this.requestedSymbol;
        this.onStockChange(this.selectedStock);
      } else {
        this.error = `Stock symbol "${this.requestedSymbol}" not found.`;
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
    this.selectedStock = selectedStock;
    this.updateChartData();
    this.renderStockChart();
    this.loadOptionsData();
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

  renderStockChart(): void {
    /* guard against empty data or missing element */
    if (!this.chartData.length || !this.chartEl) {
      this.isLoading = false;
      return;
    }

    /* destroy old chart when switching symbols */
    if (this.chart) {
      this.chart.destroy();
    }

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
        selected: 3,
        buttons: [
          { type: 'day',    count: 1, text: '1D', title: 'View 1 day' },
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
    this.isLoading = false;
  }

  searchStock(): void {
    if (this.searchQuery.trim()) {
      this.selectedStock = this.searchQuery.trim().toUpperCase();
      this.onStockChange(this.selectedStock);
      this.searchQuery = '';
    }
  }

  reloadData() {
    this.ngOnInit();
  }
}
