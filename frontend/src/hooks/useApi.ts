import { useState, useCallback } from 'react';

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  retries?: number;
  retryDelay?: number;
}

interface UseApiResult<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T>(
  apiFunc: (...args: any[]) => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiResult<T> {
  const { onSuccess, onError, retries = 3, retryDelay = 1000 } = options;
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setIsLoading(true);
      setError(null);

      let lastError: Error | null = null;

      for (let attempt = 0; attempt <= retries; attempt++) {
        try {
          const result = await apiFunc(...args);
          setData(result);
          onSuccess?.(result);
          setIsLoading(false);
          return result;
        } catch (err) {
          lastError = err as Error;
          if (attempt < retries) {
            await new Promise((resolve) => setTimeout(resolve, retryDelay * (attempt + 1)));
          }
        }
      }

      setError(lastError);
      onError?.(lastError!);
      setIsLoading(false);
      return null;
    },
    [apiFunc, onSuccess, onError, retries, retryDelay]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return { data, error, isLoading, execute, reset };
}
