from pathlib import Path
import platform

def entrypoint():
    current_path = Path(__file__).parent.parent
    build_dir = current_path / "packages" / "web" / "dist" / "binary"
    artifact = next(build_dir.glob("gazetrack-web-*"), None)
    sys = platform.system()
    postfix = sys.lower()
    is_windows = sys == "Windows"
    name = f"gazetrack-web-{postfix}.exe" if is_windows else f"gazetrack-web-{postfix}"
    if artifact is not None:
        artifact.rename(build_dir / name)

if __name__ == "__main__":
    entrypoint()