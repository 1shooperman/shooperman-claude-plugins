---
name: update
description: Update the marketplace to the latest version, then update each plugin to the version specific.
allowed-tools: []
user-invocable: true
model: haiku
---

## Instructions

When the user invokes this skill or asks to update the marketplace version:
- run `claude plugin marketplace update ${marketplace.json:name}`
- update each plug-in in this marketplace with `claude plugin update ${plugin-name}@${marketplace.json:name}`
- tell the user to run `/reload-plugins` to pick up the changes

