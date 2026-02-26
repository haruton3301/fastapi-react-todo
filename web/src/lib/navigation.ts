import { useLocation, useNavigate } from "@tanstack/react-router";

export function useBackWithFallback(fallback: string) {
  const { state } = useLocation();
  const navigate = useNavigate();

  return () => {
    const from = (state as { from?: string } | null)?.from;
    navigate({ href: from ?? fallback });
  };
}
