"use client"

import { useEffect, useState, useRef } from "react"
import { useSearchParams } from "next/navigation"

interface ProductData {
  website: string
  title: string
  price: string
  image: string
  rating: number | null
  reviews: number | null
  url: string
}

export function ProductResults() {
  const searchParams = useSearchParams()
  const productName = searchParams.get("product")
  const scrapingMethod = searchParams.get("method")

  const [productData, setProductData] = useState<ProductData[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    async function fetchProductData() {
      if (!productName || !scrapingMethod) return

      // Abort any previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }

      // Create new AbortController for this request
      abortControllerRef.current = new AbortController()

      setIsLoading(true)
      setError(null)

      try {
        const response = await fetch(
          `/api/scrape?product=${encodeURIComponent(productName)}&method=${scrapingMethod}`,
          {
            signal: abortControllerRef.current.signal,
          },
        )

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`)
        }

        const data = await response.json()
        setProductData(Array.isArray(data) ? data : [data])
      } catch (err: any) {
        if (err.name === "AbortError") {
          console.log("Request was aborted")
          setError(null) // Don't show error for aborted requests
        } else {
          console.error("Failed to fetch product data:", err)
          setError("Failed to fetch product data. Please try again.")
        }
        setProductData([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchProductData()

    // Cleanup function to abort request if component unmounts
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [productName, scrapingMethod])

  if (!productName) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      {isLoading ? (
        <div className="space-y-4">
          <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
          <div className="h-64 bg-gray-200 rounded animate-pulse"></div>
        </div>
      ) : error ? (
        <div className="relative bg-red-50 border border-red-200 rounded-md p-4">
          <button
            onClick={() => setError(null)}
            className="absolute top-2 right-2 text-red-400 hover:text-red-600 cursor-pointer"
            aria-label="Close error message"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <p className="text-red-600 pr-8">{error}</p>
        </div>
      ) : productData.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2 font-medium">Website</th>
                <th className="text-left p-2 font-medium">Title</th>
                <th className="text-left p-2 font-medium">Price</th>
                <th className="text-left p-2 font-medium">Image</th>
                <th className="text-left p-2 font-medium">Rating</th>
                <th className="text-left p-2 font-medium">Reviews</th>
              </tr>
            </thead>
            <tbody>
              {productData.map((product, index) => (
                <tr key={index} className="border-b hover:bg-gray-50">
                  <td className="p-2">{product.website}</td>
                  <td className="p-2">
                    <a
                      href={product.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {product.title}
                    </a>
                  </td>
                  <td className="p-2">{product.price}</td>
                  <td className="p-2">
                    <div className="relative h-16 w-16">
                      <img
                        src={product.image || "/placeholder.svg"}
                        alt={product.title}
                        className="object-contain h-full w-full"
                      />
                    </div>
                  </td>
                  <td className="p-2">
                    {product.rating !== null ? (
                      <div className="flex items-center">
                        <span className="mr-1">{product.rating}</span>
                        <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      </div>
                    ) : (
                      "N/A"
                    )}
                  </td>
                  <td className="p-2">{product.reviews !== null ? product.reviews : "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : productName ? (
        <div className="text-center py-8 text-gray-500">No results found for "{productName}"</div>
      ) : null}
    </div>
  )
}
