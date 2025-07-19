import { Injectable } from '@angular/core';

export interface StockInfo {
  symbol: string;
  name: string;
  aliases?: string[];
  sector?: string;
  industry?: string;
}

@Injectable({
  providedIn: 'root'
})
export class StockSearchService {
  private stockDatabase: StockInfo[] = [
    // Set 1
    { symbol: 'AAPL', name: 'Apple Inc.', aliases: ['apple', 'iphone', 'ipad', 'mac'] },
    { symbol: 'MSFT', name: 'Microsoft Corporation', aliases: ['microsoft', 'windows', 'office', 'azure'] },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', aliases: ['nvidia', 'gpu', 'graphics'] },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', aliases: ['amazon', 'aws', 'prime'] },
    { symbol: 'META', name: 'Meta Platforms Inc.', aliases: ['meta', 'facebook', 'instagram', 'whatsapp'] },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', aliases: ['google', 'alphabet', 'youtube', 'android'] },
    { symbol: 'GOOG', name: 'Alphabet Inc.', aliases: ['google', 'alphabet', 'youtube', 'android'] },
    { symbol: 'BRK-B', name: 'Berkshire Hathaway Inc.', aliases: ['berkshire', 'warren buffett'] },
    { symbol: 'TSLA', name: 'Tesla Inc.', aliases: ['tesla', 'electric cars', 'musk'] },
    { symbol: 'JPM', name: 'JPMorgan Chase & Co.', aliases: ['jpmorgan', 'chase', 'bank'] },
    { symbol: 'WMT', name: 'Walmart Inc.', aliases: ['walmart', 'wal-mart'] },
    { symbol: 'UNH', name: 'UnitedHealth Group Incorporated', aliases: ['unitedhealth', 'healthcare'] },
    { symbol: 'V', name: 'Visa Inc.', aliases: ['visa', 'credit card'] },
    { symbol: 'MA', name: 'Mastercard Incorporated', aliases: ['mastercard', 'credit card'] },
    { symbol: 'XOM', name: 'Exxon Mobil Corporation', aliases: ['exxon', 'mobil', 'oil'] },
    { symbol: 'LLY', name: 'Eli Lilly and Company', aliases: ['eli lilly', 'pharmaceuticals'] },
    { symbol: 'PG', name: 'Procter & Gamble Co.', aliases: ['procter', 'gamble', 'consumer goods'] },
    { symbol: 'HD', name: 'The Home Depot Inc.', aliases: ['home depot', 'hardware'] },
    { symbol: 'KO', name: 'The Coca-Cola Company', aliases: ['coca cola', 'coke', 'beverages'] },
    { symbol: 'COST', name: 'Costco Wholesale Corporation', aliases: ['costco', 'wholesale'] },
    { symbol: 'ADBE', name: 'Adobe Inc.', aliases: ['adobe', 'photoshop', 'creative'] },
    { symbol: 'BAC', name: 'Bank of America Corp.', aliases: ['bank of america', 'bofa'] },
    { symbol: 'PEP', name: 'PepsiCo Inc.', aliases: ['pepsi', 'beverages'] },
    { symbol: 'CSCO', name: 'Cisco Systems Inc.', aliases: ['cisco', 'networking'] },

