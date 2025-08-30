import os
import requests
from typing import List, Optional
from ..types import SiteMarket


API_URL = "https://clob.polymarket.com/markets"


def fetch_polymarket(limit: int = 200, proxy: Optional[str] = None) -> List[SiteMarket]:
	params = {"limit": limit}
	proxies = {"http": proxy, "https": proxy} if proxy else None
	r = requests.get(API_URL, params=params, proxies=proxies, timeout=30)
	r.raise_for_status()
	data = r.json()
	markets = []
	for item in data:
		mid = str(item.get("id") or item.get("market_id") or item.get("question_id") or "")
		title = item.get("question") or item.get("title") or item.get("name") or ""
		url = item.get("url") or f"https://polymarket.com/market/{mid}" if mid else None
		price = None
		try:
			# Try best-effort: if last_price or implied probability exists
			price = item.get("last_price")
			if price is None:
				prob = item.get("impliedProbability") or item.get("implied_probability")
				if isinstance(prob, (int, float)):
					price = float(prob)
		except Exception:
			price = None
		markets.append(
			SiteMarket(
				site="polymarket",
				id=mid or title,
				title=title,
				price=price,
				url=url,
				additional={"raw": item},
			)
		)
	return markets
