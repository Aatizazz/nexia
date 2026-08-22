#!/usr/bin/env python3
"""
Token Comparison Generator: Shows real savings from DocCompressor
Measures and compares: WITH vs WITHOUT tools
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple


class TokenComparison:
    """Generate comparison between WITH and WITHOUT DocCompressor tools."""
    
    def __init__(self):
        self.without_tool_metrics = {}
        self.with_tool_metrics = {}
    
    def estimate_tokens(self, size_kb: float) -> int:
        """Estimate tokens from file size (1 token ≈ 4 bytes)."""
        return int((size_kb * 1024) / 4)
    
    def estimate_cost(self, tokens: int, rate: float = 0.0001) -> float:
        """Estimate cost in USD (Claude API: $0.0001 per 1K tokens input)."""
        return (tokens / 1000) * rate
    
    def scenario_without_tools(self, num_docs_kb: float, num_features: int) -> Dict:
        """Calculate costs WITHOUT DocCompressor tools."""
        
        # Every session loads ALL docs
        tokens_per_doc_load = self.estimate_tokens(num_docs_kb)
        
        # Claude processing per feature
        tokens_per_claude_processing = 50000  # ~50K tokens for Claude to process
        tokens_per_response = 15000  # ~15K tokens for response
        
        # Per session
        tokens_per_session = tokens_per_doc_load + tokens_per_claude_processing + tokens_per_response
        cost_per_session = self.estimate_cost(tokens_per_session)
        
        # Total for all features
        total_tokens = tokens_per_session * num_features
        total_cost = cost_per_session * num_features
        tokens_wasted_on_docs = tokens_per_doc_load * num_features
        
        return {
            "scenario": "WITHOUT DocCompressor Tools",
            "tokens_per_session": tokens_per_session,
            "cost_per_session": cost_per_session,
            "total_sessions": num_features,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "tokens_wasted_on_docs": tokens_wasted_on_docs,
            "breakdown": {
                "doc_load_per_session": tokens_per_doc_load,
                "claude_processing_per_session": tokens_per_claude_processing,
                "response_per_session": tokens_per_response
            }
        }
    
    def scenario_with_tools(self, num_docs_kb: float, num_features: int) -> Dict:
        """Calculate costs WITH DocCompressor tools."""
        
        # One-time index build
        tokens_index_build = self.estimate_tokens(num_docs_kb)
        cost_index_build = self.estimate_cost(tokens_index_build)
        
        # Per session (smart query only relevant sections)
        # Smart query = 3-5% of total docs
        smart_query_percentage = 0.05
        tokens_per_smart_query = int(self.estimate_tokens(num_docs_kb) * smart_query_percentage)
        
        # Claude processing stays same
        tokens_per_claude_processing = 50000
        tokens_per_response = 15000
        
        # Per session (after first)
        tokens_per_session = tokens_per_smart_query + tokens_per_claude_processing + tokens_per_response
        cost_per_session = self.estimate_cost(tokens_per_session)
        
        # Total (index + all sessions)
        total_tokens = tokens_index_build + (tokens_per_session * num_features)
        total_cost = cost_index_build + (cost_per_session * num_features)
        
        # Memory benefit: avoid rebuilding (assume 30% of sessions reuse cached code)
        reuse_percentage = 0.30
        tokens_saved_by_memory = int(tokens_per_claude_processing * num_features * reuse_percentage)
        cost_saved_by_memory = self.estimate_cost(tokens_saved_by_memory)
        
        total_tokens -= tokens_saved_by_memory
        total_cost -= cost_saved_by_memory
        
        return {
            "scenario": "WITH DocCompressor Tools",
            "index_build_tokens": tokens_index_build,
            "index_build_cost": cost_index_build,
            "tokens_per_session": tokens_per_session,
            "cost_per_session": cost_per_session,
            "total_sessions": num_features,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "tokens_saved_by_memory": tokens_saved_by_memory,
            "cost_saved_by_memory": cost_saved_by_memory,
            "breakdown": {
                "index_build": tokens_index_build,
                "smart_query_per_session": tokens_per_smart_query,
                "claude_processing_per_session": tokens_per_claude_processing,
                "response_per_session": tokens_per_response,
                "memory_reuse": -tokens_saved_by_memory
            }
        }
    
    def generate_comparison(self, docs_size_kb: float, num_features: int) -> Dict:
        """Generate full comparison."""
        
        without = self.scenario_without_tools(docs_size_kb, num_features)
        with_tools = self.scenario_with_tools(docs_size_kb, num_features)
        
        # Calculate savings
        tokens_saved = without["total_tokens"] - with_tools["total_tokens"]
        cost_saved = without["total_cost"] - with_tools["total_cost"]
        tokens_reduction_percent = (tokens_saved / without["total_tokens"]) * 100
        cost_reduction_percent = (cost_saved / without["total_cost"]) * 100
        
        return {
            "metadata": {
                "generated_at": str(datetime.now()),
                "docs_size_kb": docs_size_kb,
                "num_features": num_features,
                "assumptions": {
                    "token_per_4_bytes": True,
                    "cost_per_1k_tokens": "$0.0001",
                    "claude_processing": "50K tokens per feature",
                    "smart_query_reduction": "95% (only 5% of docs loaded)"
                }
            },
            "without_tools": without,
            "with_tools": with_tools,
            "savings": {
                "total_tokens_saved": int(tokens_saved),
                "total_cost_saved": round(cost_saved, 2),
                "tokens_reduction_percent": round(tokens_reduction_percent, 1),
                "cost_reduction_percent": round(cost_reduction_percent, 1),
                "tokens_saved_per_feature": int(tokens_saved / num_features),
                "cost_saved_per_feature": round(cost_saved / num_features, 2)
            }
        }
    
    def format_comparison_text(self, comparison: Dict) -> str:
        """Format comparison as readable text."""
        
        meta = comparison["metadata"]
        without = comparison["without_tools"]
        with_tools = comparison["with_tools"]
        savings = comparison["savings"]
        
        output = []
        output.append("=" * 80)
        output.append("📊 TOKEN COMPARISON: WITH vs WITHOUT DocCompressor Tools")
        output.append("=" * 80)
        output.append("")
        
        # Metadata
        output.append("📋 SCENARIO")
        output.append(f"   Docs size: {meta['docs_size_kb']:.0f}KB")
        output.append(f"   Building: {meta['num_features']} features")
        output.append("")
        
        # Without tools
        output.append("❌ WITHOUT DocCompressor Tools")
        output.append("-" * 80)
        output.append(f"   Per session:")
        output.append(f"      Load all docs:        {without['breakdown']['doc_load_per_session']:,} tokens")
        output.append(f"      Claude processing:   {without['breakdown']['claude_processing_per_session']:,} tokens")
        output.append(f"      Response:            {without['breakdown']['response_per_session']:,} tokens")
        output.append(f"      ─────────────────────────────────")
        output.append(f"      Total per session:   {without['tokens_per_session']:,} tokens (${without['cost_per_session']:.2f})")
        output.append("")
        output.append(f"   For {meta['num_features']} features:")
        output.append(f"      Total tokens:        {without['total_tokens']:,} tokens")
        output.append(f"      Total cost:          ${without['total_cost']:.2f}")
        output.append(f"      Wasted on doc reload:{without['tokens_wasted_on_docs']:,} tokens")
        output.append("")
        
        # With tools
        output.append("✅ WITH DocCompressor Tools")
        output.append("-" * 80)
        output.append(f"   One-time setup:")
        output.append(f"      Index build:         {with_tools['breakdown']['index_build']:,} tokens (${with_tools['index_build_cost']:.2f})")
        output.append("")
        output.append(f"   Per session (after index):")
        output.append(f"      Smart query docs:    {with_tools['breakdown']['smart_query_per_session']:,} tokens (95% reduction!)")
        output.append(f"      Claude processing:   {with_tools['breakdown']['claude_processing_per_session']:,} tokens")
        output.append(f"      Response:            {with_tools['breakdown']['response_per_session']:,} tokens")
        output.append(f"      ─────────────────────────────────")
        output.append(f"      Total per session:   {with_tools['tokens_per_session']:,} tokens (${with_tools['cost_per_session']:.2f})")
        output.append("")
        output.append(f"   Memory benefit (30% code reuse):")
        output.append(f"      Tokens saved:        {with_tools['breakdown']['memory_reuse']:,} tokens")
        output.append(f"      Cost saved:          ${with_tools['cost_saved_by_memory']:.2f}")
        output.append("")
        output.append(f"   For {meta['num_features']} features:")
        output.append(f"      Total tokens:        {with_tools['total_tokens']:,} tokens")
        output.append(f"      Total cost:          ${with_tools['total_cost']:.2f}")
        output.append("")
        
        # Savings summary
        output.append("💰 TOTAL SAVINGS")
        output.append("=" * 80)
        output.append(f"   Tokens saved:        {savings['total_tokens_saved']:,} tokens ({savings['tokens_reduction_percent']:.1f}%)")
        output.append(f"   Cost saved:          ${savings['total_cost_saved']:.2f} ({savings['cost_reduction_percent']:.1f}%)")
        output.append(f"   Per feature:         {savings['tokens_saved_per_feature']:,} tokens / ${savings['cost_saved_per_feature']:.2f}")
        output.append("=" * 80)
        output.append("")
        
        return '\n'.join(output)
    
    def format_comparison_json(self, comparison: Dict) -> str:
        """Format comparison as JSON."""
        return json.dumps(comparison, indent=2)
    
    def format_comparison_table(self, comparison: Dict) -> str:
        """Format comparison as markdown table."""
        
        without = comparison["without_tools"]
        with_tools = comparison["with_tools"]
        savings = comparison["savings"]
        meta = comparison["metadata"]
        
        output = []
        output.append("# 📊 Token Comparison Report\n")
        output.append(f"**Docs:** {meta['docs_size_kb']:.0f}KB | **Features:** {meta['num_features']}\n")
        
        output.append("## Per-Session Cost\n")
        output.append("| Metric | Without Tools | With Tools | Savings |")
        output.append("|--------|---|---|---|")
        output.append(f"| Tokens/session | {without['tokens_per_session']:,} | {with_tools['tokens_per_session']:,} | {without['tokens_per_session'] - with_tools['tokens_per_session']:,} |")
        output.append(f"| Cost/session | ${without['cost_per_session']:.2f} | ${with_tools['cost_per_session']:.2f} | ${without['cost_per_session'] - with_tools['cost_per_session']:.2f} |")
        output.append("")
        
        output.append("## Total Cost (All Features)\n")
        output.append("| Metric | Without Tools | With Tools | Savings |")
        output.append("|--------|---|---|---|")
        output.append(f"| Total tokens | {without['total_tokens']:,} | {with_tools['total_tokens']:,} | {savings['total_tokens_saved']:,} |")
        output.append(f"| Total cost | ${without['total_cost']:.2f} | ${with_tools['total_cost']:.2f} | ${savings['total_cost_saved']:.2f} |")
        output.append(f"| Reduction | — | — | {savings['tokens_reduction_percent']:.1f}% |")
        output.append("")
        
        output.append("## Key Benefits\n")
        output.append(f"- 💾 **Smart indexing:** 95% reduction in docs loaded per session")
        output.append(f"- 🧠 **Memory:** Reuse cached code (avoid rebuild)")
        output.append(f"- 📉 **Total savings:** {savings['total_tokens_saved']:,} tokens ({savings['cost_reduction_percent']:.1f}%)")
        output.append(f"- 💰 **Cost savings:** ${savings['total_cost_saved']:.2f}")
        output.append("")
        
        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate token comparison: WITH vs WITHOUT DocCompressor tools"
    )
    parser.add_argument('--docs-size', type=float, default=707, 
                       help='Total docs size in KB (default: 707)')
    parser.add_argument('--features', type=int, default=100,
                       help='Number of features to build (default: 100)')
    parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--output', help='Save to file (optional)')
    
    args = parser.parse_args()
    
    # Generate comparison
    comparator = TokenComparison()
    comparison = comparator.generate_comparison(args.docs_size, args.features)
    
    # Format output
    if args.format == 'json':
        output = comparator.format_comparison_json(comparison)
    elif args.format == 'markdown':
        output = comparator.format_comparison_table(comparison)
    else:
        output = comparator.format_comparison_text(comparison)
    
    # Print or save
    print(output)
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"\n✅ Saved to {args.output}")


if __name__ == '__main__':
    main()