    // Set 2
    { symbol: 'NFLX', name: 'Netflix Inc.', aliases: ['netflix', 'streaming'] },
    { symbol: 'CRM', name: 'Salesforce Inc.', aliases: ['salesforce', 'crm'] },
    { symbol: 'ORCL', name: 'Oracle Corporation', aliases: ['oracle', 'database'] },
    { symbol: 'INTC', name: 'Intel Corporation', aliases: ['intel', 'processors', 'chips'] },
    { symbol: 'AMD', name: 'Advanced Micro Devices Inc.', aliases: ['amd', 'processors', 'gpu'] },
    { symbol: 'TMO', name: 'Thermo Fisher Scientific Inc.', aliases: ['thermo fisher', 'scientific'] },
    { symbol: 'MCD', name: 'McDonald\'s Corporation', aliases: ['mcdonalds', 'fast food'] },
    { symbol: 'ABT', name: 'Abbott Laboratories', aliases: ['abbott', 'healthcare'] },
    { symbol: 'CVX', name: 'Chevron Corporation', aliases: ['chevron', 'oil'] },
    { symbol: 'DIS', name: 'The Walt Disney Company', aliases: ['disney', 'entertainment'] },
    { symbol: 'WFC', name: 'Wells Fargo & Company', aliases: ['wells fargo', 'bank'] },
    { symbol: 'IBM', name: 'International Business Machines Corporation', aliases: ['ibm', 'computers'] },
    { symbol: 'QCOM', name: 'QUALCOMM Incorporated', aliases: ['qualcomm', 'mobile chips'] },
    { symbol: 'CAT', name: 'Caterpillar Inc.', aliases: ['caterpillar', 'construction'] },
    { symbol: 'GS', name: 'The Goldman Sachs Group Inc.', aliases: ['goldman sachs', 'investment bank'] },
    { symbol: 'AMGN', name: 'Amgen Inc.', aliases: ['amgen', 'biotechnology'] },
    { symbol: 'DHR', name: 'Danaher Corporation', aliases: ['danaher', 'science'] },
    { symbol: 'NKE', name: 'NIKE Inc.', aliases: ['nike', 'athletic wear'] },
    { symbol: 'LOW', name: 'Lowe\'s Companies Inc.', aliases: ['lowes', 'hardware'] },
    { symbol: 'INTU', name: 'Intuit Inc.', aliases: ['intuit', 'quickbooks', 'turbotax'] },
    { symbol: 'TXN', name: 'Texas Instruments Incorporated', aliases: ['texas instruments', 'ti', 'semiconductors'] },
    { symbol: 'UPS', name: 'United Parcel Service Inc.', aliases: ['ups', 'shipping'] },
    { symbol: 'CMCSA', name: 'Comcast Corporation', aliases: ['comcast', 'cable'] },
    { symbol: 'SPGI', name: 'S&P Global Inc.', aliases: ['s&p global', 'ratings'] },

    // Set 3
    { symbol: 'HON', name: 'Honeywell International Inc.', aliases: ['honeywell', 'industrial'] },
    { symbol: 'RTX', name: 'Raytheon Technologies Corporation', aliases: ['raytheon', 'aerospace'] },
    { symbol: 'BA', name: 'Boeing Company', aliases: ['boeing', 'aircraft'] },
    { symbol: 'C', name: 'Citigroup Inc.', aliases: ['citigroup', 'citi', 'bank'] },
    { symbol: 'PFE', name: 'Pfizer Inc.', aliases: ['pfizer', 'pharmaceuticals'] },
    { symbol: 'T', name: 'AT&T Inc.', aliases: ['att', 'telecommunications'] },
    { symbol: 'GE', name: 'General Electric Company', aliases: ['general electric', 'industrial'] },
    { symbol: 'MMM', name: '3M Company', aliases: ['3m', 'industrial'] },
    { symbol: 'DE', name: 'Deere & Company', aliases: ['deere', 'john deere', 'agriculture'] },
    { symbol: 'LMT', name: 'Lockheed Martin Corporation', aliases: ['lockheed martin', 'aerospace'] },
    { symbol: 'SCHW', name: 'Charles Schwab Corporation', aliases: ['charles schwab', 'schwab', 'brokerage'] },
    { symbol: 'MDT', name: 'Medtronic plc', aliases: ['medtronic', 'medical devices'] },
    { symbol: 'CB', name: 'Chubb Limited', aliases: ['chubb', 'insurance'] },
    { symbol: 'ELV', name: 'Elevance Health Inc.', aliases: ['elevance health', 'anthem', 'healthcare'] },
    { symbol: 'BLK', name: 'BlackRock Inc.', aliases: ['blackrock', 'asset management'] },
    { symbol: 'AXP', name: 'American Express Company', aliases: ['american express', 'amex'] },
    { symbol: 'CI', name: 'Cigna Corporation', aliases: ['cigna', 'healthcare'] },
    { symbol: 'SBUX', name: 'Starbucks Corporation', aliases: ['starbucks', 'coffee'] },
    { symbol: 'BMY', name: 'Bristol-Myers Squibb Company', aliases: ['bristol myers', 'squibb', 'pharmaceuticals'] },
    { symbol: 'GILD', name: 'Gilead Sciences Inc.', aliases: ['gilead', 'biotechnology'] },
    { symbol: 'SYK', name: 'Stryker Corporation', aliases: ['stryker', 'medical devices'] },
    { symbol: 'ADP', name: 'Automatic Data Processing Inc.', aliases: ['adp', 'payroll'] },
    { symbol: 'PLD', name: 'Prologis Inc.', aliases: ['prologis', 'real estate'] },
    { symbol: 'MMC', name: 'Marsh & McLennan Companies Inc.', aliases: ['marsh', 'mclennan', 'insurance'] },

