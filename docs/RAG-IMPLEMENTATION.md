# RAG Implementation Guide

## Overview

This document details the implementation of a Retrieval-Augmented Generation (RAG) system specifically designed for Ignition SCADA/HMI development. The RAG system combines official Ignition documentation, community knowledge, and most importantly, your production codebase to provide contextually relevant, accurate code generation.

## 🏗️ Architecture

### Multi-Layer Vector Storage

```mermaid
graph TB
    subgraph "Data Sources"
        Official[Official Ignition Docs<br/>SDK, Components, Functions]
        Production[Production Codebases<br/>WHK-Global, SCADA, Reporting]
        Community[Community Knowledge<br/>Exchange, GitHub, Forums]
        Internal[Internal Knowledge<br/>Standards, Patterns, Solutions]
    end
    
    subgraph "Processing Pipeline"
        Scrapers[Web Scrapers<br/>Documentation Extraction]
        Analyzers[Code Analyzers<br/>Pattern Recognition]
        Processors[Document Processors<br/>Chunking & Metadata]
        Quality[Quality Filters<br/>Validation & Scoring]
    end
    
    subgraph "Vector Database"
        Embeddings[Text Embeddings<br/>OpenAI text-embedding-3-large]
        Metadata[Rich Metadata<br/>Context & Quality Scores]
        Indexes[Specialized Indexes<br/>Component, Script, Tag, Config]
    end
    
    subgraph "Retrieval System"
        Query[Query Processing<br/>Intent Detection]
        Search[Semantic Search<br/>Multi-Index Querying]
        Ranking[Context Ranking<br/>Relevance & Quality]
        Synthesis[Response Synthesis<br/>Production-Aware Prompts]
    end
    
    Official --> Scrapers
    Production --> Analyzers
    Community --> Scrapers
    Internal --> Processors
    
    Scrapers --> Processors
    Analyzers --> Processors
    Processors --> Quality
    
    Quality --> Embeddings
    Quality --> Metadata
    Quality --> Indexes
    
    Query --> Search
    Search --> Indexes
    Indexes --> Ranking
    Ranking --> Synthesis
    
    style Production fill:#e8f5e8
    style Quality fill:#fff3e0
    style Synthesis fill:#fce4ec
```

## 📊 Database Schema

### Vector Storage Schema (PostgreSQL + pgvector)

```sql
-- Main knowledge storage table
CREATE TABLE ignition_knowledge (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL, -- 'official', 'production', 'community', 'internal'
    doc_type VARCHAR(50) NOT NULL,    -- 'component', 'script', 'binding', 'config', 'pattern'
    category VARCHAR(100),            -- 'perspective', 'jython', 'tag', 'gateway', 'reporting'
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    code_example TEXT,
    metadata JSONB NOT NULL,
    embedding vector(1536) NOT NULL,
    quality_score FLOAT DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_source_type CHECK (source_type IN ('official', 'production', 'community', 'internal')),
    CONSTRAINT valid_quality_score CHECK (quality_score >= 0.0 AND quality_score <= 1.0)
);

-- Specialized indexes for performance
CREATE INDEX idx_embedding ON ignition_knowledge 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_metadata ON ignition_knowledge USING GIN (metadata);
CREATE INDEX idx_source_type ON ignition_knowledge (source_type);
CREATE INDEX idx_doc_type ON ignition_knowledge (doc_type);
CREATE INDEX idx_category ON ignition_knowledge (category);
CREATE INDEX idx_quality_score ON ignition_knowledge (quality_score DESC);

-- Production code tracking
CREATE TABLE production_code_versions (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    file_path TEXT NOT NULL,
    git_commit_hash VARCHAR(40),
    file_hash VARCHAR(64) NOT NULL,
    indexed_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(file_path, file_hash)
);

-- Pattern analysis results
CREATE TABLE code_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL, -- 'component', 'script', 'binding', 'navigation'
    pattern_name VARCHAR(200) NOT NULL,
    pattern_definition JSONB NOT NULL,
    usage_examples JSONB NOT NULL,
    quality_metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User feedback for continuous improvement
CREATE TABLE rag_feedback (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    retrieved_docs INTEGER[] NOT NULL, -- Array of knowledge IDs
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    was_helpful BOOLEAN,
    corrections TEXT,
    context_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Data Ingestion Pipeline

### 1. Official Documentation Scraper

```python
# ignition-rag/app/scrapers/ignition_docs_scraper.py
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from typing import List, Dict, Optional

