import type { StoreApi } from "zustand/vanilla";

export type StoreSetter<T> = StoreApi<T>["setState"];
