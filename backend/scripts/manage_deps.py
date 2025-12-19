import sys
import tomlkit
from pathlib import Path

def merge(web_path, core_path):
    print(f"Merging dependencies from {core_path} into {web_path}...")
    with open(core_path) as f:
        core_data = tomlkit.load(f)
    with open(web_path) as f:
        web_data = tomlkit.load(f)

    core_deps = core_data['project']['dependencies']
    web_deps = web_data['project']['dependencies']

    # Remove gazetrack-core if present
    original_len = len(web_deps)
    web_deps = [d for d in web_deps if not d.startswith('gazetrack-core')]
    if len(web_deps) < original_len:
        print("Removed gazetrack-core dependency.")

    # Add core deps if not present
    current_deps = set(web_deps)
    added_count = 0
    for dep in core_deps:
        if dep not in current_deps:
            web_deps.append(dep)
            current_deps.add(dep)
            added_count += 1
    
    print(f"Added {added_count} dependencies from core.")

    web_data['project']['dependencies'] = web_deps
    
    with open(web_path, 'w') as f:
        tomlkit.dump(web_data, f)
    print("Merge complete.")

def unmerge(web_path, core_path):
    print(f"Unmerging dependencies in {web_path} using {core_path}...")
    with open(core_path) as f:
        core_data = tomlkit.load(f)
    with open(web_path) as f:
        web_data = tomlkit.load(f)

    core_deps = set(core_data['project']['dependencies'])
    web_deps = web_data['project']['dependencies']

    # Remove core deps
    original_len = len(web_deps)
    new_web_deps = [d for d in web_deps if d not in core_deps]
    removed_count = original_len - len(new_web_deps)
    print(f"Removed {removed_count} dependencies found in core.")
    
    # Add gazetrack-core if not present
    if not any(d.startswith('gazetrack-core') for d in new_web_deps):
        new_web_deps.append("gazetrack-core")
        print("Restored gazetrack-core dependency.")
        
    web_data['project']['dependencies'] = new_web_deps

    with open(web_path, 'w') as f:
        tomlkit.dump(web_data, f)
    print("Unmerge complete.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python manage_deps.py [merge|unmerge] [web_toml_path] [core_toml_path]")
        sys.exit(1)
        
    action = sys.argv[1]
    web_toml = sys.argv[2]
    core_toml = sys.argv[3]
    
    if action == "merge":
        merge(web_toml, core_toml)
    elif action == "unmerge":
        unmerge(web_toml, core_toml)
