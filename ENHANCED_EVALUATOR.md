# Enhanced Evaluator with Perplexity Integration

## Overview

The Enhanced Evaluator transforms HyperCog's assessment capability from a **static analyzer** into a **dynamic validator** by integrating real-time Perplexity verification for each assessment criterion.

## Architecture

### Components

1. **Enhanced Evaluator Agent** (`hypercog_mcp/agents/evaluator.py`)
   - Performs initial static assessment
   - Orchestrates Perplexity validations
   - Synthesizes final assessment from multiple sources

2. **Perplexity Agent** (`hypercog_mcp/sub_agents/perplexity/agent.py`)
   - Executes real-time web searches via Perplexity API
   - Returns answers with source citations
   - Validates technical claims

3. **Orchestrator Integration** (`hypercog_mcp/orchestrator.py`)
   - New method: `_run_evaluator_with_perplexity()`
   - Environment-based toggle for Perplexity validation
   - Enhanced logging of validation results

## How It Works

### 1. Initial Static Assessment

The Evaluator first performs a traditional assessment using only the extracted context:

```python
initial_assessment = await self._perform_static_assessment(
    session_context,
    attached_files,
    workspace_info,
    user_intent,
    current_prompt
)
```

This provides a baseline evaluation across the five criteria:
- Completeness
- Accuracy
- Relevance
- Depth
- Gotcha Insights

### 2. Perplexity Validation Phase

If enabled, the Evaluator calls Perplexity for each criterion that needs verification:

#### Completeness Validation
```python
query = f"What information and context is required to successfully {intent} for: {task}"
```

#### Accuracy Validation
```python
query = f"Verify current best practices and accuracy: {technical_claim}"
```

#### Relevance Validation
```python
query = f"Latest developments and current best practices in {domain} for: {task}"
```

#### Depth Validation (for complex tasks)
```python
query = f"Deep technical requirements, architecture considerations, and implementation details for {intent}: {task}"
```

#### Gotcha Insights (always checked)
```python
query = f"Common pitfalls, edge cases, security concerns, and gotchas when {intent}: {task}"
```

### 3. Synthesis

The Evaluator compares initial assessment against Perplexity findings:

```python
enhanced_assessment = await self._synthesize_assessment(
    initial_assessment,
    perplexity_validations
)
```

This produces:
- **Identified gaps** revealed by Perplexity but not in initial assessment
- **Confirmed/refuted accuracy** using Perplexity sources
- **New gotchas** and edge cases discovered
- **Adjusted confidence** based on external validation
- **Updated missing_elements** with verified gaps

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Perplexity API Key (required for enhanced validation)
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Enable/Disable Perplexity Validation (optional, default: true)
ENABLE_PERPLEXITY_VALIDATION=true
```

### Toggling Validation

Set `ENABLE_PERPLEXITY_VALIDATION=false` to:
- Use only static assessment (faster)
- Avoid Perplexity API costs
- Work without internet connectivity

Set `ENABLE_PERPLEXITY_VALIDATION=true` to:
- Enable real-time external validation
- Get verified, up-to-date assessments
- Discover edge cases and gotchas

## Benefits

### 1. Real Accuracy
Validates technical claims against current best practices, not just training data.

**Example**: Verifies if a library version mentioned is still current, or if a deprecated API is being used.

### 2. Gap Detection
Discovers missing information that wasn't obvious from static analysis.

**Example**: Identifies that implementing OAuth requires not just client credentials, but also redirect URI configuration and token refresh logic.

### 3. Up-to-Date Intelligence
Incorporates latest developments and changes in technologies.

**Example**: Detects that a framework has released a new major version with breaking changes.

### 4. Source Attribution
Provides citation URLs for all external validations.

**Example**: Links to official documentation, Stack Overflow discussions, or GitHub issues that informed the assessment.

### 5. Confidence Calibration
Adjusts confidence scores based on how well external validation confirms initial assessment.

**Example**: Lowers confidence if Perplexity findings contradict initial assessment, raises it if findings align.

## Output Format

### Enhanced Assessment Structure

```json
{
  "sufficient": false,
  "confidence": 0.7,
  "reasoning": "Initial assessment suggested context was sufficient, but Perplexity validation revealed missing OAuth refresh token implementation details and identified security gotchas with PKCE flow.",
  "missing_elements": [
    "OAuth refresh token implementation",
    "PKCE flow security configuration",
    "Token storage best practices"
  ],
  "context_size_assessment": "manageable",
  "external_validation_summary": "Perplexity validation identified 3 critical security considerations and 2 implementation gotchas not present in initial context. Current best practices require PKCE for public clients.",
  "perplexity_sources": [
    "https://oauth.net/2/pkce/",
    "https://datatracker.ietf.org/doc/html/rfc7636",
    "https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-pkce"
  ],
  "validation_confidence": 0.85
}
```

## Usage Example

The enhanced evaluator is automatically used in the orchestration flow:

```python
# In orchestrator.py
evaluation = await self._run_evaluator_with_perplexity(
    extraction_result,
    task="Implement OAuth authentication",
    current_context=session_context
)