class IgnitionDocsExtracter:
    def __init__(self):
        self.base_urls = [
            "https://docs.inductiveautomation.com/display/DOC81/Perspective+Component+Reference",
            "https://docs.inductiveautomation.com/display/DOC81/Scripting+Functions",
            "https://docs.inductiveautomation.com/display/DOC81/Expression+Functions",
            "https://docs.inductiveautomation.com/display/DOC81/System+Functions"
        ]
        self.session = None
        
    async def extract_perspective_components(self) -> List[Dict]:
        """Extract Perspective component documentation"""
        components = []
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Get component list page
            component_list = await self._fetch_component_list()
            
            for component in component_list:
                try:
                    component_data = await self._extract_component_details(component['url'])
                    components.append({
                        'type': 'perspective_component',
                        'name': component['name'],
                        'description': component_data['description'],
                        'properties': component_data['properties'],
                        'events': component_data['events'],
                        'methods': component_data.get('methods', {}),
                        'examples': component_data.get('examples', []),
                        'metadata': {
                            'component_type': component['name'],
                            'doc_url': component['url'],
                            'complexity': self._assess_complexity(component_data),
                            'common_use_cases': component_data.get('use_cases', [])
                        }
                    })
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error extracting {component['name']}: {e}")
                    continue
                    
        return components
    
    async def extract_scripting_functions(self) -> List[Dict]:
        """Extract Jython/Python scripting functions"""
        functions = []
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Process each system module
            modules = ['system.tag', 'system.db', 'system.util', 'system.perspective', 'system.alarm']
            
            for module in modules:
                try:
                    module_functions = await self._extract_module_functions(module)
                    functions.extend(module_functions)
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Error extracting {module}: {e}")
                    continue
                    
        return functions
    
    async def _extract_component_details(self, component_url: str) -> Dict:
        """Extract detailed information for a specific component"""
        async with self.session.get(component_url) as response:
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract component properties
        properties = {}
        prop_table = soup.find('table', {'class': 'properties-table'})
        if prop_table:
            for row in prop_table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 3:
                    prop_name = cells[0].get_text(strip=True)
                    prop_type = cells[1].get_text(strip=True)
                    prop_desc = cells[2].get_text(strip=True)
                    properties[prop_name] = {
                        'type': prop_type,
                        'description': prop_desc,
                        'bindable': 'bindable' in prop_desc.lower()
                    }
        
        # Extract events
        events = {}
        events_section = soup.find('div', {'id': 'events'})
        if events_section:
            for event_div in events_section.find_all('div', {'class': 'event'}):
                event_name = event_div.find('h4')
                if event_name:
                    events[event_name.get_text(strip=True)] = {
                        'description': event_div.find('p').get_text(strip=True) if event_div.find('p') else '',
                        'parameters': self._extract_event_parameters(event_div)
                    }
        
        # Extract code examples
        examples = []
        for code_block in soup.find_all('pre', {'class': 'code'}):
            examples.append({
                'code': code_block.get_text(strip=True),
                'language': 'python',  # Assume Jython for Ignition
                'context': self._extract_example_context(code_block)
            })
        
        return {
            'description': soup.find('div', {'class': 'component-description'}).get_text(strip=True) if soup.find('div', {'class': 'component-description'}) else '',
            'properties': properties,
            'events': events,
            'examples': examples
        }
