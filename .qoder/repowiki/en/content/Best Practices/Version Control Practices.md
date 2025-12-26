# Version Control Practices

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [.gitignore](file://.gitignore)
- [sources/dehergne-a.cli](file://sources/dehergne-a.cli)
- [sources/dehergne-b.cli](file://sources/dehergne-b.cli)
- [sources/dehergne-c.cli](file://sources/dehergne-c.cli)
- [sources/dehergne-d.cli](file://sources/dehergne-d.cli)
- [sources/dehergne-e.cli](file://sources/dehergne-e.cli)
- [sources/dehergne-f.cli](file://sources/dehergne-f.cli)
- [sources/dehergne-g.cli](file://sources/dehergne-g.cli)
- [sources/dehergne-h.cli](file://sources/dehergne-h.cli)
- [sources/dehergne-i.cli](file://sources/dehergne-i.cli)
- [sources/dehergne-j.cli](file://sources/dehergne-j.cli)
- [sources/dehergne-k.cli](file://sources/dehergne-k.cli)
- [sources/dehergne-l.cli](file://sources/dehergne-l.cli)
- [sources/dehergne-m.cli](file://sources/dehergne-m.cli)
- [sources/dehergne-n.cli](file://sources/dehergne-n.cli)
- [sources/dehergne-o.cli](file://sources/dehergne-o.cli)
- [sources/dehergne-p.cli](file://sources/dehergne-p.cli)
- [sources/dehergne-q.cli](file://sources/dehergne-q.cli)
- [sources/dehergne-r.cli](file://sources/dehergne-r.cli)
- [sources/dehergne-s.cli](file://sources/dehergne-s.cli)
- [sources/dehergne-t.cli](file://sources/dehergne-t.cli)
- [sources/dehergne-u.cli](file://sources/dehergne-u.cli)
- [sources/dehergne-v.cli](file://sources/dehergne-v.cli)
- [sources/dehergne-w.cli](file://sources/dehergne-w.cli)
- [sources/dehergne-x.cli](file://sources/dehergne-x.cli)
- [sources/dehergne-y.cli](file://sources/dehergne-y.cli)
- [sources/dehergne-z.cli](file://sources/dehergne-z.cli)
- [sources/dehergne-0-abrev.cli](file://sources/dehergne-0-abrev.cli)
- [extras/doc/Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)
- [extras/scripts/updateFromTemplate.sh](file://extras/scripts/updateFromTemplate.sh)
- [inferences/README.md](file://inferences/README.md)
- [identifications/README.md](file://identifications/README.md)
- [structures/sources.str](file://structures/sources.str)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure and File Organization](#project-structure-and-file-organization)
3. [Branching Strategy for Collaborative Work](#branching-strategy-for-collaborative-work)
4. [Commit Message Conventions](#commit-message-conventions)
5. [Merge Conflict Resolution Procedures](#merge-conflict-resolution-procedures)
6. [Database Change Management Principles](#database-change-management-principles)
7. [Gitignore Configuration for Generated Files](#gitignore-configuration-for-generated-files)
8. [Pull Request and Peer Review Workflow](#pull-request-and-peer-review-workflow)
9. [Conclusion](#conclusion)

## Introduction

This document outlines the recommended Git-based version control practices for collaborative work in the dehergne repository. The repository contains transcriptions of Joseph Dehergne's biographical dictionary of Jesuit missionaries in China, with contributions from multiple researchers working on transcription and identification tasks. The version control system must support concurrent work on different entries while maintaining data integrity and enabling effective collaboration. This document provides guidance on branching strategies, commit conventions, conflict resolution, and workflow practices to ensure smooth collaboration among contributors.

## Project Structure and File Organization

The dehergne repository follows a structured organization to manage transcriptions, identifications, and related resources. The primary content is organized into multiple `.cli` files in the `sources/` directory, with one file per alphabetical section (e.g., `dehergne-a.cli`, `dehergne-b.cli`). This segmentation prevents overly large files and enables parallel work on different sections of the biographical dictionary.

The repository includes several key directories:
- `sources/`: Contains the main transcription files in `.cli` format, following the Kleio markup language for historical source encoding.
- `inferences/`: Contains inference rules used to derive personal attributes and relationships from co-occurring entities in acts or events.
- `identifications/`: Contains exports of the identification process for people and other entities, supporting record linking across sources.
- `extras/doc/`: Contains documentation on transcription formats and procedures.
- `structures/`: Contains structural definitions for the source-act-person model used in the transcriptions.

This organization supports the collaborative workflow by separating content from processing rules and documentation, allowing contributors to focus on specific aspects of the project.

**Section sources**
- [README.md](file://README.md)
- [extras/doc/Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)
- [structures/sources.str](file://structures/sources.str)

## Branching Strategy for Collaborative Work

The dehergne repository employs a feature branch workflow to support concurrent transcription and identification tasks. Contributors should create feature branches for individual entries or thematic groups of entries, following the naming convention `feature/transcribe-[lastname]` for single entries or `feature/transcribe-[letter]` for alphabetical sections.

For example, when transcribing the entry for António de Abreu, a contributor would create a branch named `feature/transcribe-antonio-de-abreu`. When working on all entries beginning with the letter "A", the branch would be named `feature/transcribe-a`. This approach allows multiple contributors to work simultaneously on different entries without conflicts.

For identification tasks, use the naming convention `feature/identify-[entity-type]`, such as `feature/identify-locations` for geographic entity identification or `feature/identify-people` for person record linking. This separation ensures that transcription and identification work can proceed in parallel.

All feature branches should be created from the main branch and regularly synchronized with upstream changes to minimize merge conflicts. When a feature branch is complete, it should be merged into the main branch through a pull request following the peer review process outlined in this document.

**Section sources**
- [README.md](file://README.md)
- [extras/doc/Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)

## Commit Message Conventions

Commit messages in the dehergne repository should follow a standardized format to clearly describe changes to `.cli` files and identification rules. The convention uses a prefix indicating the type of change, followed by a concise description of the modification.

For transcription changes, use prefixes such as:
- `transcribe: add entry for [Name]` - for adding new biographical entries
- `transcribe: update [Name]` - for modifying existing entries
- `transcribe: correct [Name]` - for fixing errors in entries

For identification rule changes, use prefixes such as:
- `identify: add rule for [Entity Type]` - for adding new identification rules
- `identify: update rule for [Entity Type]` - for modifying existing rules
- `identify: remove rule for [Entity Type]` - for removing obsolete rules

For structural changes to the transcription format or processing rules:
- `structure: update [Component]` - for changes to structure files
- `inference: add rule for [Relationship Type]` - for new inference rules

Each commit should focus on a single logical change and include a detailed description in the commit body explaining the rationale for the change, especially when resolving ambiguities in the source material. This practice ensures that the repository history provides a clear audit trail of transcription decisions and identification logic.

**Section sources**
- [sources/dehergne-a.cli](file://sources/dehergne-a.cli)
- [inferences/README.md](file://inferences/README.md)
- [extras/doc/Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)

## Merge Conflict Resolution Procedures

Merge conflicts in the dehergne repository typically occur when multiple contributors edit related entities in different feature branches. For example, one contributor might update a biographical entry while another adds identification links to the same person. The following procedure should be followed to resolve such conflicts:

1. When a merge conflict is detected, first analyze the nature of the conflicting changes by examining the affected files and line ranges.
2. For conflicts in `.cli` files involving the same entry, preserve both sets of changes by combining the modifications. For example, if one branch adds a new attribute and another modifies an existing one, include both changes in the resolved version.
3. For conflicts involving identification links, verify that both sets of links are valid and include them in the resolved version. Use the `same_as` attribute to maintain connections between related entities.
4. After resolving the conflict, test the changes by processing the `.cli` file to ensure the syntax remains valid and the data imports correctly.
5. Document the resolution in the merge commit message, explaining how the conflicting changes were reconciled.

When conflicts involve structural changes (e.g., updates to `sources.str`), consult with other contributors to determine the appropriate resolution. In cases of uncertainty, preserve the most recent changes and open an issue to discuss the optimal approach.

**Section sources**
- [sources/dehergne-a.cli](file://sources/dehergne-a.cli)
- [structures/sources.str](file://structures/sources.str)
- [identifications/README.md](file://identifications/README.md)

## Database Change Management Principles

The dehergne repository follows the principle of never modifying the database directly. All changes to the data must be made through updates to the source files in the `sources/` directory. This approach ensures that all modifications are tracked in version control and can be reviewed, reverted, or audited as needed.

The workflow for making changes is as follows:
1. Create a feature branch for the desired changes.
2. Modify the appropriate `.cli` file(s) to reflect the updated information.
3. Commit the changes with a descriptive message following the commit message conventions.
4. Open a pull request for peer review.
5. After approval, merge the changes into the main branch.
6. The database is automatically updated through the processing pipeline that converts `.cli` files to `.xml` format for import.

This indirect approach to database modification provides several benefits:
- Complete audit trail of all changes through Git history
- Ability to review changes before they affect the database
- Easy rollback of erroneous changes by reverting commits
- Consistent synchronization between source files and database content

Contributors should never attempt to modify the database directly, even for minor corrections. All changes, regardless of size, must go through the source file update process.

**Section sources**
- [README.md](file://README.md)
- [sources/dehergne-a.cli](file://sources/dehergne-a.cli)
- [structures/sources.str](file://structures/sources.str)

## Gitignore Configuration for Generated Files

The `.gitignore` file in the dehergne repository is configured to manage temporary and generated files, preventing them from being committed to version control. This configuration ensures that only source files and essential configuration are tracked, reducing repository bloat and avoiding conflicts over transient files.

The current `.gitignore` configuration includes patterns for:
- IDE and editor files (`.DS_Store`, `.pyc`, `.html`, `.dot`)
- Virtual environment directories (`.venv/`)
- Log files (`kleio_service.log`)
- Database files (`database/sqlite/*`)
- Backup and temporary files (`*.old`, `*.ids`)
- Version tracking files (`versions.txt`)

This configuration allows contributors to use their preferred development tools without polluting the repository with local environment files. The focus remains on the core content files (`.cli`, `.xml`, `.str`) and documentation, which are the only files that need to be shared across the team.

When new types of generated files are created by processing tools, they should be added to `.gitignore` to maintain this clean separation between source and derived content.

**Section sources**
- [.gitignore](file://.gitignore)
- [README.md](file://README.md)

## Pull Request and Peer Review Workflow

The dehergne repository uses a pull request (PR) workflow to ensure quality control and knowledge sharing among contributors. This process provides a structured mechanism for peer review of transcriptions and identifications before they are merged into the main branch.

The recommended PR workflow is as follows:

1. A contributor completes work on a feature branch and pushes it to the remote repository.
2. The contributor creates a pull request from the feature branch to the main branch, providing a clear description of the changes and their rationale.
3. The PR is assigned to at least one other contributor for review. For significant changes, multiple reviewers may be appropriate.
4. Reviewers examine the changes, focusing on:
   - Accuracy of transcription against the source material
   - Consistency with existing entries and formatting conventions
   - Validity of identification links and inference rules
   - Adherence to commit message conventions
5. Reviewers provide feedback through comments on the PR, suggesting improvements or requesting clarification.
6. The contributor addresses the feedback by making additional commits to the feature branch.
7. Once all reviewers approve the changes, the PR is merged into the main branch.

For transcription PRs, reviewers should verify that the `.cli` syntax is correct and that the content accurately reflects the source material. For identification PRs, reviewers should check that the links are supported by evidence and that the rules are correctly formulated.

This peer review process ensures high-quality contributions while fostering collaboration and knowledge transfer among team members.

**Section sources**
- [README.md](file://README.md)
- [extras/doc/Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)
- [inferences/README.md](file://inferences/README.md)

## Conclusion

The version control practices outlined in this document provide a robust framework for collaborative work on the dehergne repository. By following the recommended branching strategy, commit conventions, and review workflow, contributors can work efficiently on transcription and identification tasks while maintaining data integrity and quality. The principle of indirect database modification through source file updates ensures that all changes are properly tracked and reviewed. These practices support the long-term sustainability of the project by creating a clear audit trail and enabling effective collaboration among researchers. Adherence to these guidelines will help maintain the high standards of scholarship required for this important historical resource.