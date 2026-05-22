---
name: team-builder
description: Use this skill when the user asks for help building a team
allowed-tools: [Bash(sqlite3 *)]
argument-hint: <required-arg> [optional-arg]
user-invocable: true
---

# Instructions

you should always ground the user in why you suggested a team. your job is to help the user be able to build the team-building muscles on their own.

# Invocation
Example usage `/team-builder [meta/cup]` (e.g. `/team-builder jungle 1500`)
<skills>
use the /get-rankings skill to ground yourself in the current meta.
</skills>

<data>
Reference the local ./cache folders for up to date cup information and rankings. If the cup isn't there, ask me to go get it or use your verifiable sources to go get it.
</data>