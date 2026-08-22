#!/usr/bin/env python3
"""
DocCompressor Smart Memory v5: Agent Memory + Smart Caching
- Tracks what agent has built (memory)
- Caches completed work (never redo)
- Saves context by reusing artifacts
- User controls: auto-save or manual save
- Persistent across sessions
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SmartAgentMemory:
    """Intelligent agent memory system."""
    
    def __init__(self, memory_file: str = '.agent-memory.json'):
        self.memory_file = memory_file
        self.memory = {
            "metadata": {
                "version": "1.0",
                "created": str(datetime.now()),
                "last_updated": str(datetime.now()),
                "total_builds": 0,
                "total_tokens_saved": 0
            },
            "completed_tasks": {},
            "code_artifacts": {},
            "api_implementations": {},
            "database_schemas": {},
            "features_built": [],
            "context_notes": {}
        }
        self.load_memory()
    
    def load_memory(self) -> bool:
        """Load existing memory if available."""
        if Path(self.memory_file).exists():
            try:
                self.memory = json.loads(Path(self.memory_file).read_text())
                print(f"✅ Loaded agent memory from {self.memory_file}")
                print(f"   Previous builds: {self.memory['metadata'].get('total_builds', 0)}")
                print(f"   Tokens saved so far: {self.memory['metadata'].get('total_tokens_saved', 0):,}\n")
                return True
            except Exception as e:
                print(f"⚠️  Could not load memory: {e}\n")
        return False
    
    def save_memory(self, auto_save: bool = True) -> bool:
        """Save memory to file."""
        try:
            self.memory['metadata']['last_updated'] = str(datetime.now())
            Path(self.memory_file).write_text(json.dumps(self.memory, indent=2))
            
            if auto_save:
                print(f"💾 Memory auto-saved")
            else:
                print(f"💾 Memory manually saved")
            
            return True
        except Exception as e:
            print(f"❌ Failed to save memory: {e}")
            return False
    
    def record_task(self, task_name: str, task_type: str, description: str, 
                   code: str = None, tokens_saved: int = 0, auto_save: bool = True) -> bool:
        """Record completed task in memory."""
        
        task_id = f"{task_type}:{task_name}:{datetime.now().timestamp()}"
        
        self.memory['completed_tasks'][task_id] = {
            "name": task_name,
            "type": task_type,
            "description": description,
            "code": code,
            "timestamp": str(datetime.now()),
            "tokens_saved": tokens_saved,
            "status": "completed"
        }
        
        # Add to feature list
        if task_type == "feature":
            self.memory['features_built'].append({
                "name": task_name,
                "timestamp": str(datetime.now()),
                "code_file": code[:50] if code else None
            })
        
        # Update stats
        self.memory['metadata']['total_builds'] += 1
        self.memory['metadata']['total_tokens_saved'] += tokens_saved
        
        print(f"✅ Recorded: {task_type} → {task_name}")
        print(f"   Tokens saved: {tokens_saved:,}")
        
        self.save_memory(auto_save=auto_save)
        return True
    
    def record_api(self, endpoint: str, method: str, description: str, 
                  implementation: str = None, auto_save: bool = True) -> bool:
        """Record built API endpoint."""
        
        self.memory['api_implementations'][endpoint] = {
            "method": method,
            "description": description,
            "implementation": implementation,
            "timestamp": str(datetime.now()),
            "status": "implemented"
        }
        
        print(f"✅ API Recorded: {method} {endpoint}")
        self.save_memory(auto_save=auto_save)
        return True
    
    def record_schema(self, table_name: str, schema: str, auto_save: bool = True) -> bool:
        """Record created database schema."""
        
        self.memory['database_schemas'][table_name] = {
            "schema": schema,
            "timestamp": str(datetime.now()),
            "status": "created"
        }
        
        print(f"✅ Schema Recorded: Table '{table_name}'")
        self.save_memory(auto_save=auto_save)
        return True
    
    def record_code_artifact(self, artifact_name: str, language: str, code: str,
                            purpose: str, auto_save: bool = True) -> bool:
        """Record reusable code artifact."""
        
        self.memory['code_artifacts'][artifact_name] = {
            "language": language,
            "code": code,
            "purpose": purpose,
            "timestamp": str(datetime.now()),
            "status": "saved"
        }
        
        print(f"✅ Code Artifact Saved: {artifact_name} ({language})")
        self.save_memory(auto_save=auto_save)
        return True
    
    def record_context_note(self, key: str, note: str, auto_save: bool = True) -> bool:
        """Record context note (for remembering context in next session)."""
        
        self.memory['context_notes'][key] = {
            "note": note,
            "timestamp": str(datetime.now())
        }
        
        print(f"✅ Context Note Saved: {key}")
        self.save_memory(auto_save=auto_save)
        return True
    
    def get_task_history(self) -> Dict:
        """Get history of all completed tasks."""
        return self.memory.get('completed_tasks', {})
    
    def get_api_implementations(self) -> Dict:
        """Get all implemented APIs."""
        return self.memory.get('api_implementations', {})
    
    def get_database_schemas(self) -> Dict:
        """Get all created schemas."""
        return self.memory.get('database_schemas', {})
    
    def get_code_artifacts(self) -> Dict:
        """Get all saved code artifacts."""
        return self.memory.get('code_artifacts', {})
    
    def get_features_built(self) -> List:
        """Get list of built features."""
        return self.memory.get('features_built', [])
    
    def get_context(self, key: str) -> Optional[str]:
        """Get context note from memory."""
        note_data = self.memory.get('context_notes', {}).get(key)
        if note_data:
            return note_data.get('note')
        return None
    
    def check_if_built(self, task_name: str) -> Optional[Dict]:
        """Check if task was already built (reuse instead of rebuild)."""
        for task_id, task_data in self.memory.get('completed_tasks', {}).items():
            if task_data['name'].lower() == task_name.lower():
                return task_data
        return None
    
    def suggest_reusable_code(self, purpose: str) -> Optional[Dict]:
        """Suggest reusable code artifact based on purpose."""
        for artifact_name, artifact_data in self.memory.get('code_artifacts', {}).items():
            if purpose.lower() in artifact_data.get('purpose', '').lower():
                return {
                    "name": artifact_name,
                    "code": artifact_data.get('code'),
                    "language": artifact_data.get('language')
                }
        return None
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        return {
            "total_builds": self.memory['metadata'].get('total_builds', 0),
            "total_tokens_saved": self.memory['metadata'].get('total_tokens_saved', 0),
            "completed_tasks": len(self.memory.get('completed_tasks', {})),
            "api_endpoints": len(self.memory.get('api_implementations', {})),
            "database_schemas": len(self.memory.get('database_schemas', {})),
            "code_artifacts": len(self.memory.get('code_artifacts', {})),
            "features_built": len(self.memory.get('features_built', []))
        }
    
    def generate_memory_report(self) -> str:
        """Generate human-readable memory report."""
        output = []
        output.append("# 🧠 Agent Memory Report\n")
        
        # Stats
        stats = self.get_stats()
        output.append("## 📊 Statistics\n")
        output.append(f"- **Total Builds:** {stats['total_builds']}")
        output.append(f"- **Tokens Saved:** {stats['total_tokens_saved']:,}")
        output.append(f"- **Completed Tasks:** {stats['completed_tasks']}")
        output.append(f"- **API Endpoints:** {stats['api_endpoints']}")
        output.append(f"- **Database Schemas:** {stats['database_schemas']}")
        output.append(f"- **Code Artifacts:** {stats['code_artifacts']}")
        output.append("")
        
        # Features built
        if self.memory.get('features_built'):
            output.append("## ✨ Features Built\n")
            for feature in self.memory.get('features_built', [])[-10:]:
                output.append(f"- **{feature['name']}** ({feature['timestamp'][:10]})")
            output.append("")
        
        # APIs implemented
        if self.memory.get('api_implementations'):
            output.append("## 🔌 API Endpoints\n")
            for endpoint, api_data in list(self.memory.get('api_implementations', {}).items())[-10:]:
                output.append(f"- **{api_data['method']}** `{endpoint}`")
                output.append(f"  - {api_data['description']}")
            output.append("")
        
        # Database schemas
        if self.memory.get('database_schemas'):
            output.append("## 🗄️ Database Schemas\n")
            for table_name, schema_data in list(self.memory.get('database_schemas', {}).items())[-10:]:
                output.append(f"- **{table_name}**")
            output.append("")
        
        # Context notes
        if self.memory.get('context_notes'):
            output.append("## 📝 Context Notes\n")
            for key, note_data in self.memory.get('context_notes', {}).items():
                output.append(f"- **{key}:** {note_data['note']}")
            output.append("")
        
        output.append(f"**Last Updated:** {self.memory['metadata'].get('last_updated', 'Never')}")
        
        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Smart Agent Memory: Track builds, save tokens, remember context"
    )
    parser.add_argument('-m', '--memory-file', default='.agent-memory.json', 
                       help='Memory file location')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Record task
    record_parser = subparsers.add_parser('record', help='Record completed task')
    record_parser.add_argument('--name', required=True, help='Task name')
    record_parser.add_argument('--type', required=True, 
                              choices=['feature', 'api', 'fix', 'optimization', 'other'])
    record_parser.add_argument('--description', required=True, help='What was done')
    record_parser.add_argument('--code', help='Code snippet')
    record_parser.add_argument('--tokens-saved', type=int, default=0, help='Tokens saved')
    record_parser.add_argument('--auto-save', action='store_true', default=True)
    
    # Record API
    api_parser = subparsers.add_parser('api', help='Record API endpoint')
    api_parser.add_argument('--endpoint', required=True, help='API endpoint')
    api_parser.add_argument('--method', required=True, choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    api_parser.add_argument('--description', required=True, help='What it does')
    api_parser.add_argument('--auto-save', action='store_true', default=True)
    
    # Record schema
    schema_parser = subparsers.add_parser('schema', help='Record database schema')
    schema_parser.add_argument('--table', required=True, help='Table name')
    schema_parser.add_argument('--definition', required=True, help='Table schema/definition')
    schema_parser.add_argument('--auto-save', action='store_true', default=True)
    
    # Record artifact
    artifact_parser = subparsers.add_parser('artifact', help='Save code artifact')
    artifact_parser.add_argument('--name', required=True, help='Artifact name')
    artifact_parser.add_argument('--language', required=True, help='Language (python, javascript, etc)')
    artifact_parser.add_argument('--code', required=True, help='Code snippet')
    artifact_parser.add_argument('--purpose', required=True, help='What this is for')
    artifact_parser.add_argument('--auto-save', action='store_true', default=True)
    
    # Record context
    context_parser = subparsers.add_parser('context', help='Save context note')
    context_parser.add_argument('--key', required=True, help='Context key')
    context_parser.add_argument('--note', required=True, help='Context note')
    context_parser.add_argument('--auto-save', action='store_true', default=True)
    
    # View memory
    view_parser = subparsers.add_parser('view', help='View memory')
    view_parser.add_argument('--what', choices=['all', 'tasks', 'apis', 'schemas', 'artifacts', 'features', 'stats'],
                            default='all', help='What to view')
    
    # Check if built
    check_parser = subparsers.add_parser('check', help='Check if task was already built')
    check_parser.add_argument('--task', required=True, help='Task name to check')
    
    # Report
    subparsers.add_parser('report', help='Generate memory report')
    
    args = parser.parse_args()
    
    memory = SmartAgentMemory(memory_file=args.memory_file)
    
    if not args.command:
        # Show default stats
        print("\n🧠 Agent Memory System\n")
        stats = memory.get_stats()
        print(f"Total Builds: {stats['total_builds']}")
        print(f"Tokens Saved: {stats['total_tokens_saved']:,}")
        print(f"Completed Tasks: {stats['completed_tasks']}")
        print(f"\nUse 'python doc-compressor-memory.py --help' for commands\n")
        return
    
    # Record task
    if args.command == 'record':
        memory.record_task(
            args.name, args.type, args.description,
            code=args.code,
            tokens_saved=args.tokens_saved,
            auto_save=args.auto_save
        )
    
    # Record API
    elif args.command == 'api':
        memory.record_api(
            args.endpoint, args.method, args.description,
            auto_save=args.auto_save
        )
    
    # Record schema
    elif args.command == 'schema':
        memory.record_schema(
            args.table, args.definition,
            auto_save=args.auto_save
        )
    
    # Record artifact
    elif args.command == 'artifact':
        memory.record_code_artifact(
            args.name, args.language, args.code, args.purpose,
            auto_save=args.auto_save
        )
    
    # Record context
    elif args.command == 'context':
        memory.record_context_note(
            args.key, args.note,
            auto_save=args.auto_save
        )
    
    # View memory
    elif args.command == 'view':
        if args.what in ['all', 'tasks']:
            print("\n📋 Completed Tasks:")
            tasks = memory.get_task_history()
            if tasks:
                for task_id, task in list(tasks.items())[-10:]:
                    print(f"- {task['name']} ({task['type']}) - {task['timestamp'][:10]}")
            else:
                print("   (none yet)")
        
        if args.what in ['all', 'apis']:
            print("\n🔌 API Endpoints:")
            apis = memory.get_api_implementations()
            if apis:
                for endpoint, api in apis.items():
                    print(f"- {api['method']} {endpoint}")
            else:
                print("   (none yet)")
        
        if args.what in ['all', 'schemas']:
            print("\n🗄️ Database Schemas:")
            schemas = memory.get_database_schemas()
            if schemas:
                for table in schemas:
                    print(f"- {table}")
            else:
                print("   (none yet)")
        
        if args.what in ['all', 'artifacts']:
            print("\n💾 Code Artifacts:")
            artifacts = memory.get_code_artifacts()
            if artifacts:
                for name, artifact in artifacts.items():
                    print(f"- {name} ({artifact['language']})")
            else:
                print("   (none yet)")
        
        if args.what in ['all', 'features']:
            print("\n✨ Features Built:")
            features = memory.get_features_built()
            if features:
                for feature in features[-10:]:
                    print(f"- {feature['name']}")
            else:
                print("   (none yet)")
        
        if args.what in ['all', 'stats']:
            print("\n📊 Statistics:")
            stats = memory.get_stats()
            for key, value in stats.items():
                print(f"- {key}: {value:,}")
    
    # Check if built
    elif args.command == 'check':
        task = memory.check_if_built(args.task)
        if task:
            print(f"\n✅ Already Built:")
            print(f"   Task: {task['name']}")
            print(f"   Type: {task['type']}")
            print(f"   Description: {task['description']}")
            print(f"   Timestamp: {task['timestamp']}")
            if task.get('code'):
                print(f"   Code: {task['code'][:100]}...")
        else:
            print(f"\n❌ Task '{args.task}' not found in memory")
    
    # Report
    elif args.command == 'report':
        report = memory.generate_memory_report()
        print(f"\n{report}")


if __name__ == '__main__':
    main()