```

### 2. Production Code Analyzer

```python
# ignition-rag/app/analyzers/production_code_analyzer.py
import os
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class ProductionCodeAnalyzer:
    def __init__(self, project_paths: List[str]):
        self.project_paths = project_paths
        self.patterns = {}
        
    def analyze_all_projects(self) -> Dict:
        """Analyze all production Ignition projects"""
        analysis_results = {
            'perspective_views': [],
            'scripts': [],
            'tags': [],
            'patterns': [],
            'metrics': {}
        }
        
        for project_path in self.project_paths:
            if os.path.exists(project_path):
                project_analysis = self.analyze_project(project_path)
                
                # Merge results
                for key in analysis_results:
                    if key != 'metrics':
                        analysis_results[key].extend(project_analysis.get(key, []))
                
                # Aggregate metrics
                for metric_key, value in project_analysis.get('metrics', {}).items():
                    if metric_key not in analysis_results['metrics']:
                        analysis_results['metrics'][metric_key] = 0
                    analysis_results['metrics'][metric_key] += value
        
        # Extract patterns after analyzing all projects
        analysis_results['patterns'] = self._extract_patterns(analysis_results)
        
        return analysis_results
    
    def analyze_project(self, project_path: str) -> Dict:
        """Analyze a single Ignition project"""
        results = {
            'perspective_views': [],
            'scripts': [],
            'tags': [],
            'metrics': {
                'total_views': 0,
                'total_scripts': 0,
                'total_components': 0,
                'complexity_score': 0
            }
        }
        
        project_name = os.path.basename(project_path)
        
        # Analyze Perspective views
        views_path = os.path.join(project_path, 'com.inductiveautomation.perspective', 'views')
        if os.path.exists(views_path):
            results['perspective_views'] = self._analyze_perspective_views(views_path, project_name)
            results['metrics']['total_views'] = len(results['perspective_views'])
        
        # Analyze scripts
        scripts_path = os.path.join(project_path, 'scripts')
        if os.path.exists(scripts_path):
            results['scripts'] = self._analyze_scripts(scripts_path, project_name)
            results['metrics']['total_scripts'] = len(results['scripts'])
        
        # Analyze tags
        tags_path = os.path.join(project_path, 'tags')
        if os.path.exists(tags_path):
            results['tags'] = self._analyze_tags(tags_path, project_name)
        
        return results
    
    def _analyze_perspective_views(self, views_path: str, project_name: str) -> List[Dict]:
        """Extract and analyze Perspective views"""
        views = []
        
        for root, dirs, files in os.walk(views_path):
            if 'view.json' in files:
                view_path = os.path.join(root, 'view.json')
                resource_path = os.path.join(root, 'resource.json')
                
                try:
                    with open(view_path, 'r', encoding='utf-8') as f:
                        view_data = json.load(f)
                    
                    resource_data = {}
                    if os.path.exists(resource_path):
                        with open(resource_path, 'r', encoding='utf-8') as f:
                            resource_data = json.load(f)
                    
                    view_name = os.path.basename(root)
                    
                    analysis = {
                        'type': 'perspective_view',
                        'project': project_name,
                        'name': view_name,
                        'path': os.path.relpath(view_path, views_path),
                        'content': view_data,
                        'resource': resource_data,
                        'metadata': self._extract_view_metadata(view_data, resource_data),
                        'file_hash': self._calculate_file_hash(view_path)
                    }
                    
                    views.append(analysis)
                    
                except Exception as e:
                    print(f"Error analyzing view {view_path}: {e}")
                    continue
        
        return views
    
    def _analyze_scripts(self, scripts_path: str, project_name: str) -> List[Dict]:
        """Analyze Jython/Python scripts"""
        scripts = []
        
        for root, dirs, files in os.walk(scripts_path):
            for file in files:
                if file.endswith('.py'):
                    script_path = os.path.join(root, file)
                    
                    try:
                        with open(script_path, 'r', encoding='utf-8') as f:
                            script_content = f.read()
                        
                        analysis = {
                            'type': 'jython_script',
                            'project': project_name,
                            'name': file[:-3],  # Remove .py extension
                            'path': os.path.relpath(script_path, scripts_path),
                            'content': script_content,
                            'metadata': self._analyze_script_content(script_content),
                            'file_hash': self._calculate_file_hash(script_path)
                        }
                        
                        scripts.append(analysis)
                        
                    except Exception as e:
                        print(f"Error analyzing script {script_path}: {e}")
                        continue
        
        return scripts
    
    def _extract_view_metadata(self, view_data: Dict, resource_data: Dict) -> Dict:
        """Extract metadata from view JSON"""
        metadata = {
            'components_used': [],
            'binding_types': [],
            'complexity_score': 0,
            'has_scripts': False,
            'parameter_count': 0,
            'custom_properties': []
        }
        
        # Extract components recursively
        def extract_components(obj, path=""):
            if isinstance(obj, dict):
                if 'type' in obj:
                    component_type = obj['type']
                    metadata['components_used'].append({
                        'type': component_type,
                        'path': path,
                        'has_custom_props': bool([k for k in obj.keys() if k.startswith('custom.')])
                    })
                    
                    # Check for bindings
                    for key, value in obj.items():
                        if isinstance(value, dict) and 'binding' in str(value):
                            binding_type = value.get('binding', {}).get('type', 'unknown')
                            metadata['binding_types'].append(binding_type)
                
                # Check for embedded scripts
                if 'script' in str(obj):
                    metadata['has_scripts'] = True
                
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        extract_components(value, f"{path}.{key}" if path else key)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_components(item, f"{path}[{i}]")
        
        extract_components(view_data)
        
        # Calculate complexity score
        metadata['complexity_score'] = (
            len(set(c['type'] for c in metadata['components_used'])) * 2 +
            len(metadata['binding_types']) * 1.5 +
            (10 if metadata['has_scripts'] else 0)
        )
        
        return metadata
    
    def _analyze_script_content(self, script_content: str) -> Dict:
        """Analyze Jython script content"""
        metadata = {
            'imports': [],
            'system_functions': [],
            'tag_operations': [],
            'db_operations': [],
            'complexity_score': 0,
            'error_handling': False,
            'logging_usage': False
        }
        
        lines = script_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Extract imports
            if line.startswith('import ') or line.startswith('from '):
                metadata['imports'].append(line)
            
            # Find system function calls
            system_calls = re.findall(r'system\.(\w+)\.(\w+)', line)
            for module, function in system_calls:
                metadata['system_functions'].append(f"system.{module}.{function}")
            
            # Find tag operations
            if 'tag' in line.lower() and any(op in line for op in ['read', 'write', 'browse']):
                metadata['tag_operations'].append(line.strip())
            
            # Find database operations
            if 'system.db' in line:
                metadata['db_operations'].append(line.strip())
            
            # Check for error handling
            if 'try:' in line or 'except' in line:
                metadata['error_handling'] = True
            
            # Check for logging
            if 'logger' in line.lower() or 'log' in line.lower():
                metadata['logging_usage'] = True
        
        # Calculate complexity
        metadata['complexity_score'] = (
            len(metadata['imports']) * 1 +
            len(set(metadata['system_functions'])) * 2 +
            len(metadata['tag_operations']) * 3 +
            len(metadata['db_operations']) * 2 +
            (5 if metadata['error_handling'] else -5) +
            (3 if metadata['logging_usage'] else 0)
        )
        
        return metadata
    
    def _extract_patterns(self, analysis_results: Dict) -> List[Dict]:
        """Extract reusable patterns from analyzed code"""
        patterns = []
        
        # Component usage patterns
        component_usage = {}
        for view in analysis_results['perspective_views']:
            for component in view['metadata']['components_used']:
                comp_type = component['type']
                if comp_type not in component_usage:
                    component_usage[comp_type] = []
                component_usage[comp_type].append({
                    'view': view['name'],
                    'project': view['project'],
                    'path': component['path']
                })
        
        # Identify common patterns
        for comp_type, usages in component_usage.items():
            if len(usages) >= 3:  # Used in at least 3 places
                patterns.append({
                    'type': 'component_pattern',
                    'pattern_name': f"Common {comp_type} Usage",
                    'component_type': comp_type,
                    'usage_count': len(usages),
                    'examples': usages[:5],  # Top 5 examples
                    'confidence_score': min(len(usages) / 10, 1.0)
                })
        
        # Script patterns
        script_patterns = self._extract_script_patterns(analysis_results['scripts'])
        patterns.extend(script_patterns)
        
        return patterns
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return ""
```

### 3. Document Processing Pipeline

```python
# ignition-rag/app/processors/document_processor.py
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from typing import List, Dict, Optional
import json

