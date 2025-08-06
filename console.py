import os
import re
import sys
import subprocess
import cmd2
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# define scripts directory
SCRIPTS_DIR = "./modules"

class MyConsole(cmd2.Cmd):
    """CSAK interactive console for module/script execution"""

    def __init__(self):
        super().__init__()

        # Enable fluid shell-like tab completion
        self.complete_includespace = True
        self.complete_ignorecase = True

        # Hide built-in commands (keep 'set' and 'show' visible)
        self.hidden_commands.extend([
            'alias', 'macro', 'run_script', 'run_pyscript',
            'shortcuts', 'edit', 'shell'
        ])

        self.current_module = None
        self.current_script = None
        self.script_options = {}  # store user-set options
        self.tools_index = []     # (module, script) list
        self.update_prompt()

    def update_prompt(self):
        """Update the shell prompt based on current context"""
        if self.current_script:
            self.prompt = (
                f"CSAK (" f"{Fore.RED}{self.current_module}{Style.RESET_ALL}) - "
                f"{Fore.RED}{self.current_script}{Style.RESET_ALL} > "
            )
        elif self.current_module:
            self.prompt = (
                f"CSAK (" f"{Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) > "
            )
        else:
            self.prompt = "CSAK > "

    def get_module_description(self, module_name):
        """Read first non-empty line from module's README.md or description.txt"""
        for filename in ["README.md", "description.txt"]:
            path = os.path.join(SCRIPTS_DIR, module_name, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if line.strip():
                            return line.strip()
        return "No description available"

    def get_tool_description(self, module_name, tool_name):
        """Extract docstring or description field from the tool script"""
        path = os.path.join(SCRIPTS_DIR, module_name, f"{tool_name}.py")
        if not os.path.exists(path):
            return "No description available"
        try:
            content = open(path, 'r').read()
            doc = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if doc:
                return doc.group(1).strip().splitlines()[0]
            match = re.search(r'description=["\'](.+?)["\']', content)
            return match.group(1) if match else "No description available"
        except Exception:
            return "No description available"

    def do_list(self, args):
        """List available modules and scripts with descriptions"""
        if not os.path.exists(SCRIPTS_DIR):
            self.perror(f"Scripts directory not found: {SCRIPTS_DIR}")
            return
        self.tools_index.clear()
        idx = 0
        for module in sorted(os.listdir(SCRIPTS_DIR)):
            mod_path = os.path.join(SCRIPTS_DIR, module)
            if not os.path.isdir(mod_path):
                continue
            desc = self.get_module_description(module)
            self.poutput(f"Module: {Fore.MAGENTA}{module}{Style.RESET_ALL} - {desc}")
            for fname in sorted(os.listdir(mod_path)):
                if not fname.endswith('.py'):
                    continue
                script = fname[:-3]
                self.tools_index.append((module, script))
                sdesc = self.get_tool_description(module, script)
                self.poutput(
                    f"  [{Fore.GREEN}{idx}{Style.RESET_ALL}] "
                    f"{Fore.CYAN}{script}{Style.RESET_ALL} - {sdesc}"
                )
                idx += 1
            self.poutput("")

    def do_use(self, arg):
        """Select a tool by number or module/script name"""
        arg = arg.strip()
        if arg.isdigit():
            i = int(arg)
            try:
                m, t = self.tools_index[i]
            except Exception:
                return self.perror(f"No such index {i}")
        elif '/' in arg:
            m, t = arg.split('/', 1)
            if (m, t) not in self.tools_index:
                return self.perror(f"No such tool {arg}")
        else:
            return self.perror("Usage: use <num> or use <module>/<tool>")
        self.current_module, self.current_script = m, t
        self.script_options.clear()
        self.update_prompt()

    def do_show(self, arg):
        """Show options for the selected tool"""
        if arg.strip() == 'options':
            return self._show_options()
        self.perror("Usage: show options")

    def _show_options(self):
        """Internal: display the option table for the current script"""
        if not self.current_script:
            return self.perror("No tool selected.")
        path = os.path.join(SCRIPTS_DIR, self.current_module, f"{self.current_script}.py")
        if not os.path.exists(path):
            return self.perror(f"Tool not found: {path}")
        args = []
        for line in open(path):
            if 'add_argument' not in line:
                continue
            flags = re.findall(r"['\"](-{1,2}[A-Za-z0-9][^'\",]*)['\"]", line)
            if not flags:
                continue
            key = flags[-1].lstrip('-')
            default = re.search(r'default\s*=\s*([^,\s]+)', line)
            req = re.search(r'required\s*=\s*(True|False)', line)
            args.append({
                'option': key,
                'default': default.group(1) if default else '',
                'required': 'Yes' if req and req.group(1)=='True' else 'No',
                'value': self.script_options.get(key, '')
            })
        cols = ['Option', 'Default', 'Required', 'Value']
        widths = {c: len(c) for c in cols}
        for a in args:
            for c in cols:
                widths[c] = max(widths[c], len(str(a[c.lower()])))
        self.poutput('  '.join(c.ljust(widths[c]) for c in cols))
        self.poutput('  '.join('-'*widths[c] for c in cols))
        for a in args:
            self.poutput('  '.join(str(a[c.lower()]).ljust(widths[c]) for c in cols))

    def do_set(self, arg):
        """Set a tool option. Use 'on/off' for boolean flags"""
        parts = arg.split(None, 1)
        if not parts:
            return self.perror("Usage: set <option> [value]")
        k = parts[0]
        v = parts[1] if len(parts) > 1 else None
        path = os.path.join(SCRIPTS_DIR, self.current_module or '', f"{self.current_script or ''}.py")
        flags = []
        if os.path.exists(path):
            for l in open(path):
                if 'add_argument' in l:
                    flags += re.findall(r"['\"](-{1,2}[\w-]+)['\"]", l)
        valid = {f.lstrip('-') for f in flags}
        if k not in valid:
            return self.perror("Invalid option. show options")
        if v and v.lower() in ('on','off'):
            if v.lower()=='on': self.script_options[k]=None
            else: self.script_options.pop(k,None)
            return self.poutput(f"Set {k} = {v.lower()}")
        self.script_options[k] = None if v is None else v
        self.poutput(f"Set {k} = {v if v is not None else '<flag>'}")

    def complete_set(self, text, line, begidx, endidx):
        """Tab-complete file paths for file-like options"""
        tokens = line.split()
        if len(tokens) >= 2 and tokens[1] in {'file','output','path'}:
            return self.path_complete(text, line, begidx, endidx)
        return []

    def do_run(self, args):
        """Run the selected tool with its configured options"""
        if not self.current_script:
            return self.perror("No tool selected.")
        script_path = os.path.join(SCRIPTS_DIR, self.current_module, f"{self.current_script}.py")
        cmd = [sys.executable, script_path]
        for k, v in self.script_options.items():
            if v is None: cmd.append(f"--{k}")
            else:      cmd.extend([f"--{k}", v])
        self.poutput(f"{Fore.YELLOW}Running: {' '.join(cmd)}{Style.RESET_ALL}")
        try:
            subprocess.run(cmd, check=False)
        except Exception as e:
            self.perror(f"Error running tool: {e}")

    def complete_use(self, text, line, begidx, endidx):
        """Tab-complete tool indices or module/script names"""
        opts = [str(i) for i in range(len(self.tools_index))]
        opts += [f"{m}/{t}" for m, t in self.tools_index]
        return [o for o in opts if o.startswith(text)]

if __name__ == "__main__":
    MyConsole().cmdloop()
