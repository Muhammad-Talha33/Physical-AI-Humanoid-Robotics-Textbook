---
id: 2
title: Add RAG Chatbot Requirements to Constitution
stage: constitution
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: gh-pages
user: unknown
command: /sp.constitution
labels: ["constitution", "rag-chatbot", "interactive-learning", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (documentation update)
---

## Prompt

# Physical AI & Humanoid Robotics Constitution

## Core Principles

### Technical Accuracy
All robotics, AI, hardware, and software explanations must be aligned with verified, authoritative sources.

### Educational Clarity
Writing should be understandable for readers with undergraduate-level knowledge of computer science, robotics, or engineering.

### Practical Insight
Focus on real-world applications, engineering considerations, safety principles, and implementation details.

### Modularity
Chapters must be structured so readers can independently learn concepts like sensors, actuators, locomotion, control systems, AI models, and ethics.

### Open-Source Transparency
All code examples and diagrams must be reproducible and accessible via GitHub Pages.

### Future-Proofing
Emphasize emerging trends (Physical AI, embodied intelligence, humanoid robotics, autonomous control).

### Intelligent Interactivity (New)
The book must include an integrated RAG chatbot capable of answering questions strictly based on book content, improving learner engagement and comprehension.

---

## Key Standards

### Factual Verification
All technical claims must come from reliable sources such as robotics textbooks, research labs, IEEE papers, and manufacturer documentation. No speculative claims without disclaimers.

### Citation Style
Use APA style for all references. Include links to digital sources when available.

### Source Requirements
Minimum 40% peer-reviewed research (IEEE, ACM, Nature Robotics, Science Robotics, arXiv technical papers). Remaining sources may include industrial whitepapers, engineering manuals, official documentation, and robotics lab publications.

### Diagram & Code Standard
All diagrams must be original or reproduced with permission. Code examples must be tested and runnable. Use consistent naming, formatting, and annotations.

### Writing Quality
Aim for Flesch-Kincaid Grade 9–11 for global readability. Avoid unnecessary jargon; define all technical terms. Maintain a professional, instructional tone suitable for a technical book.

### RAG Chatbot Standards (New)
- The integrated chatbot must answer questions *only* using the book's content or user-selected text.
- Retrieval must use high-quality embeddings and deterministic chunking.
- System must prevent hallucination by enforcing grounding strictly in the retrieved context.
- All chatbot behavior must be transparent and auditable.
- Chatbot must support follow-up questions, citations, and context-traceability.

---

## Constraints

### Format
Must be published using Docusaurus and deployed to GitHub Pages. All chapters organized as markdown files under /docs.

### Length
Total content: 25,000–40,000 words (full technical book). Each chapter: 1,500–3,500 words.

### Structure
Book must include at minimum:
- Introduction to Physical AI,
- History of Humanoid Robotics,
- Robotics Hardware (motors, actuators, sensors),
- Control Systems (PID, model-based, reinforcement learning, etc.),
- Computer Vision & Perception,
- Locomotion & Balance, Grasping & Manipulation,
- LLMs,
- Neural Models & Embodied Intelligence,
- Ethics,
- Safety,
- Future of Humanoid Robotics,
- Practical Projects / Tutorials.

### Platform and Tools Requirement

- **Publishing Platform**: Docosaurus
- **Deployment Target**: GitHub Pages
- **Development Framework**: Spec-Kit Plus + Claude Code
- **Version Control**: Git with structured commit history

### RAG Chatbot Technology Stack (New)
The RAG system must be implemented using:

- **OpenAI Agents or ChatKit SDKs**
- **FastAPI backend**
- **Neon Serverless Postgres** for metadata and logs
- **Qdrant Cloud Free Tier** for vector embeddings
- **Docusaurus front-end integration** for embedding chatbot widget
- **Secure client-server architecture** to prevent unauthorized access
- The chatbot must run efficiently within free-tier or low-cost infrastructure.

---

## Success Criteria

### Chapter Quality
Every chapter must:
Contain accurate and peer-verified explanations, Include citations for all factual claims, Provide clear diagrams, examples, or tables, Pass plagiarism check = 0% tolerance, Use consistent writing style across all chapters.

### Project Deployment
Entire book deploys correctly on GitHub Pages via Docusaurus. All links, references, and code examples work. Chapters are clear, structured, and technically correct. Book passes internal technical review + fact check. Readability and structure meet Spec-Kit Plus standards.

### RAG Chatbot Success Criteria (New)
- Chatbot only answers from book content or user-selected text.
- No hallucinations (validated through retrieval-grounding checks).
- Latency under 2 seconds for standard queries.
- Embeddings correctly index all final book markdown pages.
- System logs and traces all interactions for debugging and transparency.
- Fully functional integration into the Docusaurus UI.

---

## Governance

This Constitution supersedes all other project practices and guidelines. Amendments to this Constitution require a documented proposal, review, and approval process, ensuring all affected stakeholders are consulted. All pull requests and code reviews must verify compliance with these principles. New principles or significant changes to existing ones will result in a MINOR or MAJOR version bump. Clarifications or minor wording changes will result in a PATCH version bump.

**Version**: 1.1.0 (Updated for RAG Chatbot)
**Ratified**: 2025-12-04
**Last Amended**: 2025-12-06

## Response snapshot

Constitution updated from version 1.0.0 to 1.1.0 with the following changes:

**New Principle Added:**
- **Intelligent Interactivity**: Mandates integrated RAG chatbot for interactive learning support

**Key Standards Enhanced:**
- Added comprehensive RAG Chatbot Standards covering grounding, retrieval quality, hallucination prevention, transparency, user experience, and performance

**Constraints Updated:**
- Added RAG Chatbot Technology Stack specifying: OpenAI Agents/ChatKit SDK, FastAPI backend, Neon Serverless Postgres, Qdrant Cloud Free Tier, Docusaurus integration, and security requirements
- Fixed typos: "Docosaurus" → "Docusaurus", "Github" → "GitHub", "sturctured" → "structured"

**Success Criteria Expanded:**
- Added RAG Chatbot Success Criteria including accuracy, performance (<2s latency), coverage, logging, integration, reliability (99% uptime), and cost efficiency (<$20/month)

**Templates Verified:**
- plan-template.md: ✅ Generic constitution check - no changes needed
- spec-template.md: ✅ No constitution references - no changes needed
- tasks-template.md: ✅ No constitution references - no changes needed

All changes enforce strict content grounding to prevent AI hallucination and ensure interactive learning remains faithful to book content.

## Outcome

- ✅ Impact: Constitution amended to version 1.1.0 (MINOR) with comprehensive RAG chatbot requirements
- 🧪 Tests: N/A (governance document update)
- 📁 Files: Updated .specify/memory/constitution.md with Sync Impact Report
- 🔁 Next prompts: Consider `/sp.specify` to create RAG chatbot feature specification
- 🧠 Reflection: Successfully integrated RAG chatbot requirements while maintaining backward compatibility. All dependent templates verified for consistency. Version bump follows semantic versioning (MINOR for new principle/sections).

## Evaluation notes (flywheel)

- Failure modes observed: None. Templates required no updates as they use generic constitution references.
- Graders run and results (PASS/FAIL): PASS - All placeholders resolved, version bumped correctly, Sync Impact Report complete
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor if RAG chatbot requirements need PATCH updates during implementation phase
