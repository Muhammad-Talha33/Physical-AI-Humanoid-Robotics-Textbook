<!-- Sync Impact Report:
Version change: 1.0.0 -> 1.1.0 (MINOR - Added RAG Chatbot principle and requirements)
List of modified principles:
  - Added: Intelligent Interactivity (new principle)
  - Modified: Key Standards (added RAG Chatbot Standards subsection)
  - Modified: Constraints (added RAG Chatbot Technology Stack subsection)
  - Modified: Success Criteria (added RAG Chatbot Success Criteria subsection)
  - Fixed typos: "Docosaurus" -> "Docusaurus", "Github" -> "GitHub", "sturctured" -> "structured"
Added sections:
  - Intelligent Interactivity principle
  - RAG Chatbot Standards
  - RAG Chatbot Technology Stack
  - RAG Chatbot Success Criteria
Removed sections: None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (verified - generic constitution check)
  ✅ .specify/templates/spec-template.md (verified - no constitution references)
  ✅ .specify/templates/tasks-template.md (verified - no constitution references)
  ✅ .specify/templates/commands/*.md (no command files found)
  ⚠️ README.md (not checked - file path not confirmed)
  ⚠️ docs/quickstart.md (not checked - file path not confirmed)
Follow-up TODOs:
  - Verify README.md references constitution principles if file exists
  - Verify docs/quickstart.md references constitution if file exists
  - Consider creating spec for RAG chatbot feature implementation
-->
# Physical AI & Humanoid Robotics Constitution

## Core Principles

### Technical Accuracy
All robotics, AI, hardware, and software explanations MUST be aligned with verified,
authoritative sources such as robotics textbooks, research labs, IEEE papers, and
manufacturer documentation.

**Rationale**: Ensures the book provides reliable, trustworthy information that readers
can confidently use in academic and professional contexts.

### Educational Clarity
Writing MUST be understandable for readers with undergraduate-level knowledge of computer
science, robotics, or engineering. Technical terms MUST be defined on first use.

**Rationale**: Makes advanced robotics concepts accessible to a broader audience while
maintaining technical rigor.

### Practical Insight
Content MUST focus on real-world applications, engineering considerations, safety
principles, and implementation details rather than purely theoretical concepts.

**Rationale**: Bridges the gap between academic knowledge and practical robotics
development, enabling readers to apply concepts in real projects.

### Modularity
Chapters MUST be structured so readers can independently learn concepts like sensors,
actuators, locomotion, control systems, AI models, and ethics without requiring
sequential reading.

**Rationale**: Supports diverse learning paths and allows readers to focus on topics
most relevant to their interests or projects.

### Open-Source Transparency
All code examples and diagrams MUST be reproducible and accessible via GitHub Pages.
Code MUST be tested and runnable. Diagrams MUST be original or reproduced with
permission.

**Rationale**: Enables readers to verify, experiment with, and build upon the provided
examples, fostering hands-on learning.

### Future-Proofing
Content MUST emphasize emerging trends including Physical AI, embodied intelligence,
humanoid robotics, and autonomous control systems.

**Rationale**: Prepares readers for the evolving landscape of robotics and ensures the
book remains relevant as the field advances.

### Intelligent Interactivity
The book MUST include an integrated RAG (Retrieval-Augmented Generation) chatbot capable
of answering questions strictly based on book content or user-selected text, improving
learner engagement and comprehension.

**Rationale**: Provides interactive learning support, enabling readers to get instant
clarification on concepts without leaving the reading experience. Ensures answers are
grounded in the book's content, preventing misinformation.

## Key Standards

### Factual Verification
All technical claims MUST come from reliable sources. No speculative claims without
explicit disclaimers stating the speculative nature.

**Sources**: Robotics textbooks, research labs, IEEE papers, manufacturer documentation,
peer-reviewed journals, official SDK documentation.

### Citation Style
All references MUST use APA style. Digital sources MUST include accessible URLs when
available.

**Format**: (Author, Year) in-text citations with full references in bibliography.

### Source Requirements
Minimum 40% of all citations MUST be from peer-reviewed research including IEEE, ACM,
Nature Robotics, Science Robotics, and arXiv technical papers.

Remaining sources MAY include:
- Industrial whitepapers from recognized robotics companies
- Engineering manuals and official documentation
- Robotics lab publications from accredited institutions

### Diagram & Code Standard
**Diagrams**: MUST be original or reproduced with explicit permission. MUST include
clear labels and captions. MUST follow consistent styling.

**Code Examples**: MUST be tested and runnable. MUST use consistent naming conventions
and formatting. MUST include comments for non-obvious logic. MUST specify dependencies
and environment requirements.

### Writing Quality
**Readability**: Target Flesch-Kincaid Grade 9–11 for global accessibility.

**Style**: Professional and instructional tone. Avoid unnecessary jargon. Define all
technical terms on first use. Use active voice when possible.

**Consistency**: Maintain consistent terminology, formatting, and structure across all
chapters.

### RAG Chatbot Standards
The integrated chatbot MUST adhere to the following standards:

**Grounding**: Chatbot MUST answer questions ONLY using the book's content or
user-selected text. MUST NOT generate information beyond retrieved context.

**Retrieval Quality**: MUST use high-quality embeddings (e.g., OpenAI text-embedding-3)
and deterministic chunking strategies to ensure accurate context retrieval.

**Hallucination Prevention**: System MUST enforce strict grounding in retrieved context.
When insufficient context exists, chatbot MUST respond with "I cannot find information
about this in the book content" rather than generating unsupported answers.

**Transparency**: All chatbot behavior MUST be auditable. System MUST log queries,
retrieved chunks, and responses for debugging and quality assurance.

**User Experience**: Chatbot MUST support follow-up questions, provide citations to
specific chapters/sections, and maintain conversational context within a session.

**Performance**: Response latency MUST be under 2 seconds for standard queries.

## Constraints

### Format
Book MUST be published using Docusaurus and deployed to GitHub Pages. All chapters MUST
be organized as markdown files under `/docs` directory.

**Structure**: Use Docusaurus sidebars for navigation. Maintain consistent front matter
in all markdown files.

### Length
**Total Content**: 25,000–40,000 words (comprehensive technical book)

**Per Chapter**: 1,500–3,500 words

**Rationale**: Ensures sufficient depth while maintaining readability and focus.

### Structure
Book MUST include at minimum the following topics:

- Introduction to Physical AI
- History of Humanoid Robotics
- Robotics Hardware (motors, actuators, sensors)
- Control Systems (PID, model-based, reinforcement learning)
- Computer Vision & Perception
- Locomotion & Balance
- Grasping & Manipulation
- Large Language Models (LLMs)
- Neural Models & Embodied Intelligence
- Ethics in Robotics
- Safety Considerations
- Future of Humanoid Robotics
- Practical Projects / Tutorials

### Platform and Tools Requirement

**Publishing Platform**: Docusaurus (React-based static site generator)

**Deployment Target**: GitHub Pages (static hosting)

**Development Framework**: Spec-Kit Plus + Claude Code for planning, specification, and
assisted writing

**Version Control**: Git with structured commit history following conventional commit
format

### RAG Chatbot Technology Stack
The RAG system MUST be implemented using the following technology stack:

**AI Framework**: OpenAI Agents SDK or ChatKit SDK for conversational AI capabilities

**Backend API**: FastAPI for RESTful API endpoints handling chat requests

**Database**: Neon Serverless Postgres for metadata storage, user logs, and session
management

**Vector Store**: Qdrant Cloud Free Tier for storing and querying document embeddings

**Frontend Integration**: Docusaurus front-end integration using custom React component
or plugin for embedding chatbot widget

**Architecture**: Secure client-server architecture with API authentication to prevent
unauthorized access and abuse

**Infrastructure**: System MUST run efficiently within free-tier or low-cost
infrastructure constraints (Neon free tier, Qdrant free tier, minimal API costs)

**Security**: MUST implement rate limiting, API key protection, input sanitization, and
CORS policies

## Success Criteria

### Chapter Quality
Every chapter MUST satisfy all of the following:

- Contain accurate and peer-verified explanations
- Include citations for all factual claims
- Provide clear diagrams, examples, or tables
- Pass plagiarism check with 0% tolerance for copied content
- Use consistent writing style matching other chapters
- Meet readability targets (Flesch-Kincaid Grade 9–11)

### Project Deployment
The complete book MUST satisfy all of the following:

- Deploy correctly on GitHub Pages via Docusaurus without build errors
- All internal links, external references, and code examples work correctly
- Chapters are clear, well-structured, and technically accurate
- Book passes internal technical review and fact-checking process
- Readability and structure meet Spec-Kit Plus standards
- Navigation is intuitive and consistent across all pages

### RAG Chatbot Success Criteria
The integrated RAG chatbot system MUST satisfy all of the following:

**Accuracy**: Chatbot answers ONLY from book content or user-selected text with no
hallucinations (validated through retrieval-grounding checks)

**Performance**: Response latency under 2 seconds for standard queries (measured at
95th percentile)

**Coverage**: Embeddings correctly index all final book markdown pages with proper
chunking

**Logging**: System logs and traces all interactions including query, retrieved context,
and response for debugging and transparency

**Integration**: Fully functional integration into Docusaurus UI with intuitive user
interface

**Reliability**: System maintains 99% uptime and handles graceful degradation when
external services are unavailable

**Cost Efficiency**: Operates within free-tier limits or minimal monthly cost (<$20/month)

## Governance

### Authority
This Constitution supersedes all other project practices and guidelines. In case of
conflict, Constitution principles take precedence.

### Amendment Process
Amendments to this Constitution require:

1. Documented proposal with rationale
2. Review of impact on existing content and templates
3. Approval process ensuring all affected stakeholders are consulted
4. Update of Sync Impact Report documenting changes

### Version Bump Policy
**MAJOR**: Backward incompatible governance changes or principle removals/redefinitions

**MINOR**: New principles/sections added or materially expanded guidance

**PATCH**: Clarifications, wording improvements, typo fixes, non-semantic refinements

### Compliance
All pull requests and code reviews MUST verify compliance with these principles.
Violations MUST be documented in the Complexity Tracking section of plan.md with
justification.

### Review Cadence
Constitution MUST be reviewed at major project milestones (e.g., completion of each
module) to ensure continued relevance and effectiveness.

---

**Version**: 1.1.0 | **Ratified**: 2025-12-04 | **Last Amended**: 2025-12-06
