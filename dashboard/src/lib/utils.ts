import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: string): string {
  // Already formatted from backend
  return value;
}

export function formatPercentage(value: string): string {
  return value;
}

export function parseNumericValue(value: string): number {
  // Remove commas, currency symbols, and other non-numeric characters
  const cleaned = value.replace(/[^0-9.-]/g, '');
  return parseFloat(cleaned) || 0;
}

export function getChangeColor(change: string): string {
  if (change.startsWith('-')) {
    return 'text-red-600';
  } else if (change.startsWith('+')) {
    return 'text-green-600';
  }
  return 'text-gray-600';
}

export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
}
