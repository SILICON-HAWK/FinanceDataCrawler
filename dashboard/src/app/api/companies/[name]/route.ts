import { NextResponse } from 'next/server';
import { getCompanyByName, getCompanyRatios, getFinancialStatements } from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: { name: string } }
) {
  try {
    const decodedName = decodeURIComponent(params.name);
    const company = getCompanyByName(decodedName);

    if (!company) {
      return NextResponse.json({ error: 'Company not found' }, { status: 404 });
    }

    const ratios = getCompanyRatios(company.id);
    const statements = getFinancialStatements(company.id);

    // Parse financial statements JSON
    const financialData: any = {};
    statements.forEach(stmt => {
      try {
        financialData[stmt.statement_type] = JSON.parse(stmt.data);
      } catch (e) {
        console.error(`Error parsing ${stmt.statement_type}:`, e);
      }
    });

    return NextResponse.json({
      ...company,
      ratios,
      financial_data: financialData,
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Failed to fetch company data' }, { status: 500 });
  }
}
