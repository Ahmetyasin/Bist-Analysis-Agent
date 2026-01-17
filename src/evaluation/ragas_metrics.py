"""RAGAS-based evaluation metrics."""
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


class RAGASEvaluator:
    """Evaluate RAG quality using RAGAS-style metrics."""

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
        contexts: List[str],
        ground_truth: str = None
    ) -> Dict[str, float]:
        """
        Compute RAGAS metrics.

        Args:
            query: User question
            response: Generated answer
            contexts: Retrieved context passages
            ground_truth: Optional expected answer

        Returns:
            Dictionary of metric scores
        """
        results = {}

        # Faithfulness: Is the answer grounded in context?
        results["faithfulness"] = self._compute_faithfulness(response, contexts)

        # Answer Relevancy: Is the answer relevant to the question?
        results["answer_relevancy"] = self._compute_answer_relevancy(query, response)

        # Context Precision: Are retrieved contexts relevant?
        results["context_precision"] = self._compute_context_precision(query, contexts)

        # Context Recall: Did we retrieve all needed info?
        if ground_truth:
            results["context_recall"] = self._compute_context_recall(ground_truth, contexts)

        return results

    def _compute_faithfulness(self, response: str, contexts: List[str]) -> float:
        """Check if response claims are supported by context."""
        if not contexts:
            return 0.0

        context_str = "\n\n".join(contexts[:5])  # Limit context

        prompt = f"""Verilen yanittaki iddialarin kaynaklar tarafindan desteklenip desteklenmedigini degerlendir.

Yanit:
{response[:1500]}

Kaynaklar:
{context_str[:2000]}

Her iddiayi kontrol et ve 0-1 arasi bir puan ver:
- 1.0: Tum iddialar kaynaklarda destekleniyor
- 0.5: Bazi iddialar destekleniyor, bazilari belirsiz
- 0.0: Iddialar kaynaklarda desteklenmiyor

Sadece sayisal puani ver (0 ile 1 arasi ondalikli sayi):"""

        try:
            result = self.llm.invoke(prompt)
            score = float(result.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5

    def _compute_answer_relevancy(self, query: str, response: str) -> float:
        """Check if answer is relevant to query."""
        prompt = f"""Verilen yanitin soruyla ne kadar alakali oldugunu degerlendir.

Soru: {query}

Yanit: {response[:1500]}

Alaka duzeyini 0-1 arasi puanla:
- 1.0: Yanit soruyu tam olarak cevapliyor
- 0.5: Yanit kismen alakali
- 0.0: Yanit alakasiz

Sadece sayisal puani ver:"""

        try:
            result = self.llm.invoke(prompt)
            score = float(result.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5

    def _compute_context_precision(self, query: str, contexts: List[str]) -> float:
        """Check if retrieved contexts are relevant to query."""
        if not contexts:
            return 0.0

        relevant_count = 0
        for ctx in contexts[:5]:
            prompt = f"""Bu metin verilen soruyla alakali mi?

Soru: {query}

Metin: {ctx[:500]}

Sadece 'Evet' veya 'Hayir' yaz:"""

            try:
                result = self.llm.invoke(prompt)
                if "evet" in result.content.lower():
                    relevant_count += 1
            except:
                pass

        return relevant_count / min(len(contexts), 5)

    def _compute_context_recall(self, ground_truth: str, contexts: List[str]) -> float:
        """Check if contexts contain info needed to answer."""
        if not contexts:
            return 0.0

        context_str = "\n\n".join(contexts[:5])

        prompt = f"""Beklenen cevaptaki bilgilerin kaynaklarda bulunup bulunmadigini degerlendir.

Beklenen Cevap: {ground_truth[:500]}

Kaynaklar: {context_str[:2000]}

Bilgilerin ne kadarinin kaynaklarda bulundugunu 0-1 arasi puanla:
Sadece sayisal puani ver:"""

        try:
            result = self.llm.invoke(prompt)
            score = float(result.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5
