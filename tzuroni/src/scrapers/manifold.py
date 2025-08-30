import requests
from typing import List, Optional
from ..types import SiteMarket


API_URL = "https://manifold.markets/api/v0/markets"


def fetch_manifold(limit: int = 200, proxy: Optional[str] = None) -> List[SiteMarket]:
	params = {"limit": limit}
	proxies = {"http": proxy, "https": proxy} if proxy else None
	r = requests.get(API_URL, params=params, proxies=proxies, timeout=30)
	r.raise_for_status()
	data = r.json()
	markets = []
	for item in data:
		mid = str(item.get("id"))
		title = item.get("question") or item.get("slug") or ""
		url = f"https://manifold.markets/{item.get('creatorUsername')}/{item.get('slug')}" if item.get("slug") else None
		prob = item.get("probability")
		price = float(prob) if isinstance(prob, (int, float)) else None
		markets.append(
			SiteMarket(
				site="manifold",
				id=mid,
				title=title,
				price=price,
				url=url,
				additional={"raw": item},
			)
		)
	return markets
