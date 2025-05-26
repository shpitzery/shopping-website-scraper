import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const product = searchParams.get("product")
  const method = searchParams.get("method")

  if (!product || !method) {
    return NextResponse.json({ error: "Product name and scraping method are required" }, { status: 400 })
  }

  try {
    // Use environment variable for backend URL
    const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:8000"

    // Map the frontend method names to your Python backend's expected parameter
    const methodMapping: Record<string, string> = {
      basic: "basic",
      llm: "llm",
      firecrawl: "firecrawl",
    }

    // Make request to your Python backend
    const backendMethod = methodMapping[method] || method
    const queryParam = encodeURIComponent(product)

    // Format the URL to match your FastAPI endpoint
    const url = `${PYTHON_BACKEND_URL}/scrape?button=${backendMethod}&query=${queryParam}`

    console.log(`Sending request to: ${url}`)

    // Create an AbortController with a timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 60000) // 60 second timeout

    const response = await fetch(url, {
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()

    // Transform the data to match the expected format in the frontend
    const formattedData = data.map((item: any) => ({
      website: item.name || "",
      title: item.title || "",
      price: item.price || "",
      image: item.image || "",
      rating: item.rating ? Number.parseFloat(item.rating) : null,
      reviews: item.reviews ? Number.parseInt(item.reviews, 10) : null,
      url: item.url || "",
    }))

    return NextResponse.json(formattedData)
  } catch (error: any) {
    if (error.name === "AbortError") {
      return NextResponse.json({ error: "Request was aborted" }, { status: 499 })
    }
    console.error("Error scraping product:", error)
    return NextResponse.json({ error: "Failed to scrape product information" }, { status: 500 })
  }
}
