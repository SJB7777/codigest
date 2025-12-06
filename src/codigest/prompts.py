INITIAL_PROMPT_TEMPLATE = """
[SYSTEM: CODIGEST - INITIAL CONTEXT]
You are an expert AI developer. I am providing the full context of a project named "{root_name}".
Please digest this structure and code to build your internal mental model.

<project_root>
{root_name}
</project_root>

<project_structure>
{tree_structure}
</project_structure>

<source_code>
{content}
</source_code>
"""

UPDATE_PROMPT_TEMPLATE = """
[SYSTEM: CODIGEST - INCREMENTAL UPDATE]
Here are the latest changes (git diff) since our last sync.
Please update your memory of the codebase accordingly.

<git_diff>
{diff_content}
</git_diff>
"""