class IgnitionDocumentProcessor:
    def __init__(self):
        self.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536
        )
        self.chunk_size = 1024
        self.chunk_overlap = 200
    
    def process_production_view(self, view_data: Dict) -> List[Document]:
        """Process a production Perspective view into documents"""
        documents = []
        
        # Main view document
        main_doc = Document(
            text=self._create_view_text(view_data),
            metadata={
                'doc_type': 'perspective_view',
                'source_type': 'production',
                'project': view_data['project'],
                'view_name': view_data['name'],
                'complexity_score': view_data['metadata']['complexity_score'],
                'components_count': len(view_data['metadata']['components_used']),
                'has_bindings': len(view_data['metadata']['binding_types']) > 0,
                'has_scripts': view_data['metadata']['has_scripts'],
                'file_hash': view_data['file_hash'],
                'quality_score': self._calculate_view_quality(view_data)
            }
        )
        documents.append(main_doc)
        
        # Create component-specific documents
        for component in view_data['metadata']['components_used']:
            if component['has_custom_props']:
                comp_doc = Document(
                    text=self._create_component_text(component, view_data),
                    metadata={
                        'doc_type': 'component_usage',
                        'source_type': 'production',
                        'component_type': component['type'],
                        'parent_view': view_data['name'],
                        'project': view_data['project'],
                        'usage_context': component['path'],
                        'quality_score': 0.8  # Production code gets high score
                    }
                )
                documents.append(comp_doc)
        
        return documents
    
    def process_production_script(self, script_data: Dict) -> List[Document]:
        """Process a production Jython script into documents"""
        documents = []
        
        # Main script document
        main_doc = Document(
            text=script_data['content'],
            metadata={
                'doc_type': 'jython_script',
                'source_type': 'production',
                'project': script_data['project'],
                'script_name': script_data['name'],
                'script_path': script_data['path'],
                'complexity_score': script_data['metadata']['complexity_score'],
                'has_error_handling': script_data['metadata']['error_handling'],
                'has_logging': script_data['metadata']['logging_usage'],
                'system_functions': json.dumps(script_data['metadata']['system_functions']),
                'file_hash': script_data['file_hash'],
                'quality_score': self._calculate_script_quality(script_data)
            }
        )
        documents.append(main_doc)
        
        # Create function-specific documents for complex scripts
        if script_data['metadata']['complexity_score'] > 10:
            functions = self._extract_functions(script_data['content'])
            for func_name, func_code in functions.items():
                func_doc = Document(
                    text=func_code,
                    metadata={
                        'doc_type': 'script_function',
                        'source_type': 'production',
                        'function_name': func_name,
                        'parent_script': script_data['name'],
                        'project': script_data['project'],
                        'quality_score': 0.8
                    }
                )
                documents.append(func_doc)
        
        return documents
    
    def process_pattern(self, pattern_data: Dict) -> Document:
        """Process an extracted pattern into a document"""
        return Document(
            text=self._create_pattern_text(pattern_data),
            metadata={
                'doc_type': 'pattern',
                'source_type': 'production',
                'pattern_type': pattern_data['type'],
                'pattern_name': pattern_data['pattern_name'],
                'usage_count': pattern_data.get('usage_count', 0),
                'confidence_score': pattern_data.get('confidence_score', 0.5),
                'quality_score': min(pattern_data.get('usage_count', 0) / 10, 1.0)
            }
        )
    
    def _create_view_text(self, view_data: Dict) -> str:
        """Create searchable text from view data"""
        components = [c['type'] for c in view_data['metadata']['components_used']]
        bindings = view_data['metadata']['binding_types']
        
        text = f"""
Perspective View: {view_data['name']}
Project: {view_data['project']}

Components Used: {', '.join(set(components))}
Binding Types: {', '.join(set(bindings))}
Complexity Score: {view_data['metadata']['complexity_score']}

This is a production Perspective view from the {view_data['project']} project.
It demonstrates real-world usage of {len(set(components))} different component types
with {len(bindings)} bindings configured.

Component Details:
"""
        
        for component in view_data['metadata']['components_used']:
            text += f"- {component['type']} at path {component['path']}\n"
        
        if view_data['metadata']['has_scripts']:
            text += "\nThis view includes embedded scripts for custom behavior."
        
        return text.strip()
    
    def _calculate_view_quality(self, view_data: Dict) -> float:
        """Calculate quality score for a production view"""
        score = 0.5  # Base score for production code
        
        # Bonus for complexity (more sophisticated examples)
        if view_data['metadata']['complexity_score'] > 20:
            score += 0.2
        elif view_data['metadata']['complexity_score'] > 10:
            score += 0.1
        
        # Bonus for having bindings
        if view_data['metadata']['binding_types']:
            score += 0.1
        
        # Bonus for error handling in scripts
        if view_data['metadata']['has_scripts']:
            score += 0.1
        
        # Bonus for reusable patterns
        unique_components = len(set(c['type'] for c in view_data['metadata']['components_used']))
        if unique_components > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_script_quality(self, script_data: Dict) -> float:
        """Calculate quality score for a production script"""
        score = 0.5  # Base score for production code
        
        # Bonus for error handling
        if script_data['metadata']['error_handling']:
            score += 0.2
        
        # Bonus for logging
        if script_data['metadata']['logging_usage']:
            score += 0.1
        
        # Bonus for using system functions properly
        system_funcs = len(script_data['metadata']['system_functions'])
        if system_funcs > 3:
            score += 0.1
        
        # Bonus for reasonable complexity
        complexity = script_data['metadata']['complexity_score']
        if 10 <= complexity <= 30:  # Sweet spot
            score += 0.1
        
        return min(score, 1.0)
