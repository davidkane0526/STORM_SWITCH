from pathlib import Path

TOTK = "0x0100F2C0115B6000ULL"


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8-sig")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, got {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# Skip STORM's bundled TOTK profile, then select only asynchronous CPU ASTC decode.
replace_once(
    "src/core/core.cpp",
    "Core::GameFixDatabase::ApplyProfileDirectly(params.program_id);",
    f"if (params.program_id == {TOTK}) {{\n"
    "                Settings::values.accelerate_astc.SetValue(Settings::AstcDecodeMode::CpuAsynchronous);\n"
    "            } else {\n"
    "                Core::GameFixDatabase::ApplyProfileDirectly(params.program_id);\n"
    "            }",
)

# Keep TOTK on the Normal GPU-accuracy fast path even if High was saved previously.
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
