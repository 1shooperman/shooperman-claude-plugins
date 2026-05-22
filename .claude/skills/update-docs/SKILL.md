---
name: update-docs
description: Update the local plugin marketplace docs accordingly.
allowed-tools: [Bash, Read, Bash(git log *)]
user-invocable: true
---

## Instruction

Read each of the plug-ins in the ./plugins folder and update their respective README.md files with basic usage and description as outlined in ./templates/README_TEMPLATE.md

1. The primary README.md (at root) is the only README that should not follow the template structure. 
2. The primary README.md should be kept up to date with top level information.
3. DO NOT conflate internal dependency references with user invokable skills.

## Arguments

The user invoked this with: $ARGUMENTS

## Instructions

When this skill is invoked:

1. Parse the arguments provided by the user
2. Update the README as needed based on changes in the git log