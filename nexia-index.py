#!/usr/bin/env python3
"""
DocCompressor Smart Index v4: Persistent Documentation Query System
- One-time compression & indexing (first run only)
- Smart section extraction (query-based, no re-compression)
- Persists across sessions (reuses indexed data)
- Agent asks for what it needs, gets exactly that
- Zero API costs, zero re-processing
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class DocIndex:
    """Smart documentation index system."""
    
    def __init__(self, index_file: str = '.doc-index.json'):
        self.index_file = index_file
        self.index_data = {}
        self.load_index()
    
    def load_index(self):
        """Load existing index if available."""
        if Path(self.index_file).exists():
            try:
                self.index_data = json.loads(Path(self.index_file).read_text())
                print(f"✅ Loaded existing index from {self.index_file}")
                return True
            except Exception as e:
                print(f"⚠️  Could not load index: {e}")
        return False
    
    def save_index(self):
        """Save index to file."""
        Path(self.index_file).write_text(json.dumps(self.index_data, indent=2))
        print(f"💾 Index saved to {self.index_file}")
    
    def extract_sections(self, content: str) -> Dict[str, Dict]:
        """Extract all sections from document with metadata."""
        sections = {}
        current_heading = "intro"
        current_content = []
        heading_level = 0
        
        for line in content.split('\n'):
            # Check if line is a heading
            if line.strip().startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_heading] = {
                        "content": '\n'.join(current_content).strip(),
                        "level": heading_level,
                        "lines": len(current_content)
                    }
                
                # Start new section
                match = re.match(r'^(#+)\s+(.+)$', line.strip())
                if match:
                    heading_level = len(match.group(1))
                    current_heading = match.group(2).lower().replace(' ', '_')
                    current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_heading] = {
                "content": '\n'.join(current_content).strip(),
                "level": heading_level,
                "lines": len(current_content)
            }
        
        return sections
    
    def extract_code_blocks(self, content: str) -> List[Dict]:
        """Extract all code blocks with context."""
        blocks = []
        pattern = r'```([\w]*)\n(.*?)\n```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2)
            
            # Extract first meaningful line (signature)
            lines = code.split('\n')
            signature = None
            for line in lines:
                if any(kw in line for kw in ['def ', 'class ', 'async ', 'export ', 'const ', 'function ']):
                    signature = line.strip()
                    break
            
            blocks.append({
                "language": language,
                "code": code[:300],  # First 300 chars
                "signature": signature,
                "full_code": code
            })
        
        return blocks
    
    def extract_tables(self, content: str) -> List[str]:
        """Extract all markdown tables."""
        tables = []
        pattern = r'(\|[^\n]*\|(?:\n\|[^\n]*\|)+)'
        
        for match in re.finditer(pattern, content):
            table = match.group(1).strip()
            tables.append(table)
        
        return tables
    
    def extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords and entities."""
        keywords = set()
        
        # API endpoints
        keywords.update(re.findall(r'(?:GET|POST|PUT|DELETE|PATCH)\s+/\S+', content))
        
        # Database tables
        keywords.update(re.findall(r'(?:table|Table)\s+["`]?(\w+)["`]?', content))
        
        # Function/Class names
        keywords.update(re.findall(r'(?:def|class)\s+(\w+)', content))
        
        # Important terms
        for term in ['authentication', 'authorization', 'encryption', 'database', 'cache', 'queue', 'api']:
            if term in content.lower():
                keywords.add(term)
        
        return list(keywords)
    
    def build_index(self, directory: str) -> Dict:
        """Build comprehensive index from documents."""
        print(f"\n🔨 Building index from {directory}...\n")
        
        docs_dir = Path(directory)
        if not docs_dir.exists():
            print(f"❌ Directory not found: {directory}")
            return {}
        
        index = {
            "metadata": {
                "created": str(Path(directory).stat().st_mtime),
                "docs_count": 0,
                "total_sections": 0,
                "total_code_blocks": 0,
                "total_tables": 0
            },
            "documents": {},
            "sections_by_name": {},
            "keywords_index": defaultdict(list),
            "code_signatures": {},
            "tables_index": {}
        }
        
        supported = {'.md', '.txt', '.py', '.js', '.json', '.yaml', '.yml', '.sql'}
        doc_count = 0
        
        for file_path in sorted(docs_dir.rglob('*')):
            if file_path.is_file() and file_path.suffix in supported:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if len(content) < 50:
                        continue
                    
                    doc_count += 1
                    doc_name = file_path.name
                    print(f"  📄 Indexing: {doc_name}")
                    
                    # Extract components
                    sections = self.extract_sections(content)
                    code_blocks = self.extract_code_blocks(content)
                    tables = self.extract_tables(content)
                    keywords = self.extract_keywords(content)
                    
                    # Store in index
                    index["documents"][doc_name] = {
                        "path": str(file_path),
                        "size_bytes": len(content),
                        "sections": len(sections),
                        "code_blocks": len(code_blocks),
                        "tables": len(tables),
                        "keywords": keywords,
                        "sections_data": sections
                    }
                    
                    # Index sections by name
                    for section_name, section_data in sections.items():
                        key = f"{doc_name}#{section_name}"
                        index["sections_by_name"][key] = section_data
                    
                    # Index code signatures
                    for i, block in enumerate(code_blocks):
                        if block.get('signature'):
                            index["code_signatures"][f"{doc_name}:block_{i}"] = {
                                "signature": block['signature'],
                                "language": block['language'],
                                "code": block['full_code']
                            }
                    
                    # Index tables
                    for i, table in enumerate(tables):
                        index["tables_index"][f"{doc_name}:table_{i}"] = table
                    
                    # Build keyword index
                    for keyword in keywords:
                        index["keywords_index"][keyword.lower()].append(doc_name)
                    
                    # Update stats
                    index["metadata"]["total_sections"] += len(sections)
                    index["metadata"]["total_code_blocks"] += len(code_blocks)
                    index["metadata"]["total_tables"] += len(tables)
                    
                except Exception as e:
                    print(f"  ⚠️  Skipped {file_path.name}: {e}")
        
        index["metadata"]["docs_count"] = doc_count
        
        # Convert defaultdict to regular dict
        index["keywords_index"] = dict(index["keywords_index"])
        
        print(f"\n✅ Index built!")
        print(f"   Documents: {doc_count}")
        print(f"   Sections: {index['metadata']['total_sections']}")
        print(f"   Code blocks: {index['metadata']['total_code_blocks']}")
        print(f"   Tables: {index['metadata']['total_tables']}")
        print(f"   Keywords indexed: {len(index['keywords_index'])}")
        
        return index
    
    def query_by_keyword(self, keyword: str) -> Dict:
        """Query: Find sections containing keyword."""
        if not self.index_data:
            return {"error": "Index not built. Run: doc-compressor-smart-index --build --input ./docs"}
        
        keyword_lower = keyword.lower()
        results = {}
        
        # Find in keywords index
        if keyword_lower in self.index_data.get("keywords_index", {}):
            docs = self.index_data["keywords_index"][keyword_lower]
            results["docs_containing_keyword"] = docs
        
        # Find in section names
        for section_key, section_data in self.index_data.get("sections_by_name", {}).items():
            if keyword_lower in section_key.lower():
                doc_name, section_name = section_key.split('#')
                if doc_name not in results:
                    results[doc_name] = []
                results[doc_name].append({
                    "section": section_name,
                    "lines": section_data.get("lines", 0),
                    "content": section_data.get("content", "")[:300]
                })
        
        return results
    
    def query_api_endpoints(self) -> Dict:
        """Query: Get all API endpoints."""
        if not self.index_data:
            return {}
        
        endpoints = {}
        for keyword, docs in self.index_data.get("keywords_index", {}).items():
            if keyword.startswith(('get ', 'post ', 'put ', 'delete ', 'patch ')):
                endpoints[keyword] = docs
        
        return endpoints
    
    def query_database_schema(self) -> Dict:
        """Query: Get all database tables."""
        if not self.index_data:
            return {}
        
        tables = {}
        for table_key, table_content in self.index_data.get("tables_index", {}).items():
            doc_name, table_id = table_key.split(':')
            if doc_name not in tables:
                tables[doc_name] = []
            tables[doc_name].append(table_content[:500])  # First 500 chars
        
        return tables
    
    def query_code_signatures(self, language: str = None) -> Dict:
        """Query: Get code signatures (function/class definitions)."""
        if not self.index_data:
            return {}
        
        signatures = {}
        for sig_key, sig_data in self.index_data.get("code_signatures", {}).items():
            if language and sig_data.get("language") != language:
                continue
            signatures[sig_key] = sig_data.get("signature")
        
        return signatures
    
    def query_section(self, doc_name: str, section_name: str) -> Optional[Dict]:
        """Query: Get specific section from doc."""
        if not self.index_data:
            return None
        
        key = f"{doc_name}#{section_name}"
        return self.index_data.get("sections_by_name", {}).get(key)
    
    def generate_quick_reference(self) -> str:
        """Generate quick reference guide from index."""
        if not self.index_data:
            return "Index not built"
        
        output = []
        output.append("# 📚 Documentation Quick Reference\n")
        
        # Overview
        meta = self.index_data.get("metadata", {})
        output.append(f"**Docs:** {meta.get('docs_count', 0)} files")
        output.append(f"**Sections:** {meta.get('total_sections', 0)}")
        output.append(f"**API Endpoints:** {len([k for k in self.index_data.get('keywords_index', {}).keys() if 'get ' in k or 'post ' in k])}")
        output.append(f"**Tables:** {meta.get('total_tables', 0)}")
        output.append("")
        
        # Documents list
        output.append("## 📄 Documents\n")
        for doc_name, doc_data in self.index_data.get("documents", {}).items():
            output.append(f"- **{doc_name}** ({doc_data.get('sections', 0)} sections)")
        
        output.append("")
        
        # Quick queries
        output.append("## 🔍 Quick Queries (Use These)\n")
        output.append("```")
        output.append("# Search by keyword")
        output.append("python doc-compressor-smart-index --query api --input ./docs")
        output.append("")
        output.append("# Get API endpoints")
        output.append("python doc-compressor-smart-index --apis --input ./docs")
        output.append("")
        output.append("# Get database schema")
        output.append("python doc-compressor-smart-index --schema --input ./docs")
        output.append("")
        output.append("# Get specific section")
        output.append("python doc-compressor-smart-index --section prd.md:features --input ./docs")
        output.append("```")
        
        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description="DocCompressor Smart Index: One-time compression, persistent queries"
    )
    parser.add_argument('-i', '--input', required=True, help='Docs directory')
    parser.add_argument('--build', action='store_true', help='Build index (one-time)')
    parser.add_argument('--query', help='Query by keyword')
    parser.add_argument('--apis', action='store_true', help='Get all API endpoints')
    parser.add_argument('--schema', action='store_true', help='Get database schema')
    parser.add_argument('--section', help='Get specific section (format: doc.md:section_name)')
    parser.add_argument('--reference', action='store_true', help='Generate quick reference')
    parser.add_argument('--index-file', default='.doc-index.json', help='Index file location')
    
    args = parser.parse_args()
    
    indexer = DocIndex(index_file=args.index_file)
    
    # Build index (one-time)
    if args.build:
        index = indexer.build_index(args.input)
        indexer.index_data = index
        indexer.save_index()
        print(f"✅ Index saved. Use queries next time (no rebuild needed).\n")
        return
    
    # Ensure index is loaded
    if not indexer.index_data:
        print("⚠️  No index found. Run build first:")
        print(f"   python doc-compressor-smart-index --build --input {args.input}\n")
        return
    
    # Query: By keyword
    if args.query:
        results = indexer.query_by_keyword(args.query)
        print(f"\n🔍 Results for '{args.query}':")
        print(json.dumps(results, indent=2))
        return
    
    # Query: APIs
    if args.apis:
        apis = indexer.query_api_endpoints()
        print(f"\n🔌 API Endpoints:")
        for endpoint, docs in apis.items():
            print(f"- {endpoint} (in {docs})")
        return
    
    # Query: Schema
    if args.schema:
        schema = indexer.query_database_schema()
        print(f"\n🗄️ Database Schema:")
        print(json.dumps(schema, indent=2))
        return
    
    # Query: Specific section
    if args.section:
        parts = args.section.split(':')
        if len(parts) == 2:
            doc_name, section_name = parts
            section = indexer.query_section(doc_name, section_name)
            if section:
                print(f"\n📖 {doc_name} → {section_name}:")
                print(section.get("content", ""))
            else:
                print(f"❌ Section not found")
        return
    
    # Generate reference
    if args.reference:
        reference = indexer.generate_quick_reference()
        print(reference)
        return
    
    # Default: show stats
    meta = indexer.index_data.get("metadata", {})
    print(f"\n📊 Index Statistics:")
    print(f"   Documents: {meta.get('docs_count', 0)}")
    print(f"   Sections: {meta.get('total_sections', 0)}")
    print(f"   Code blocks: {meta.get('total_code_blocks', 0)}")
    print(f"   Tables: {meta.get('total_tables', 0)}")
    print(f"\n💡 Use --help to see available queries")


if __name__ == '__main__':
    main()
