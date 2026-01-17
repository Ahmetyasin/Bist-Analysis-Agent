"""LLM-as-Judge evaluation."""
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


JUDGE_PROMPT = """Sen bir finansal analiz degerlendirmecisisin. Asagidaki hisse analiz raporunu degerlendir.

## Kullanici Sorusu
{query}

## Uretilen Analiz
{response}

## Kullanilan Kaynaklar
{sources}

## Degerlendirme Kriterleri (Her biri 1-5 arasi puanla)

### 1. Veri Dogrulugu (data_accuracy)
5: Tum finansal rakamlar dogru ve kaynaktan dogrulanabilir
4: Buyuk cogunluk dogru, kucuk eksiklikler
3: Cogu veri dogru, bazi hatalar var
2: Onemli hatalar mevcut
1: Ciddi veri hatalari, yanlis rakamlar

### 2. Analiz Kapsami (analysis_depth)
5: Makro, temel, teknik ve kurumsal gorusler tam dahil
4: 3-4 analiz boyutu kapsamli sekilde mevcut
3: En az 2 analiz boyutu yeterli derinlikte
2: Tek boyutlu veya yuzeysel analiz
1: Cok eksik veya yetersiz analiz

### 3. Muhakeme Kalitesi (reasoning_quality)
5: Veriden sonuca net mantik zinciri, alternatifler degerlendirilmis
4: Iyi muhakeme, kucuk eksiklikler
3: Temel muhakeme var ama bazi atlamalar mevcut
2: Zayif muhakeme, desteksiz iddialar
1: Sonuclar verilerle desteklenmiyor

### 4. Yatirimci Icin Fayda (investor_usefulness)
5: Karar vermeye yardimci somut, uygulanabilir icgoruler
4: Faydali bilgiler, bazi pratik oneriler
3: Genel bilgi var ama aksiyon belirsiz
2: Sinirli pratik deger
1: Yatirimciya katkisi minimal

### 5. Sunum Kalitesi (presentation_quality)
5: Net yapi, kolay okunur, profesyonel format
4: Iyi organize, kucuk format sorunlari
3: Anlasilir ama daginik
2: Takibi zor, duzensiz
1: Karmasik, okunamaz

## Yanit Formati
SADECE asagidaki JSON formatinda yanit ver, baska hicbir sey yazma:

{{
  "data_accuracy": {{"score": <1-5>, "reasoning": "<kisa aciklama>"}},
  "analysis_depth": {{"score": <1-5>, "reasoning": "<kisa aciklama>"}},
  "reasoning_quality": {{"score": <1-5>, "reasoning": "<kisa aciklama>"}},
  "investor_usefulness": {{"score": <1-5>, "reasoning": "<kisa aciklama>"}},
  "presentation_quality": {{"score": <1-5>, "reasoning": "<kisa aciklama>"}},
  "overall_score": <1-5 ortalamasi>,
  "strengths": ["<guclu yon 1>", "<guclu yon 2>"],
  "weaknesses": ["<zayif yon 1>", "<zayif yon 2>"]
}}"""


class LLMJudge:
    """LLM-based evaluation judge."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0
        )

    def evaluate(
        self,
        query: str,
        response: str,
        sources: str = "Kaynak bilgisi yok"
    ) -> Dict:
        """
        Evaluate response quality using LLM judge.

        Args:
            query: User question
            response: Generated response
            sources: Source information

        Returns:
            Evaluation results dictionary
        """
        prompt = JUDGE_PROMPT.format(
            query=query,
            response=response[:3000],
            sources=sources[:1500]
        )

        try:
            result = self.llm.invoke(prompt)

            # Parse JSON response
            content = result.content.strip()

            # Try to extract JSON from response
            if "{" in content:
                json_start = content.index("{")
                json_end = content.rindex("}") + 1
                json_str = content[json_start:json_end]
                scores = json.loads(json_str)
            else:
                scores = self._default_scores()

            # Validate and normalize scores
            return self._normalize_scores(scores)

        except Exception as e:
            print(f"Judge evaluation error: {e}")
            return self._default_scores()

    def _default_scores(self) -> Dict:
        """Return default scores when evaluation fails."""
        return {
            "data_accuracy": {"score": 3, "reasoning": "Degerlendirme yapilamadi"},
            "analysis_depth": {"score": 3, "reasoning": "Degerlendirme yapilamadi"},
            "reasoning_quality": {"score": 3, "reasoning": "Degerlendirme yapilamadi"},
            "investor_usefulness": {"score": 3, "reasoning": "Degerlendirme yapilamadi"},
            "presentation_quality": {"score": 3, "reasoning": "Degerlendirme yapilamadi"},
            "overall_score": 3.0,
            "strengths": [],
            "weaknesses": []
        }

    def _normalize_scores(self, scores: Dict) -> Dict:
        """Ensure scores are in valid range."""
        dimensions = ["data_accuracy", "analysis_depth", "reasoning_quality",
                      "investor_usefulness", "presentation_quality"]

        total = 0
        for dim in dimensions:
            if dim in scores:
                if isinstance(scores[dim], dict):
                    score = scores[dim].get("score", 3)
                else:
                    score = scores[dim]
                scores[dim] = {"score": max(1, min(5, int(score))),
                              "reasoning": scores[dim].get("reasoning", "") if isinstance(scores[dim], dict) else ""}
                total += scores[dim]["score"]
            else:
                scores[dim] = {"score": 3, "reasoning": ""}
                total += 3

        scores["overall_score"] = total / len(dimensions)

        if "strengths" not in scores:
            scores["strengths"] = []
        if "weaknesses" not in scores:
            scores["weaknesses"] = []

        return scores