    // Set 4
    { symbol: 'MO', name: 'Altria Group Inc.', aliases: ['altria', 'tobacco'] },
    { symbol: 'COP', name: 'ConocoPhillips', aliases: ['conocophillips', 'oil'] },
    { symbol: 'TJX', name: 'The TJX Companies Inc.', aliases: ['tjx', 'tj maxx', 'retail'] },
    { symbol: 'NEE', name: 'NextEra Energy Inc.', aliases: ['nextera', 'energy'] },
    { symbol: 'SO', name: 'Southern Company', aliases: ['southern', 'utility'] },
    { symbol: 'DUK', name: 'Duke Energy Corporation', aliases: ['duke energy', 'utility'] },
    { symbol: 'ZTS', name: 'Zoetis Inc.', aliases: ['zoetis', 'animal health'] },
    { symbol: 'EOG', name: 'EOG Resources Inc.', aliases: ['eog', 'oil'] },
    { symbol: 'SLB', name: 'Schlumberger Limited', aliases: ['schlumberger', 'oil services'] },
    { symbol: 'VRTX', name: 'Vertex Pharmaceuticals Incorporated', aliases: ['vertex', 'biotechnology'] },
    { symbol: 'REGN', name: 'Regeneron Pharmaceuticals Inc.', aliases: ['regeneron', 'biotechnology'] },
    { symbol: 'BSX', name: 'Boston Scientific Corporation', aliases: ['boston scientific', 'medical devices'] },
    { symbol: 'ADI', name: 'Analog Devices Inc.', aliases: ['analog devices', 'semiconductors'] },
    { symbol: 'KLAC', name: 'KLA Corporation', aliases: ['kla', 'semiconductor equipment'] },
    { symbol: 'PANW', name: 'Palo Alto Networks Inc.', aliases: ['palo alto networks', 'cybersecurity'] },
    { symbol: 'AMAT', name: 'Applied Materials Inc.', aliases: ['applied materials', 'semiconductor equipment'] },
    { symbol: 'LRCX', name: 'Lam Research Corporation', aliases: ['lam research', 'semiconductor equipment'] },
    { symbol: 'CSX', name: 'CSX Corporation', aliases: ['csx', 'railroad'] },
    { symbol: 'NSC', name: 'Norfolk Southern Corporation', aliases: ['norfolk southern', 'railroad'] },
    { symbol: 'ITW', name: 'Illinois Tool Works Inc.', aliases: ['illinois tool works', 'industrial'] },
    { symbol: 'SHW', name: 'Sherwin-Williams Company', aliases: ['sherwin williams', 'paint'] },
    { symbol: 'EMR', name: 'Emerson Electric Co.', aliases: ['emerson', 'industrial'] },
    { symbol: 'AON', name: 'Aon plc', aliases: ['aon', 'insurance'] },
    { symbol: 'FDX', name: 'FedEx Corporation', aliases: ['fedex', 'shipping'] },