if evaluation["sufficient"]:
    # Context is verified as sufficient
    proceed_with_execution()
else:
    # Context needs enrichment
    # Use Perplexity findings to guide search queries
    enrich_context(evaluation["missing_elements"])
```

## Performance Considerations

### Caching

The Evaluator implements validation caching to avoid duplicate Perplexity calls:

```python
self.validation_cache = {}  # Cache results by hash of claim
```

### Concurrency

All Perplexity validations run concurrently:

```python
validation_results = await asyncio.gather(
    *validation_tasks, 
    return_exceptions=True
)
```

### Rate Limiting

Limits validation to:
- Top 3 technical claims for accuracy validation
- Single query per criterion
- Cached results reused within session

## Error Handling

The enhanced evaluator gracefully degrades:

1. **Perplexity API unavailable**: Falls back to static assessment
2. **API key missing**: Logs warning, continues with static assessment
3. **Individual validation fails**: Continues with other validations
4. **Synthesis fails**: Returns initial assessment

```python
try:
    enhanced_assessment = await self._synthesize_assessment(
        initial_assessment,
        perplexity_validations
    )
    return enhanced_assessment
except Exception as e:
    self.log(f"Synthesis failed: {e}, using initial assessment", "WARNING")
    return initial_assessment
```

## Testing the Integration

### 1. Check Perplexity API Key

```bash
python -c "import os; print('PERPLEXITY_API_KEY:', 'SET' if os.getenv('PERPLEXITY_API_KEY') else 'NOT SET')"
```

### 2. Test Perplexity Agent

```python
from hypercog_mcp.sub_agents.perplexity.agent import PerplexityAgent

agent = PerplexityAgent()
result = await agent.search("What are the latest best practices for OAuth 2.0?")
print(result["answer"])
print(result["citations"])
```

### 3. Test Enhanced Evaluator

```python
from hypercog_mcp.agents.evaluator import EvaluatorAgent

evaluator = EvaluatorAgent(prompt_file, llm_client)
evaluation = await evaluator.evaluate(
    session_context="User wants to implement OAuth",
    attached_files=[],
    workspace_info=None,
    user_intent="implement authentication",
    current_prompt="Add OAuth 2.0 login",
    enable_perplexity=True
)

print(f"Sufficient: {evaluation['sufficient']}")
print(f"Confidence: {evaluation['confidence']}")
print(f"External validation: {evaluation.get('external_validation_summary', 'N/A')}")
```

## Migration Guide

### Existing Code

If you have existing code calling the old evaluator:

```python
# Old way
evaluation = await evaluator.execute({
    "task": task,
    "current_context": context,
    "metadata": metadata
})
```

This still works! The enhanced evaluator maintains backward compatibility through the `execute()` method.

### New Way (Recommended)

```python
# New way - more explicit control
evaluation = await evaluator.evaluate(
    session_context=context,
    attached_files=files,
    workspace_info=workspace,
    user_intent=intent,
    current_prompt=prompt,
    enable_perplexity=True  # or False for static only
)
```

## Troubleshooting

### Issue: "PERPLEXITY_API_KEY not found"

**Solution**: Add your API key to `.env`:
```bash
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxx
```

### Issue: Perplexity validation slow

**Solution**: Disable for faster assessment:
```bash
ENABLE_PERPLEXITY_VALIDATION=false
```

### Issue: Validation confidence always low

**Solution**: Check if Perplexity sources are being returned. May indicate API quota issues or network problems.

### Issue: Missing perplexity_sources in output

**Solution**: This is normal for static assessment mode. Enable Perplexity validation to get sources.

## Future Enhancements

1. **Smarter Caching**: Persist validation cache across sessions
2. **Selective Validation**: Only validate specific criteria based on task type
3. **Confidence Thresholds**: Auto-trigger Perplexity validation when static confidence is below threshold
4. **Validation History**: Track validation results over time for learning
5. **Custom Validators**: Allow domain-specific validation plugins

## References

- [Perplexity API Documentation](https://docs.perplexity.ai/)
- [HyperCog Orchestration Flowchart](./HyperCog%20MCP%20Orchestration%20Flowchart(1).md)
- [Evaluator Agent Prompt](./hypercog_mcp/agents/prompts/evaluator_agent.md)
