import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { StockSearchService, StockInfo } from '../services/stock-search.service';

@Component({
  selector: 'app-home',
  standalone: false,
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home implements OnInit {
  searchQuery: string = '';
  popularStocks: StockInfo[] = [];
  
  constructor(
    private router: Router,
    private stockSearchService: StockSearchService
  ) {}

  ngOnInit() {
    this.popularStocks = this.stockSearchService.getPopularStocks();
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

  selectPopularStock(stock: StockInfo) {
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