    // Set 5
    { symbol: 'ECL', name: 'Ecolab Inc.', aliases: ['ecolab', 'cleaning'] },
    { symbol: 'TGT', name: 'Target Corporation', aliases: ['target', 'retail'] },
    { symbol: 'MCK', name: 'McKesson Corporation', aliases: ['mckesson', 'healthcare distribution'] },
    { symbol: 'USB', name: 'U.S. Bancorp', aliases: ['us bancorp', 'bank'] },
    { symbol: 'CME', name: 'CME Group Inc.', aliases: ['cme group', 'futures exchange'] },
    { symbol: 'PNC', name: 'PNC Financial Services Group Inc.', aliases: ['pnc', 'bank'] },
    { symbol: 'MAR', name: 'Marriott International Inc.', aliases: ['marriott', 'hotels'] },
    { symbol: 'PH', name: 'Parker-Hannifin Corporation', aliases: ['parker hannifin', 'industrial'] },
    { symbol: 'ROP', name: 'Roper Technologies Inc.', aliases: ['roper', 'industrial'] },
    { symbol: 'MCO', name: 'Moody\'s Corporation', aliases: ['moodys', 'ratings'] },
    { symbol: 'AFL', name: 'Aflac Incorporated', aliases: ['aflac', 'insurance'] },
    { symbol: 'TRV', name: 'Travelers Companies Inc.', aliases: ['travelers', 'insurance'] },
    { symbol: 'PSX', name: 'Phillips 66', aliases: ['phillips 66', 'oil'] },
    { symbol: 'OXY', name: 'Occidental Petroleum Corporation', aliases: ['occidental', 'oil'] },
    { symbol: 'MET', name: 'MetLife Inc.', aliases: ['metlife', 'insurance'] },
    { symbol: 'AIG', name: 'American International Group Inc.', aliases: ['aig', 'insurance'] },
    { symbol: 'EW', name: 'Edwards Lifesciences Corporation', aliases: ['edwards lifesciences', 'medical devices'] },
    { symbol: 'HUM', name: 'Humana Inc.', aliases: ['humana', 'healthcare'] },
    { symbol: 'D', name: 'Dominion Energy Inc.', aliases: ['dominion', 'utility'] },
    { symbol: 'AEP', name: 'American Electric Power Company Inc.', aliases: ['american electric power', 'utility'] },
    { symbol: 'STZ', name: 'Constellation Brands Inc.', aliases: ['constellation brands', 'beverages'] },
    { symbol: 'KMB', name: 'Kimberly-Clark Corporation', aliases: ['kimberly clark', 'consumer goods'] },
    { symbol: 'GIS', name: 'General Mills Inc.', aliases: ['general mills', 'food'] },
    { symbol: 'YUM', name: 'Yum! Brands Inc.', aliases: ['yum brands', 'kfc', 'pizza hut', 'taco bell'] }
  ];

  constructor() {}

  searchStocks(query: string): StockInfo[] {
    if (!query || query.trim() === '') {
      return [];
    }

    const searchTerm = query.trim().toLowerCase();
    const results: StockInfo[] = [];
    
    // First, look for exact symbol matches (case-insensitive)
    const exactSymbolMatches = this.stockDatabase.filter(stock => 
      stock.symbol.toLowerCase() === searchTerm
    );
    results.push(...exactSymbolMatches);

    // Then, look for symbol starts with matches
    const symbolStartsWithMatches = this.stockDatabase.filter(stock => 
      stock.symbol.toLowerCase().startsWith(searchTerm) && 
      stock.symbol.toLowerCase() !== searchTerm
    );
    results.push(...symbolStartsWithMatches);

    // Then, look for name starts with matches
    const nameStartsWithMatches = this.stockDatabase.filter(stock => 
      stock.name.toLowerCase().startsWith(searchTerm) &&
      !results.some(r => r.symbol === stock.symbol)
    );
    results.push(...nameStartsWithMatches);

    // Then, look for alias matches
    const aliasMatches = this.stockDatabase.filter(stock => 
      stock.aliases && stock.aliases.some(alias => 
        alias.toLowerCase().includes(searchTerm)
      ) &&
      !results.some(r => r.symbol === stock.symbol)
    );
    results.push(...aliasMatches);

    // Finally, look for contains matches in both symbol and name
    const containsMatches = this.stockDatabase.filter(stock => 
      (stock.symbol.toLowerCase().includes(searchTerm) || 
       stock.name.toLowerCase().includes(searchTerm)) &&
      !results.some(r => r.symbol === stock.symbol)
    );
    results.push(...containsMatches);

    return results.slice(0, 10); // Limit to 10 results
  }

  getAllStocks(): StockInfo[] {
    return [...this.stockDatabase];
  }

  getStockBySymbol(symbol: string): StockInfo | undefined {
    return this.stockDatabase.find(stock => 
      stock.symbol.toLowerCase() === symbol.toLowerCase()
    );
  }

  getPopularStocks(): StockInfo[] {
    return [
      { symbol: 'AAPL', name: 'Apple Inc.' },
      { symbol: 'GOOGL', name: 'Alphabet Inc.' },
      { symbol: 'MSFT', name: 'Microsoft Corporation' },
      { symbol: 'AMZN', name: 'Amazon.com Inc.' },
      { symbol: 'TSLA', name: 'Tesla Inc.' },
      { symbol: 'META', name: 'Meta Platforms Inc.' },
      { symbol: 'NVDA', name: 'NVIDIA Corporation' },
      { symbol: 'NFLX', name: 'Netflix Inc.' }
    ];
  }

  // Helper method to get stock info for display
  getStockDisplayInfo(symbol: string): { symbol: string; name: string } | null {
    const stock = this.getStockBySymbol(symbol);
    return stock ? { symbol: stock.symbol, name: stock.name } : null;
  }
} 