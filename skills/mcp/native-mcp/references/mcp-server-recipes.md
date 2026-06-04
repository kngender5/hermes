# MCP Server Recipes

Tested MCP server configurations for common use cases.

## Filesystem

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/kng"]
    timeout: 30
```

**14 tools**: read_file, read_text_file, read_media_file, read_multiple_files, write_file, edit_file, create_directory, list_directory, list_directory_with_sizes, directory_tree, move_file, search_files, get_file_info, list_allowed_directories

## GitHub

```bash
npm install -g @modelcontextprotocol/server-github
```

Note: shows npm deprecation warning but still works.

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
    timeout: 60
```

**26 tools**: create_or_update_file, search_repositories, create_repository, get_file_contents, push_files, create_issue, create_pull_request, fork_repository, create_branch, list_commits, list_issues, update_issue, add_issue_comment, search_code, search_issues, search_users, get_issue, get_pull_request, list_pull_requests, create_pull_request_review, merge_pull_request, get_pull_request_files, get_pull_request_status, update_pull_request_branch, get_pull_request_comments, get_pull_request_reviews

## Puppeteer (Browser Automation)

```bash
npm install -g @modelcontextprotocol/server-puppeteer
```

Note: `@modelcontextprotocol/server-playwright` does NOT exist on npm. Use puppeteer instead.

```yaml
mcp_servers:
  puppeteer:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-puppeteer"]
    timeout: 60
```

**7 tools**: puppeteer_navigate, puppeteer_screenshot, puppeteer_click, puppeteer_fill, puppeteer_select, puppeteer_hover, puppeteer_evaluate

## CLI Workflow

The `hermes mcp add` command has an interactive confirmation prompt. For scripting/non-interactive use, pipe `y`:

```bash
echo "y" | hermes mcp add <name> --command <cmd> --args <arg1> <arg2>
```

## Catalog Note

`hermes mcp catalog` and `hermes mcp picker` may return empty ("No MCPs in the catalog or configured"). This is a known limitation — the remote catalog is not always populated. Use `hermes mcp add` with manual npx commands as the reliable fallback.

## Troubleshooting

- **Timeout on first connect**: npx downloads the package on first run. Pre-install globally with `npm install -g <package>` to avoid this.
- **"Package not found"**: Verify the exact package name with `npm search @modelcontextprotocol/server-`
- **Deprecated warnings**: Some servers (github, puppeteer) show deprecation warnings but still function.
