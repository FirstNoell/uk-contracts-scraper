import scrapy


class ContractsSpiderSpider(scrapy.Spider):
    name = "contracts_spider"
    allowed_domains = ["contractsfinder.service.gov.uk"]
    start_urls = [
        "https://www.contractsfinder.service.gov.uk/Search/Results"
    ]

    def parse(self, response):
        for contract in response.css("div.search-result"):
            # Title + Link
            title = contract.css("div.search-result-header h2 a::text").get(default="").strip()
            link = contract.css("div.search-result-header h2 a::attr(href)").get()

            # Buyer
            buyer = contract.css("div.search-result-sub-header::text").get(default="").strip()

            # ✅ Description fix: first wrap-text that is NOT buyer
            wrap_texts = [t.strip() for t in contract.css("div.wrap-text::text").getall() if t.strip()]
            description = ""
            for text in wrap_texts:
                if text != buyer:   # avoid duplicating buyer
                    description = text
                    break

            # Extract details
            closing_date, value, published_date = "", "", ""

            for entry in contract.css("div.search-result-entry"):
                label = entry.css("strong::text").get(default="").strip()
                text = entry.xpath("normalize-space(text())").get(default="").strip()

                if "Closing" in label:
                    closing_date = text
                elif "Contract value" in label:
                    value = text
                elif "Publication date" in label:
                    published_date = text

            yield {
                "title": title,
                "link": link,
                "buyer": buyer,
                "description": description,
                "closing_date": closing_date,
                "contract_value": value,
                "published_date": published_date,
            }

        # Pagination (absolute link)
        next_page = response.css("li.standard-paginate a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
