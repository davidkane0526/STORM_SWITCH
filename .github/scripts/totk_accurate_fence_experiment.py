from pathlib import Path

TOTK = "0x0100F2C0115B6000ULL"


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8-sig")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, got {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# Do not apply STORM's bundled TOTK profile: no High GPU, reactive flushing,
# Fast GPU Time override, memory-layout override, etc.
replace_once(
    "src/core/core.cpp",
    "Core::GameFixDatabase::ApplyProfileDirectly(params.program_id);",
    f"if (params.program_id != {TOTK}) {{\n"
    "                Core::GameFixDatabase::ApplyProfileDirectly(params.program_id);\n"
    "            }",
)

# Keep TOTK on the Normal GPU-accuracy fast path regardless of a stored High setting.
replace_once(
    "src/common/settings.cpp",
    "bool IsGPULevelHigh() {\n    return values.current_gpu_accuracy == GpuAccuracy::High;\n}",
    f"bool IsGPULevelHigh() {{\n"
    f"    if (GetCurrentProgramID() == {TOTK}) {{\n"
    "        return false;\n"
    "    }\n"
    "    return values.current_gpu_accuracy == GpuAccuracy::High;\n"
    "}",
)

# Force only Eden #4182's Accurate GPU-fence policy for TOTK.
for name, enum_name, forced in (
    ("Default", "Default", "false"),
    ("Balanced", "Balanced", "false"),
    ("Accurate", "Accurate", "true"),
    ("Strict", "Strict", "false"),
):
    replace_once(
        "src/common/settings.cpp",
        f"bool IsGPUFenceBehavior{name}() {{\n"
        f"    return values.gpu_fence_behavior.GetValue() == GpuFenceBehavior::{enum_name};\n"
        "}",
        f"bool IsGPUFenceBehavior{name}() {{\n"
        f"    if (GetCurrentProgramID() == {TOTK}) {{\n"
        f"        return {forced};\n"
        "    }\n"
        f"    return values.gpu_fence_behavior.GetValue() == GpuFenceBehavior::{enum_name};\n"
        "}",
    )
