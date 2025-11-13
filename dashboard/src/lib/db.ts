import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.join(process.cwd(), '..', 'finance_data.db');

let db: Database.Database | null = null;

export function getDb() {
  if (!db) {
    db = new Database(dbPath, { readonly: true });
  }
  return db;
}

export interface Company {
  id: number;
  company_name: string;
  url: string;
  stock_price: string;
  percentage_change: string;
  market_cap: string;
  about: string;
  created_at: string;
  updated_at: string;
}

export interface Ratio {
  id: number;
  company_id: number;
  ratio_name: string;
  ratio_value: string;
}

export interface FinancialStatement {
  id: number;
  company_id: number;
  statement_type: string;
  data: string;
}

export interface CrawlHistory {
  id: number;
  company_name: string;
  url: string;
  status: string;
  error_message: string | null;
  crawled_at: string;
}

export function getAllCompanies(): Company[] {
  try {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM companies ORDER BY company_name');
    return stmt.all() as Company[];
  } catch (error) {
    console.error('Error fetching companies:', error);
    return [];
  }
}

export function getCompanyByName(name: string): Company | null {
  try {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM companies WHERE company_name = ?');
    return stmt.get(name) as Company | null;
  } catch (error) {
    console.error('Error fetching company:', error);
    return null;
  }
}

export function getCompanyRatios(companyId: number): Ratio[] {
  try {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM ratios WHERE company_id = ?');
    return stmt.all(companyId) as Ratio[];
  } catch (error) {
    console.error('Error fetching ratios:', error);
    return [];
  }
}

export function getFinancialStatements(companyId: number): FinancialStatement[] {
  try {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM financial_statements WHERE company_id = ?');
    return stmt.all(companyId) as FinancialStatement[];
  } catch (error) {
    console.error('Error fetching financial statements:', error);
    return [];
  }
}

export function searchCompanies(query: string): Company[] {
  try {
    const db = getDb();
    const stmt = db.prepare(
      'SELECT * FROM companies WHERE company_name LIKE ? ORDER BY company_name LIMIT 20'
    );
    return stmt.all(`%${query}%`) as Company[];
  } catch (error) {
    console.error('Error searching companies:', error);
    return [];
  }
}

export function getDatabaseStats() {
  try {
    const db = getDb();

    const totalCompanies = db.prepare('SELECT COUNT(*) as count FROM companies').get() as { count: number };
    const successfulCrawls = db.prepare('SELECT COUNT(*) as count FROM crawl_history WHERE status = "success"').get() as { count: number };
    const failedCrawls = db.prepare('SELECT COUNT(*) as count FROM crawl_history WHERE status = "error"').get() as { count: number };
    const recentCompanies = db.prepare('SELECT company_name, created_at FROM companies ORDER BY created_at DESC LIMIT 5').all() as Company[];

    return {
      totalCompanies: totalCompanies.count,
      successfulCrawls: successfulCrawls.count,
      failedCrawls: failedCrawls.count,
      recentCompanies,
    };
  } catch (error) {
    console.error('Error fetching database stats:', error);
    return {
      totalCompanies: 0,
      successfulCrawls: 0,
      failedCrawls: 0,
      recentCompanies: [],
    };
  }
}

export function getTopPerformers(limit: number = 10) {
  try {
    const db = getDb();
    const stmt = db.prepare(`
      SELECT c.company_name, c.stock_price, c.percentage_change, c.market_cap
      FROM companies c
      WHERE c.percentage_change NOT LIKE '-%'
      ORDER BY CAST(REPLACE(REPLACE(c.percentage_change, '%', ''), '+', '') AS REAL) DESC
      LIMIT ?
    `);
    return stmt.all(limit) as Company[];
  } catch (error) {
    console.error('Error fetching top performers:', error);
    return [];
  }
}
