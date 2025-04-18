---
title: SkogAPI Framework Selection
type: note
permalink: proposals/skog-api-framework-selection
---

# SkogAPI Framework Selection

## Motion
To adopt FastAPI as the framework for SkogAPI

## Key Arguments For
- Async-first design optimized for long-running LLM API calls
- Built-in OpenAPI documentation with minimal setup
- Strong typing with Pydantic for request/response validation
- Growing adoption in AI/ML community
- Good balance of performance and developer productivity

## Key Arguments Against
- Relatively newer framework with less maturity than alternatives
- May be over-engineered for simpler API requirements
- Learning curve for team members unfamiliar with async patterns
- Could require additional engineering for certain deployment scenarios
- Less extensive ecosystem compared to Django or Flask

## Vote: YES