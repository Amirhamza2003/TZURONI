import requests
from typing import List, Optional
from ..types import SiteMarket


API_URL = "https://www.predictit.org/api/marketdata/all"


def fetch_predictit(limit: int = 200, proxy: Optional[str] = None) -> List[SiteMarket]:
	proxies = {"http": proxy, "https": proxy} if proxy else None
	r = requests.get(API_URL, proxies=proxies, timeout=30)
	r.raise_for_status()
	data = r.json()
	markets = []
	for market in data.get("markets", [])[:limit]:
		mid = str(market.get("id"))
		title = market.get("name") or ""
		url = market.get("url") or f"https://www.predictit.org/markets/detail/{mid}"
		# Use best-contract price if available
		price = None
		contracts = market.get("contracts") or []
		if contracts:
			best = None
			for c in contracts:
				last = c.get("lastTradePrice")
				if isinstance(last, (int, float)):
					best = max(best, last) if best is not None else last
			price = best
		markets.append(
			SiteMarket(
				site="predictit",
				id=mid,
				title=title,
				price=price,
				url=url,
				additional={"raw": market},
			)
		)
	return markets
