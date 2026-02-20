import { format } from "date-fns";

/** "2025-02-20" → "2025/02/20" */
export function formatDate(dateStr: string): string {
  return format(new Date(dateStr), "yyyy/MM/dd");
}
