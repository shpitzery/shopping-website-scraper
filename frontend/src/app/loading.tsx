import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="container mx-auto py-10 px-4">
      <Skeleton className="h-10 w-64 mx-auto mb-8" />
      <div className="max-w-3xl mx-auto">
        <Skeleton className="h-[300px] w-full mb-8" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    </div>
  )
}
