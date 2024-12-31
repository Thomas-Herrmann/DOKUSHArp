from typing import Iterable
from openai import OpenAI
import re


class GptTranslator:
    gpt_client : OpenAI

    def __init__(self):
        self.gpt_client = OpenAI()

    def translate(self, source_text : Iterable):
        response = self.gpt_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "When you are given a sequence of the form \"Japanese_text_1\",...,\"Japanese_text_n\" your response must be \"English_text_1\",...,\"English_text_n\" such that English_text_1 is the English translation of Japanese_text_1 and so forth. The texts/sentences are extracted from the same manga page, so the translations should be contextually alligned and represent the translated manga page. As such, when translating English_text_i you should also consider English_text_j for all j!=i."},
                {"role": "user", "content": ", ".join([f"\"{segment}\"" for segment in source_text])}
            ]
        )

        return re.findall(r'"([^"]*)"', response.choices[0].message.content)