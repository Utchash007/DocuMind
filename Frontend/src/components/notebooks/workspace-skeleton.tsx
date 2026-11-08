import { Skeleton } from "@/components/ui/skeleton";

export function WorkspaceSkeleton() {
  return <main id="main-content" aria-label="Loading notebook" className="flex h-dvh"><div className="hidden w-72 shrink-0 space-y-8 border-r bg-sidebar p-6 lg:block"><Skeleton className="h-9 w-36" /><Skeleton className="h-40 w-full" /><Skeleton className="h-28 w-full" /></div><div className="flex min-w-0 flex-1 flex-col"><div className="border-b p-6"><Skeleton className="h-7 w-52" /></div><div className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center gap-5 px-6"><Skeleton className="mx-auto size-14 rounded-2xl" /><Skeleton className="mx-auto h-10 w-3/4" /><Skeleton className="mx-auto h-5 w-1/2" /><div className="mt-4 grid grid-cols-2 gap-4"><Skeleton className="h-32 rounded-xl" /><Skeleton className="h-32 rounded-xl" /></div></div><Skeleton className="mx-auto mb-8 h-24 w-4/5 max-w-2xl rounded-2xl" /></div></main>;
}
