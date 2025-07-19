import { TestBed } from '@angular/core/testing';
import { StockSearchService, StockInfo } from './stock-search.service';

describe('StockSearchService', () => {
  let service: StockSearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StockSearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return exact symbol matches first', () => {
    const results = service.searchStocks('AAPL');
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].symbol).toBe('AAPL');
  });

  it('should find stocks by company name', () => {
    const results = service.searchStocks('Apple');
    expect(results.length).toBeGreaterThan(0);
    expect(results.some(stock => stock.symbol === 'AAPL')).toBe(true);
  });

  it('should find stocks by partial symbol', () => {
    const results = service.searchStocks('AAP');
    expect(results.length).toBeGreaterThan(0);
    expect(results.some(stock => stock.symbol === 'AAPL')).toBe(true);
  });

  it('should return empty array for empty query', () => {
    const results = service.searchStocks('');
    expect(results).toEqual([]);
  });

  it('should return empty array for whitespace query', () => {
    const results = service.searchStocks('   ');
    expect(results).toEqual([]);
  });

  it('should be case insensitive', () => {
    const results1 = service.searchStocks('aapl');
    const results2 = service.searchStocks('AAPL');
    expect(results1[0].symbol).toBe(results2[0].symbol);
  });

  it('should get stock by symbol', () => {
    const stock = service.getStockBySymbol('AAPL');
    expect(stock).toBeTruthy();
    expect(stock?.symbol).toBe('AAPL');
    expect(stock?.name).toBe('Apple Inc.');
  });

  it('should return undefined for non-existent symbol', () => {
    const stock = service.getStockBySymbol('NONEXISTENT');
    expect(stock).toBeUndefined();
  });

  it('should return popular stocks', () => {
    const popularStocks = service.getPopularStocks();
    expect(popularStocks.length).toBe(8);
    expect(popularStocks.some(stock => stock.symbol === 'AAPL')).toBe(true);
  });

  it('should limit results to 10', () => {
    const results = service.searchStocks('A');
    expect(results.length).toBeLessThanOrEqual(10);
  });

  it('should prioritize exact matches', () => {
    const results = service.searchStocks('MSFT');
    expect(results[0].symbol).toBe('MSFT');
  });
}); 