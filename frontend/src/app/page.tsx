import { ProductSearchForm } from "@/components/product-search-form"
import { ProductResults } from "@/components/product-results"

export default function Home() {
  return (
    <main className="container mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-8 text-center">Product Scraper</h1>
      <div className="max-w-3xl mx-auto">
        <ProductSearchForm />
        <ProductResults />
      </div>
    </main>
  )
}
