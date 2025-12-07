---
id: 001
title: Update constitution with ChatKit UI requirements
stage: constitution
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-rag-chatbot-embeddings
user: user
command: /sp.constitution
labels: ["constitution", "chatkit", "ui-standards", "rag-chatbot", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (no test files)
---

## Prompt

```text
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

### Conversational Interface (NEW)
The RAG chatbot MUST include a modern, intuitive UI built using **OpenAI ChatKit**, fully
embedded inside the Docusaurus book.

**Rationale**: Ensures a seamless, professional user experience consistent with modern AI
assistants and aligns with project requirements for ChatKit-based UI development.

[... Complete user input with all sections including Chat UI Standards, Frontend Integration
Constraints, Additional Chat UI Requirements, Chat UI Success Criteria, and UI/Chatbot
Governance as provided in the original prompt ...]
```

## Response snapshot

Successfully updated the Physical AI & Humanoid Robotics Constitution from version 1.1.0 to 1.2.0.

**Key Changes**:
- Added new principle: **Conversational Interface** mandating OpenAI ChatKit for RAG chatbot UI
- Added **Chat UI Standards** section with framework requirements, UI integration, interaction requirements, and reliability standards
- Added **Frontend Integration Constraints** specifying React component location and backend URL
- Added **Additional Chat UI Requirements** detailing ChatKit primitives, backend integration, text-selection mode, and Neon Postgres logging
- Added **Chat UI Success Criteria** with performance metrics
- Added **UI/Chatbot Governance** subsection for UI change requirements

All template files verified for consistency. No conflicts detected.

## Outcome

- ✅ Impact: Constitution updated with comprehensive ChatKit UI requirements and standards (v1.1.0 → v1.2.0)
- 🧪 Tests: N/A (documentation update)
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: Consider updating feature specification for 001-rag-chatbot-embeddings to include ChatKit UI implementation tasks
- 🧠 Reflection: The constitution now clearly defines UI framework requirements (OpenAI ChatKit) and integration patterns, providing concrete implementation guidance for the RAG chatbot frontend

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS - all placeholders filled, version bumped correctly, sync impact report accurate
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
