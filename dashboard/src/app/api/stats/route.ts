import { NextResponse } from 'next/server';
import { getDatabaseStats, getTopPerformers } from '@/lib/db';

export async function GET() {
  try {
    const stats = getDatabaseStats();
    const topPerformers = getTopPerformers(10);

    return NextResponse.json({
      ...stats,
      topPerformers,
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Failed to fetch stats' }, { status: 500 });
  }
}
