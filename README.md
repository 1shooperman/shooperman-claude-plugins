# 1shooperman's claude plugin custom marketplace 

## Available Plug-ins
- [pokemon-gbl](https://github.com/1shooperman/shooperman-claude-plugins/blob/main/plugins/pokemon-gbl) — GBL team builder, type chart lookup, and type matchup quiz
- [fitness-coach](https://github.com/1shooperman/shooperman-claude-plugins/blob/main/plugins/fitness-coach) — AI-augmented fitness planning via a panel of real-world expert coaches
- [custom-plugin-tools](https://github.com/1shooperman/shooperman-claude-plugins/blob/main/plugins/custom-plugin-tools) — Multi-agent PR description writer: summarizes changes, audits security, and generates a test plan
- [slack-publish](https://github.com/1shooperman/shooperman-claude-plugins/blob/main/plugins/slack-publish) — Publish local Markdown files to Slack as formatted messages via chat.postMessage


## Add the marketplace
```bash 
claude plugin marketplace add https://github.com/1shooperman/shooperman-claude-plugins.git
```

## Update / Remove the marketplace
```bash
claude plugin marketplace (remove|update) shooperman-claude-plugins
```
  
## Install plug-ins from the custom marketplace
```bash
claude plugin install [plugin-name]
```
