from my_comfy_wrapper.domain.lora import LoraEntry
from my_comfy_wrapper.services.prompt_service import PromptService


class FakeOllama:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def generate_text(self, model: str, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses.pop(0)


def test_prompt_service_two_pass_uses_lora_trigger_words():
    fake = FakeOllama(
        [
            '{"positive_prompt": "base positive", "negative_prompt": "base negative"}',
            '{"positive_prompt": "refined prompt", "negative_prompt": "refined negative"}',
        ]
    )
    service = PromptService(ollama=fake, model="dummy")

    positive, negative, metadata = service.generate_prompts(
        description="a person standing in a field",
        loras=[LoraEntry("x", 1.0, "cinematic lighting, flowing cloth", True)],
        action_hint="slow dolly in",
    )

    assert positive == "refined prompt"
    assert negative == "refined negative"
    assert "cinematic lighting, flowing cloth" in fake.calls[1]
    assert "slow dolly in" in fake.calls[1]
    assert "first_pass" in metadata
    assert "second_pass" in metadata
