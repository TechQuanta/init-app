import sys
import os
import readchar
import time
from pyfiglet import Figlet
from create_app.engine.ui.ui_config import UIConfig

class InitUI(UIConfig):
    """
    Rendering Engine: High-performance interactive layer.
    Standardized for: Base-Slug routing and minimalist navigation.
    """
    def __init__(self, app_name, version):
        self.app_name = app_name
        self.version = version
        self.cfg = UIConfig 
        self.manifest = {}
        # Pre-cache Figlet font for high-speed header rendering
        self.fig = Figlet(font="slant")

    def _get_c(self, key):
        return self.cfg.C.get(key, self.cfg.C["primary"])

    def clear(self):
        """Cross-platform terminal clear."""
        if os.name == 'nt':
            os.system('cls')
        else:
            sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()

    def exit_gracefully(self):
        """Standardized exit sequence."""
        UIConfig.write(f"\n\n  {self.cfg.C['accent']}⚡ DISCONNECTED: {self.cfg.C['white']}session ended by user.")
        UIConfig.write(f"  {self.cfg.C['dim']}engine state preserved. no files were modified.\n")
        sys.exit(0)

    def status_bar(self, steps):
        """Standardized Breadcrumb Navigation."""
        formatted = []
        for i, s in enumerate(steps):
            color = self._get_c("success") if i < len(steps)-1 else self._get_c("accent")
            label = str(s).replace('_', ' ').title()
            formatted.append(f"{color}{label}")
        tag = f" {self.cfg.C['muted']} » ".join(formatted)
        UIConfig.write(f"  {self.cfg.C['muted']}path: {tag}\n")

    def header(self, subtitle, color_key="primary"):
        """High-performance header rendering with buffered output."""
        self.clear()
        c = self._get_c(color_key)
        banner = self.fig.renderText(self.app_name).lower()
        
        output = []
        for line in banner.splitlines():
            output.append(f"  {c}{self.cfg.C['bold']}{line}")
        
        output.append(f"  {c}⚡ {subtitle.lower()} {self.cfg.C['dim']}│ {self.cfg.C['white']}v{self.version}")
        UIConfig.write("\n".join(output) + "\n")

    def menu(self, title, options, color_key="primary", sub_mapping=None, flow=None):
        """Standardized Selector: Returns (Base_Slug, Sub_Value)."""
        selected, sub_idx = 0, -1
        c = self._get_c(color_key)
        
        while True:
            try:
                self.header(title, color_key)
                if flow: self.status_bar(flow)
                
                current_opt = options[selected].lower()
                lookup_key = None
                if sub_mapping:
                    lookup_key = next((k for k in sub_mapping if k.lower() in current_opt), None)

                output = []
                for i, opt in enumerate(options):
                    is_active = (i == selected)
                    label = opt.replace('_', ' ').lower()
                    
                    if is_active:
                        sub_text = ""
                        if sub_mapping and lookup_key:
                            val = sub_mapping[lookup_key][sub_idx] if sub_idx != -1 else "auto"
                            sub_text = f"  {self.cfg.C['accent']}⸬ {self.cfg.C['white']}« {str(val).lower()} »"
                        
                        output.append(f"  {c}{self.cfg.SYMBOL_ACTIVE} {self.cfg.C['bg_highlight']}{self.cfg.C['white']}{self.cfg.C['bold']} {label.ljust(25)} {self.cfg.C['reset']}{sub_text}")
                    else:
                        output.append(f"    {self.cfg.C['white']}{label.ljust(25)}")
                
                UIConfig.write("\n".join(output))
                
                key = readchar.readkey()

                if key == ' ' and "django" in current_opt:
                    options[selected] = "django" if "rest framework" in options[selected].lower() else "django + rest framework"
                elif key == readchar.key.UP: 
                    selected = (selected - 1) % len(options); sub_idx = -1
                elif key == readchar.key.DOWN: 
                    selected = (selected + 1) % len(options); sub_idx = -1
                elif key in ['a', 'd', readchar.key.LEFT, readchar.key.RIGHT] and sub_mapping:
                    if lookup_key: sub_idx = (sub_idx + 1) % len(sub_mapping[lookup_key])
                elif key == readchar.key.ENTER:
                    res_name = options[selected].lower()
                    final_sub = str(sub_mapping[lookup_key][sub_idx]).lower() if (sub_mapping and lookup_key and sub_idx != -1) else "standard"
                    self.manifest[title.lower()] = f"{res_name} ({final_sub})"
                    return res_name, final_sub
                elif key == '\x03': self.exit_gracefully()
            except KeyboardInterrupt: self.exit_gracefully()

    def architect(self, folder_list, fw_slug="standard", flow=None):
        """
        NEXUS ARCHITECT (v0.3.5)
        Manual structure mapping with context-aware filtering.
        """
        # 1. SMART FILTERING: Only show relevant folders for the framework
        # Prevents "Folder Bloat" in the UI
        filtered_list = []
        rag_specific = ['vectordb', 'embeddings', 'knowledge', 'retrievers', 'chains']
        data_specific = ['dags', 'transformers', 'staging', 'analysis']
        
        for f in folder_list:
            if fw_slug == "django" and (f in rag_specific or f in data_specific):
                continue
            if fw_slug == "rag_ai" and f in data_specific:
                continue
            filtered_list.append(f)

        selected, init_map, idx = set(), {}, 0
        # Add administrative controls at the bottom
        master = filtered_list + ["---", "master init (force all)"]
        
        while True:
            try:
                # Use sys.stdout.write for faster rendering than print()
                self.header("nexus architect", "primary")
                if flow: self.status_bar(flow)
                
                output = []
                # Calculate visible range to prevent terminal overflow
                for i, item in enumerate(master):
                    if item == "---": 
                        output.append(f"  {self.cfg.C['dim']}  {'┈' * 35}")
                        continue
                    
                    is_active = (i == idx)
                    is_selected = item in selected
                    
                    # Icons & Styling
                    check_icon = f"{self.cfg.C['success']}{self.cfg.SYMBOL_CHECKED}" if is_selected else f"{self.cfg.C['muted']}{self.cfg.SYMBOL_UNCHECKED}"
                    label = item.replace('_', ' ').lower()
                    
                    if is_active:
                        # Logic for Init Toggle (Python Package vs Folder)
                        status = f"  {self.cfg.C['success']}{self.cfg.SYMBOL_INIT_ON} init" if init_map.get(item) else f"  {self.cfg.C['dim']}{self.cfg.SYMBOL_INIT_OFF} init"
                        output.append(f"  {self._get_c('primary')}{self.cfg.SYMBOL_ACTIVE} {self.cfg.C['bg_highlight']}{self.cfg.C['white']}{self.cfg.C['bold']} {check_icon} {label.ljust(22)} {self.cfg.C['reset']}{status}")
                    else:
                        mark = f"{self.cfg.C['success']}•" if init_map.get(item) else " "
                        output.append(f"    {check_icon} {self.cfg.C['white']}{label.ljust(22)} {mark}")
                
                # Buffered write to prevent flickering
                UIConfig.write("\n".join(output))
                UIConfig.write(f"\n  {self.cfg.C['muted']}(Space) Toggle | (Arrows) Package Init | (Enter) Confirm")
                
                key = readchar.readkey()
                
                if key == readchar.key.UP: 
                    idx = (idx - 1) % len(master)
                elif key == readchar.key.DOWN: 
                    idx = (idx + 1) % len(master)
                elif key == ' ':
                    target = master[idx]
                    if target == "master init (force all)":
                        for f in selected: init_map[f] = True
                    elif target != "---":
                        if target in selected:
                            selected.remove(target)
                            init_map[target] = False
                        else:
                            selected.add(target)
                elif key in ['a', 'd', readchar.key.LEFT, readchar.key.RIGHT]:
                    target = master[idx]
                    if target not in ["---", "master init (force all)"] and target in selected:
                        init_map[target] = not init_map.get(target, False)
                elif key == readchar.key.ENTER:
                    # Filter the init_map to only include selected folders
                    final_init_strategy = {f: init_map.get(f, False) for f in selected}
                    self.manifest["domain folders"] = f"{len(selected)} folders"
                    return selected, final_init_strategy
                elif key == '\x03': 
                    self.exit_gracefully()
                    
            except KeyboardInterrupt: 
                self.exit_gracefully()

    def checklist(self, title, label, items, flow=None):
        """Standardized Checklist for Infra/Addons."""
        selected, idx = set(), 0
        while True:
            try:
                self.header(title, "primary")
                if flow: self.status_bar(flow)
                UIConfig.write(f"  {self.cfg.C['dim']}layer: {self.cfg.C['white']}{label.lower()}\n")
                output = []
                for i, item in enumerate(items):
                    is_active = (i == idx)
                    check = f"{self.cfg.C['success']}{self.cfg.SYMBOL_CHECKED}" if item in selected else f"{self.cfg.C['muted']}{self.cfg.SYMBOL_UNCHECKED}"
                    display_name = item.split('/')[-1].lower() if '/' in item else item.lower()
                    
                    if is_active:
                        output.append(f"  {self._get_c('primary')}{self.cfg.SYMBOL_ACTIVE} {self.cfg.C['bg_highlight']}{self.cfg.C['white']}{self.cfg.C['bold']} {check} {display_name.ljust(30)} {self.cfg.C['reset']}")
                    else:
                        output.append(f"    {check} {self.cfg.C['white']}{display_name}")
                
                UIConfig.write("\n".join(output))
                key = readchar.readkey()
                if key == readchar.key.UP: idx = (idx - 1) % len(items)
                elif key == readchar.key.DOWN: idx = (idx + 1) % len(items)
                elif key == ' ':
                    t = items[idx]; selected.remove(t) if t in selected else selected.add(t)
                elif key == readchar.key.ENTER:
                    self.manifest[label.lower()] = f"{len(selected)} items"
                    return selected
                elif key == '\x03': self.exit_gracefully()
            except KeyboardInterrupt: self.exit_gracefully()

    def finalize(self, p_name):
        """Standardized Compact Summary Manifest."""
        self.header("mission sequence", "success")
        c = self.cfg.C
        fw = str(self.manifest.get("core blueprint", "fastapi")).split(' (')[0].lower()
        mode = str(self.manifest.get("build strategy", "standard")).lower()
        db = str(self.manifest.get("database", "sqlite")).split(' ')[0].lower()
        
        infra_total = 0
        for key in ["docker", "automation", "github", "kubernetes", "community"]:
            val = self.manifest.get(key, "0 items")
            if isinstance(val, str) and "items" in val: infra_total += int(val.split(' ')[0])

        UIConfig.write(f"  {c['muted']}┌──────────────────────────────────────────┐")
        UIConfig.write(f"  {c['muted']}│ {c['white']}NAME  : {c['primary']}{p_name[:12].ljust(12)} {c['white']}ENGINE: {c['primary']}{fw[:10].ljust(10)} {c['muted']}│")
        UIConfig.write(f"  {c['muted']}│ {c['white']}MODE  : {c['primary']}{mode[:12].ljust(12)} {c['white']}DB    : {c['primary']}{db[:10].ljust(10)} {c['muted']}│")
        UIConfig.write(f"  {c['muted']}│ {c['white']}VENV  : {c['primary']}{str(self.manifest.get('venv_enabled', False)).ljust(12)} {c['white']}INFRA : {c['primary']}{(str(infra_total) + ' files').ljust(10)} {c['muted']}│")
        UIConfig.write(f"  {c['muted']}└──────────────────────────────────────────┘")
        UIConfig.write(f"\n  {c['success']}✔ {c['bold']}system sequence verified")