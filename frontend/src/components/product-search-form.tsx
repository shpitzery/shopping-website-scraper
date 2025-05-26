"use client"

import type React from "react"
import { useState, useRef } from "react"
import { useRouter } from "next/navigation"

export function ProductSearchForm() {
  const [productName, setProductName] = useState("")
  const [scrapingMethod, setScrapingMethod] = useState("basic")
  const [isLoading, setIsLoading] = useState(false)
  const [showTooltip, setShowTooltip] = useState(false)
  const [showWarning, setShowWarning] = useState(false)
  const router = useRouter()
  const abortControllerRef = useRef<AbortController | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!productName.trim()) return

    // If already loading, abort the request
    if (isLoading && abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsLoading(false)
      return
    }

    setIsLoading(true)

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController()

    // Add the search parameters to the URL
    const params = new URLSearchParams()
    params.set("product", productName)
    params.set("method", scrapingMethod)

    router.push(`/?${params.toString()}`)

    // The actual scraping will be handled by the ProductResults component
    // We just need to keep the loading state here
  }

  const handleAbort = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsLoading(false)
    }
  }


  return (
    <form onSubmit={handleSubmit} className="space-y-6 mb-8 p-6 border rounded-lg shadow-sm bg-white">
      <div className="space-y-2">
        <label htmlFor="product-name" className="block text-sm font-medium text-gray-700">
          Product Name
        </label>
        <input
          id="product-name"
          type="text"
          placeholder="Enter product name..."
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">Scraping Method</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button
            type="button"
            className={`flex items-center justify-start h-16 px-4 border rounded-lg transition-all cursor-pointer hover:shadow-md ${
              scrapingMethod === "basic"
                ? "bg-green-600 text-white border-green-600"
                : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
            }`}
            onClick={() => setScrapingMethod("basic")}
            disabled={isLoading}
          >
            <div className="flex items-center">
              <div className="mr-3 flex items-center justify-center w-9 h-9 overflow-hidden">
                <img
                  src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/bot-icon.png-EUMa07kCtE9yv1jkNx4iCD4VmXNrOj.webp"
                  alt="Basic Scraping"
                  className="w-9 h-9 object-contain"
                />
              </div>
              <div className="text-left">
                <p className="font-medium">Basic Scraping</p>
                <p className="text-xs opacity-75">HTML parsing tools</p>
              </div>
            </div>
          </button>
          <button
            type="button"
            className={`flex items-center justify-start h-16 px-4 border rounded-lg transition-all cursor-pointer hover:shadow-md ${
              scrapingMethod === "llm"
                ? "bg-blue-600 text-white border-blue-600"
                : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
            }`}
            onClick={() => setScrapingMethod("llm")}
            disabled={isLoading}
          >
            <div className="flex items-center">
              <div className="mr-3 flex items-center justify-center w-9 h-9 overflow-hidden">
                <img
                  src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/llm-icon.png-uZCVhyzcmV7NQrzmqhOnNUoZ7IIwJs.jpeg"
                  alt="LLM Scraping"
                  className="w-9 h-9 object-contain"
                />
              </div>
              <div className="text-left">
                <p className="font-medium">LLM Scraping</p>
                <p className="text-xs opacity-75">AI-powered extraction</p>
              </div>
            </div>
          </button>
          <div className="relative">
            <button
              type="button"
              className={`flex items-center justify-start h-16 px-4 border rounded-lg transition-all w-full cursor-pointer hover:shadow-md ${
                scrapingMethod === "firecrawl"
                  ? "bg-orange-600 text-white border-orange-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
              onClick={() => setScrapingMethod("firecrawl")}
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
              disabled={isLoading}
            >
              <div className="flex items-center">
                <div className="mr-3 flex items-center justify-center w-9 h-9 overflow-hidden">
                  <img
                    src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/fire-iconn-0DDpQ9AJ7VTmDTA4NBpAiXLJoiTUKu.png"
                    alt="Firecrawl"
                    className="w-9 h-9 object-contain"
                  />
                </div>
                <div className="text-left">
                  <p className="font-medium">Firecrawl</p>
                  <p className="text-xs opacity-75">Advanced crawler</p>
                </div>
              </div>
            </button>
            {showTooltip && (
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap z-10">
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                  <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-gray-900"></div>
                </div>
                This process may take a while
              </div>
            )}
          </div>
        </div>
      </div>

      <button
        type={isLoading ? "button" : "submit"}
        onClick={isLoading ? handleAbort : undefined}
        className={`w-full py-2 px-4 font-medium rounded-lg transition-colors cursor-pointer hover:shadow-md ${
          isLoading ? "bg-red-600 text-white hover:bg-red-700" : "bg-blue-600 text-white hover:bg-blue-700"
        }`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Abort
          </span>
        ) : (
          "Scrape"
        )}
      </button>

      <div className="mt-4 flex justify-end">
        <div className="relative">
          <button
            type="button"
            className="p-1.5 text-amber-600 bg-amber-50 rounded-full border border-amber-200 cursor-pointer hover:bg-amber-100 transform -translate-y-1"
            onMouseEnter={() => setShowWarning(true)}
            onMouseLeave={() => setShowWarning(false)}
            aria-label="Show warning about web scraping"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </button>

          {showWarning && (
            <div className="absolute right-full top-1/3 mr-2 w-130 p-3 bg-amber-50 border border-amber-200 rounded-md shadow-md z-10 transform -translate-y-1/2">
                <div className="absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2 rotate-45 w-2 h-2 bg-amber-50 border-t border-r border-amber-200"></div>
                <p className="text-sm text-amber-800">
                    <span className="font-medium">Be aware:</span> Web scraping may not succeed due to site blocking, rate
                    limiting, or anti-bot measures. Some websites actively prevent automated data collection.
                </p>
            </div>
          )}
        </div>
      </div>
    </form>
  )
}
