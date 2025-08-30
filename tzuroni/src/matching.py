from typing import List, Tuple
from rapidfuzz import fuzz
from .types import SiteMarket, UnifiedProduct


def normalize_title(title: str) -> str:
	t = title.lower().strip()
	for ch in ["?", "!", ",", ".", ":", ";", "(", ")", "[", "]"]:
		t = t.replace(ch, " ")
	while "  " in t:
		t = t.replace("  ", " ")
	return t


def similarity(a: str, b: str) -> float:
	return fuzz.token_set_ratio(normalize_title(a), normalize_title(b)) / 100.0


def cluster_markets(markets: List[SiteMarket], threshold: float = 0.78) -> List[UnifiedProduct]:
	clusters: List[List[Tuple[SiteMarket, float]]] = []
	for m in markets:
		placed = False
		for cluster in clusters:
			# compare to cluster centroid (first title)
			centroid_title = cluster[0][0].title
			score = similarity(m.title, centroid_title)
			if score >= threshold:
				cluster.append((m, score))
				placed = True
				break
		if not placed:
			clusters.append([(m, 1.0)])

	unified: List[UnifiedProduct] = []
	for cluster in clusters:
		titles = [cm.title for cm, _ in cluster]
		# choose representative title as longest/common
		rep = max(titles, key=len)
		unified.append(
			UnifiedProduct(
				unified_title=rep,
				members=[cm for cm, _ in cluster],
				confidence_scores=[sc for _, sc in cluster],
			)
		)
	return unified
