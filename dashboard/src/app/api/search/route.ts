import { NextResponse } from 'next/server';
import { searchCompanies } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q') || '';

    if (query.length < 2) {
      return NextResponse.json([]);
    }

    const companies = searchCompanies(query);
    return NextResponse.json(companies);
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Search failed' }, { status: 500 });
  }
}
