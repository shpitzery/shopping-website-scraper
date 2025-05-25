SITES = [
    {
        "site_name": "Amazon.com",
        # "url_template": "https://www.amazon.com/s?k={query}",
        "url_template": "https://www.amazon.com/s?k={query}&ref=nb_sb_noss",
        "price_selector":"span.a-offscreen",
        "url_selector": "a.a-link-normal",
        "title_selector": "a[href] span",
        "img_selector": "img.s-image",
        "rating_selector": "span.a-icon-alt",
        "reviews_selector": "span.s-underline-text",
        "html_selector": "div[role='listitem']",
    },

    {
        "site_name": "BestBuy.com",
        # "url_template": "https://www.bestbuy.com/site/searchpage.jsp?st={query}",
        "url_template": "https://www.bestbuy.com/site/searchpage.jsp?st={query}&intl=nosplash",
        "price_selector": "div.pricing, .buying-option-link",
        "url_selector": "a[href]",
        "title_selector": "h2.product-title",
        "img_selector": ".product-image img",
        "rating_selector": ".ratings, .rnr-stats",
        "reviews_selector": "span.c-reviews, span.order-2",
        "html_selector": "li.product-list-item",
        "country_popup_selector": 'a[href*="intl=nosplash"]',
        "matched_selector": 
        [
            "li.product-list-item",
            "ul.plp-product-list",
            "div#main-results",
            ".columns"
        ],
    },

    {
        "site_name": "Walmart.com",
        # "url_template": "https://www.walmart.com/search?q={query}",
        "url_template": "https://www.walmart.com/search?q={query}&ref=nb_sb_noss",
        "price_selector": "div[data-automation-id='product-price'] span.w_iUH7",
        "url_selector": "a[href]",
        "title_selector": "a > span.w_iUH7",
        "img_selector": "div.relative img",
        "rating_selector": "span.w_iUH7",
        "reviews_selector": "span[data-testid='product-reviews']",
        "html_selector": "div[role='group']",
    },

    {
        "site_name": "Newegg.com",
        # "url_template": "https://www.newegg.com/p/pl?d={query}",
        "url_template": "https://www.newegg.com/p/pl?d={query}&intl=nosplash",
        "price_selector": "li.price-current",
        "url_selector": "a[href]",
        "title_selector": "a.item-title",
        "img_selector": "a[href] img",
        "rating_selector": "span.item-rating-num",
        "reviews_selector": "span.item333",
        "html_selector": "div.item-cell",
        "country_popup_selector": "button.button.button-m.bg-white",
        "matched_selector": [
            "div.item-cell",
            "div.item-cells-wrap",
            "div.list-wrap"
        ],
    }
]