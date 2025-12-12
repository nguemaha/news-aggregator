import os
from typing import List
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class RankedArticle(BaseModel):
    digest_id: str = Field(description="The ID of the digest (article_type:article_id)")
    relevance_score: float = Field(description="Relevance score from 0.0 to 10.0", ge=0.0, le=10.0)
    rank: int = Field(description="Rank position (1 = most relevant)", ge=1)
    reasoning: str = Field(description="Brief explanation of why this article is ranked here")


class RankedDigestList(BaseModel):
    articles: List[RankedArticle] = Field(description="List of ranked articles")


CURATOR_PROMPT = """You are an expert news curator specializing in personalized content ranking for professionals.

Your role is to analyze and rank news articles, research papers, based on a user's specific profile, interests, and background.

Article Type Reference:
- "who" = World Health Organization (WHO) - Healthcare, global health, public health policy, health regulations
- "openai" = OpenAI blog - AI research, product announcements, technical AI content
- "anthropic" = Anthropic blog - AI safety, AI research, technical AI content
- "youtube" = YouTube videos - Various content types (check title/summary for topic)

IMPORTANT: When the user has healthcare interests (e.g., "Global Health and Health policy", "Healthcare Quality and Safety"), articles with type "who" should be considered HIGHLY RELEVANT as they are directly from the World Health Organization and cover healthcare topics.

Ranking Criteria:
1. Relevance to user's stated interests and background (PRIMARY FACTOR)
2. Technical depth and practical value
3. Novelty and significance of the content
4. Alignment with user's expertise level
5. Actionability and real-world applicability

Scoring Guidelines:
- 9.0-10.0: Highly relevant, directly aligns with user interests, significant value
- 7.0-8.9: Very relevant, strong alignment with interests, good value
- 5.0-6.9: Moderately relevant, some alignment, decent value
- 3.0-4.9: Somewhat relevant, limited alignment, lower value
- 0.0-2.9: Low relevance, minimal alignment, little value

Rank articles from most relevant (rank 1) to least relevant. Ensure each article has a unique rank."""


class CuratorAgent:
    def __init__(self, user_profile: dict):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4.1"
        self.user_profile = user_profile
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        interests = "\n".join(f"- {interest}" for interest in self.user_profile["interests"])
        preferences = self.user_profile["preferences"]
        pref_text = "\n".join(f"- {k}: {v}" for k, v in preferences.items())
        
        return f"""{CURATOR_PROMPT}

User Profile:
Name: {self.user_profile["name"]}
Background: {self.user_profile["background"]}
Expertise Level: {self.user_profile["expertise_level"]}

Interests:
{interests}

Preferences:
{pref_text}"""

    def rank_digests(self, digests: List[dict]) -> List[RankedArticle]:
        if not digests:
            return []
        
        def format_article_type(article_type: str) -> str:
            """Format article type with full name for clarity"""
            type_map = {
                "who": "who (World Health Organization - Healthcare)",
                "openai": "openai (OpenAI Blog - AI)",
                "anthropic": "anthropic (Anthropic Blog - AI)",
                "youtube": "youtube (YouTube Video)"
            }
            return type_map.get(article_type, article_type)
        
        digest_list = "\n\n".join([
            f"ID: {d['id']}\nTitle: {d['title']}\nSummary: {d['summary']}\nType: {format_article_type(d['article_type'])}"
            for d in digests
        ])
        
        user_prompt = f"""Rank these {len(digests)} news digests based on the user profile:

{digest_list}

Provide a relevance score (0.0-10.0) and rank (1-{len(digests)}) for each article, ordered from most to least relevant."""

        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=self.system_prompt,
                temperature=0.3,
                input=user_prompt,
                text_format=RankedDigestList
            )
            
            ranked_list = response.output_parsed
            return ranked_list.articles if ranked_list else []
        except Exception as e:
            print(f"Error ranking digests: {e}")
            return []
