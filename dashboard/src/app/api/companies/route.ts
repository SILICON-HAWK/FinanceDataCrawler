import { NextResponse } from 'next/server';
import { getAllCompanies } from '@/lib/db';

export async function GET() {
  try {
    const companies = getAllCompanies();
    return NextResponse.json(companies);
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Failed to fetch companies' }, { status: 500 });
  }
}
