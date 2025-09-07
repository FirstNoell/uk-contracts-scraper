from itemadapter import ItemAdapter
from datetime import datetime
import re

class ContractsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Trim whitespace
        for field in adapter.field_names():
            if adapter.get(field) and isinstance(adapter.get(field), str):
                adapter[field] = adapter[field].strip()

        # Normalize published_date & closing_date → YYYY-MM-DD
        for date_field in ["published_date", "closing_date"]:
            raw_date = adapter.get(date_field)
            if raw_date:
                parsed_date = self.parse_date(raw_date)
                if parsed_date:
                    adapter[date_field] = parsed_date

        # Clean contract_value → numeric fields
        value = adapter.get("contract_value")
        if value:
            clean_value = value.replace(",", "").replace("£", "").strip()
            match = re.match(r"(\d+)\s*to\s*(\d+)", clean_value)
            if match:
                adapter["contract_value_min"] = int(match.group(1))
                adapter["contract_value_max"] = int(match.group(2))
            else:
                try:
                    adapter["contract_value_value"] = int(clean_value)
                except ValueError:
                    adapter["contract_value_value"] = clean_value

        return item

    def parse_date(self, raw_date):
        # Remove trailing text like ", 12pm"
        raw_date = raw_date.split(",")[0].strip()
        formats = ["%d %B %Y", "%d %b %Y", "%d/%m/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None
