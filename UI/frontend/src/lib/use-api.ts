"use client";

import { useCallback, useEffect, useState } from "react";

// Oddiy hook: ma'lumotni yuklaydi, loading / error holatlarini beradi; reload() — qayta yuklash.
// deps o'zgarsa (masalan, boshqa hujjat tanlansa) ham qayta yuklanadi.
export function useApi<T>(load: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [version, setVersion] = useState(0);
  const key = JSON.stringify(deps);

  useEffect(() => {
    let alive = true;
    load()
      .then((result) => alive && (setData(result), setError(null)))
      .catch((err) => alive && setError(err instanceof Error ? err.message : String(err)))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, version]);

  const reload = useCallback(() => {
    setLoading(true);
    setVersion((v) => v + 1);
  }, []);

  return { data, error, loading, reload };
}
