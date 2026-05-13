import { readdirSync, readFileSync, existsSync } from 'fs';
import { resolve } from 'path';
import { json } from '@sveltejs/kit';

const companiesDir = process.env.COMPANIES_DIR || resolve(process.cwd(), '..', 'companies');

export function GET({ url }) {
  const name = url.searchParams.get('name');

  if (name) {
    const filePath = resolve(companiesDir, `${name}.json`);
    if (!existsSync(filePath)) {
      return json({ error: 'Company not found' }, { status: 404 });
    }
    return json(JSON.parse(readFileSync(filePath, 'utf-8')));
  }

  const files = readdirSync(companiesDir).filter(f => f.endsWith('.json'));
  const companies = files.map(f => {
    const d = JSON.parse(readFileSync(resolve(companiesDir, f), 'utf-8'));
    return {
      company_name: d.company_name || d.company_data?.company_name,
      stock_price: d.company_data?.stock_price,
      percentage_change: d.company_data?.percentage_change,
      ratios: d.company_data?.ratios
    };
  });

  return json(companies);
}
