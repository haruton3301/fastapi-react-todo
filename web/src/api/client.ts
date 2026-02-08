const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const client = async <T>(
  url: string,
  init: RequestInit,
): Promise<T> => {
  const response = await fetch(`${BASE_URL}${url}`, init);

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
};

export default client;
