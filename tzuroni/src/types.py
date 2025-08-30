from typing import List, Optional
from pydantic import BaseModel, Field


class SiteMarket(BaseModel):
	site: str
	id: str
	title: str
	price: Optional[float] = Field(default=None, description="Probability/price in 0..1 if available")
	url: Optional[str] = None
	additional: dict = Field(default_factory=dict)


class UnifiedProduct(BaseModel):
	unified_title: str
	members: List[SiteMarket]
	confidence_scores: List[float]

	@property
	def average_confidence(self) -> float:
		if not self.confidence_scores:
			return 0.0
		return sum(self.confidence_scores) / len(self.confidence_scores)