```

## 🔍 Query Processing & Retrieval

### Context-Aware Query Engine

```python
# ignition-rag/app/query/context_aware_retriever.py
from llama_index.core import VectorStoreIndex, QueryBundle
from llama_index.core.retrievers import BaseRetriever
from typing import List, Dict, Optional
import json

class IgnitionContextRetriever(BaseRetriever):
    def __init__(self, indexes: Dict[str, VectorStoreIndex], production_weight: float = 0.4):
        self.indexes = indexes
        self.production_weight = production_weight
        self.context_keywords = {
            'perspective': ['view', 'component', 'binding', 'perspective', 'ui', 'interface'],
            'scripting': ['script', 'jython', 'python', 'function', 'gateway', 'tag'],
            'tags': ['tag', 'udt', 'opc', 'device', 'provider', 'historian'],
            'system': ['system', 'gateway', 'config', 'security', 'user', 'role']
        }
    
    async def _aretrieve(self, query_bundle: QueryBundle) -> List[Dict]:
        """Retrieve relevant documents with production bias"""
        query_text = query_bundle.query_str.lower()
        
        # Determine query context
        context = self._determine_context(query_text)
        
        # Build retrieval strategy
        retrieval_plan = self._build_retrieval_plan(context, query_text)
        
        # Execute multi-source retrieval
        all_results = []
        
        for source_type, config in retrieval_plan.items():
            if source_type in self.indexes:
                results = await self._retrieve_from_source(
                    self.indexes[source_type], 
                    query_bundle, 
                    config
                )
                all_results.extend(results)
        
        # Rank and merge results
        ranked_results = self._rank_results(all_results, query_text, context)
        
        return ranked_results[:10]  # Top 10 results
    
    def _determine_context(self, query_text: str) -> str:
        """Determine the primary context of the query"""
        context_scores = {}
        
        for context, keywords in self.context_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_text)
            if score > 0:
                context_scores[context] = score
        
        if context_scores:
            return max(context_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _build_retrieval_plan(self, context: str, query_text: str) -> Dict:
        """Build retrieval plan based on context"""
        plan = {}
        
        if context == 'perspective':
            plan = {
                'production': {'weight': 0.5, 'filters': {'doc_type': 'perspective_view'}},
                'official': {'weight': 0.3, 'filters': {'category': 'perspective'}},
                'patterns': {'weight': 0.2, 'filters': {'pattern_type': 'component_pattern'}}
            }
        elif context == 'scripting':
            plan = {
                'production': {'weight': 0.6, 'filters': {'doc_type': 'jython_script'}},
                'official': {'weight': 0.3, 'filters': {'category': 'scripting'}},
                'community': {'weight': 0.1, 'filters': {'doc_type': 'script'}}
            }
        elif context == 'tags':
            plan = {
                'production': {'weight': 0.4, 'filters': {'doc_type': 'tag_config'}},
                'official': {'weight': 0.4, 'filters': {'category': 'tag'}},
                'patterns': {'weight': 0.2, 'filters': {'pattern_type': 'tag_pattern'}}
            }
        else:
            # General retrieval
            plan = {
                'production': {'weight': 0.4},
                'official': {'weight': 0.3},
                'community': {'weight': 0.2},
                'patterns': {'weight': 0.1}
            }
        
        return plan
    
    def _rank_results(self, results: List[Dict], query_text: str, context: str) -> List[Dict]:
        """Rank results based on relevance and production bias"""
        for result in results:
            score = result.get('similarity_score', 0.0)
            
            # Production bias
            if result.get('source_type') == 'production':
                score *= (1 + self.production_weight)
            
            # Quality score bonus
            quality = result.get('quality_score', 0.5)
            score *= (1 + quality * 0.2)
            
            # Context relevance bonus
            if self._matches_context(result, context):
                score *= 1.1
            
            # Recency bonus for production code
            if result.get('source_type') == 'production' and 'updated_at' in result:
                # Implement recency scoring based on updated_at
                pass
            
            result['final_score'] = score
        
        return sorted(results, key=lambda x: x['final_score'], reverse=True)
    
    def _matches_context(self, result: Dict, context: str) -> bool:
        """Check if result matches the query context"""
        if context == 'perspective':
            return result.get('doc_type') in ['perspective_view', 'component_usage', 'perspective_component']
        elif context == 'scripting':
            return result.get('doc_type') in ['jython_script', 'script_function', 'scripting_function']
        elif context == 'tags':
            return result.get('doc_type') in ['tag_config', 'tag_pattern', 'udt_definition']
        
        return True  # General match
```

## 🔧 Integration with Existing Services

### Enhanced LlamaIndex Service Integration

```python
# Enhancement to existing llama-index-service/app/core/index_manager.py
class IgnitionIndexManager:
    def __init__(self, settings):
        super().__init__(settings)
        self.production_analyzer = ProductionCodeAnalyzer([
            "/usr/local/bin/ignition/data/projects/WHK-Global",
            "/usr/local/bin/ignition/data/projects/QSI_WhiskeyHouseKentucky01",
            "/usr/local/bin/ignition/data/projects/Reporting"
        ])
        
    async def build_ignition_indexes(self):
        """Build specialized indexes for Ignition development"""
        
        # 1. Analyze production code
        production_analysis = self.production_analyzer.analyze_all_projects()
        
        # 2. Scrape official documentation
        docs_scraper = IgnitionDocsExtracter()
        official_docs = await docs_scraper.extract_all_documentation()
        
        # 3. Process all sources into documents
        processor = IgnitionDocumentProcessor()
        all_documents = []
        
        # Process production code
        for view in production_analysis['perspective_views']:
            all_documents.extend(processor.process_production_view(view))
        
        for script in production_analysis['scripts']:
            all_documents.extend(processor.process_production_script(script))
        
        for pattern in production_analysis['patterns']:
            all_documents.append(processor.process_pattern(pattern))
        
        # Process official documentation
        for doc in official_docs:
            all_documents.append(processor.process_official_doc(doc))
        
        # 4. Create specialized indexes
        indexes = {
            'production': self._build_index(
                [doc for doc in all_documents if doc.metadata['source_type'] == 'production']
            ),
            'official': self._build_index(
                [doc for doc in all_documents if doc.metadata['source_type'] == 'official']
            ),
            'patterns': self._build_index(
                [doc for doc in all_documents if doc.metadata['doc_type'] == 'pattern']
            )
        }
        
        return indexes
    
    async def update_from_git_changes(self, changed_files: List[str]):
        """Update indexes when production code changes"""
        for file_path in changed_files:
            if self._is_ignition_file(file_path):
                # Re-analyze changed file
                # Update relevant documents
                # Refresh index
                pass
```

## 📈 Performance Optimization

### Caching Strategy

```python
# ignition-rag/app/cache/rag_cache.py
import redis
import json
import hashlib
from typing import Optional, List, Dict

class RAGCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour default TTL
    
    def get_query_result(self, query: str, context: str) -> Optional[List[Dict]]:
        """Get cached query results"""
        cache_key = self._generate_cache_key(query, context)
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        return None
    
    def cache_query_result(self, query: str, context: str, results: List[Dict]):
        """Cache query results"""
        cache_key = self._generate_cache_key(query, context)
        self.redis.setex(
            cache_key, 
            self.ttl, 
            json.dumps(results, default=str)
        )
    
    def invalidate_production_cache(self, project_name: str):
        """Invalidate cache when production code changes"""
        pattern = f"rag:*:prod:{project_name}"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def _generate_cache_key(self, query: str, context: str) -> str:
        """Generate consistent cache key"""
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"rag:{context}:{query_hash}"
```

## 🔄 Continuous Learning Pipeline

### Feedback Integration

```python
# ignition-rag/app/feedback/learning_pipeline.py
class ContinuousLearningPipeline:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def record_user_feedback(self, query: str, results: List[Dict], feedback: Dict):
        """Record user feedback for continuous improvement"""
        feedback_record = {
            'query': query,
            'retrieved_docs': [r['id'] for r in results],
            'user_rating': feedback.get('rating'),
            'was_helpful': feedback.get('helpful'),
            'corrections': feedback.get('corrections'),
            'context_metadata': feedback.get('context', {})
        }
        
        # Store in database for analysis
        self._store_feedback(feedback_record)
        
        # Update document quality scores
        self._update_quality_scores(results, feedback)
    
    def _update_quality_scores(self, results: List[Dict], feedback: Dict):
        """Update document quality scores based on feedback"""
        rating = feedback.get('rating', 3)
        adjustment = (rating - 3) * 0.05  # -0.1 to +0.1 adjustment
        
        for result in results:
            doc_id = result['id']
            current_score = result.get('quality_score', 0.5)
            new_score = max(0.0, min(1.0, current_score + adjustment))
            
            # Update in database
            self._update_document_quality(doc_id, new_score)
```

## 🚀 Deployment Configuration

### Docker Service Configuration

```yaml
# ignition-rag service addition to docker-compose.yml
ignition-rag:
  build: ./ignition-rag
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - POSTGRES_VECTOR_URL=postgresql://admin:${DB_PASSWORD}@vector-db:5432/whk_vectors
    - REDIS_URL=redis://redis:6379
    - IGNITION_PROJECTS_PATH=/ignition-data/projects
    - SCRAPING_INTERVAL=86400  # Daily scraping
    - ANALYSIS_INTERVAL=3600   # Hourly analysis
  volumes:
    - gw-data:/ignition-data:ro
    - ./ignition-rag/storage:/storage
    - ./ignition-docs:/docs
  networks:
    - whk-network
  ports:
    - "8081:8080"
  depends_on:
    - vector-db
    - redis
    - ignition
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3

# Add periodic sync service
ignition-rag-sync:
  build: ./ignition-rag
  command: ["python", "-m", "sync_production_code"]
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - POSTGRES_VECTOR_URL=postgresql://admin:${DB_PASSWORD}@vector-db:5432/whk_vectors
    - REDIS_URL=redis://redis:6379
    - IGNITION_PROJECTS_PATH=/ignition-data/projects
  volumes:
    - gw-data:/ignition-data:ro
  networks:
    - whk-network
  depends_on:
    - ignition-rag
  restart: unless-stopped
```

## 📊 Monitoring & Analytics

### RAG Performance Metrics

```python
# ignition-rag/app/metrics/rag_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics definitions
query_counter = Counter('rag_queries_total', 'Total RAG queries', ['context', 'source_type'])
query_duration = Histogram('rag_query_duration_seconds', 'RAG query duration')
cache_hits = Counter('rag_cache_hits_total', 'RAG cache hits')
cache_misses = Counter('rag_cache_misses_total', 'RAG cache misses')
document_quality = Gauge('rag_document_quality_avg', 'Average document quality score', ['source_type'])

class RAGMetrics:
    @staticmethod
    def record_query(context: str, source_type: str, duration: float, cache_hit: bool):
        query_counter.labels(context=context, source_type=source_type).inc()
        query_duration.observe(duration)
        
        if cache_hit:
            cache_hits.inc()
        else:
            cache_misses.inc()
    
    @staticmethod
    def update_quality_metrics(quality_scores: Dict[str, float]):
        for source_type, avg_quality in quality_scores.items():
            document_quality.labels(source_type=source_type).set(avg_quality)
```

---

This RAG implementation provides a comprehensive foundation for Ignition-specific AI assistance, with strong emphasis on learning from your production codebase while maintaining high performance and accuracy through caching and quality scoring systems.