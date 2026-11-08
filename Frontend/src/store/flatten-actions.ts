export function flattenActions<T extends object>(instance: T): Pick<T, keyof T> {
  const actions: Record<string, unknown> = {};
  const keys = new Set([...Object.keys(instance), ...Object.getOwnPropertyNames(Object.getPrototypeOf(instance))]);

  for (const key of keys) {
    if (key === "constructor") continue;
    const value = instance[key as keyof T];
    if (typeof value === "function") actions[key] = value.bind(instance);
  }

  return actions as Pick<T, keyof T>;
}
