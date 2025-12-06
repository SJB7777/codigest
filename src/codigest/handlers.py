"""
Implementation of registered commands.
"""
from .commands import registry
from .prompts import DEFAULT_PROMPTS

# NOTE: 'ctx' argument is a Context object passed from Shell/CLI.
# It MUST contain 'actions' (DigestActions) and 'root_path' (Path).

@registry.register(name="scan", desc="Scan project & snapshot", aliases=["s"])
def handle_scan(ctx, args):
    print("⏳ Scanning...", end="\r")
    target_paths = [ (ctx.root_path / a).resolve() for a in args ] if args else None
    content, saved_path = ctx.actions.scan_and_save(target_paths)
    ctx.handle_result(content, saved_path, "Snapshot")

@registry.register(name="diff", desc="Get git diff changes", aliases=["d"])
def handle_diff(ctx, args):
    print("🔍 Checking diff...", end="\r")
    content, saved_path = ctx.actions.diff_and_save()
    ctx.handle_result(content, saved_path, "Git Diff")

@registry.register(name="init", desc="Create config & prompts", aliases=["i"])
def handle_init(ctx, args):
    """
    Generates a config.json file in .codigest/ allowing users to customize prompts.
    """
    config_data = {
        "version": "2.0",
        "description": "Customize your prompts here.",
        "prompts": DEFAULT_PROMPTS
    }
    try:
        path = ctx.actions.io.save_config(config_data)
        print(f"✅ Initialized! Config created at: {path}")
        print("💡 You can now edit the prompts in that file.")
    except Exception as e:
        print(f"❌ Failed to init: {e}")

@registry.register(name="pwd", desc="Print working directory")
def handle_pwd(ctx, args):
    print(ctx.root_path)