# import modules
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
    def __init__(self):
        super().__init__()

        # hiding built in commands (keep 'set' and 'show' visible)
        self.hidden_commands.extend([
            'alias',
            'macro',
            'run_script',
            'run_pyscript',
            'shortcuts',
            'edit',
            'shell'
        ])

        self.current_module = None
        self.current_script = None
        # store user-set options (name -> value)
        self.script_options = {}
        self.tools_index = []
        self.update_prompt()

    def update_prompt(self):
        if self.current_script:
            self.prompt = (
                f"CSAK ("
                f"{Fore.RED}{self.current_module}{Style.RESET_ALL}) - "
                f"{Fore.RED}{self.current_script}{Style.RESET_ALL} > "
            )
        elif self.current_module:
            self.prompt = (
                f"CSAK ("
                f"{Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) > "
            )
        else:
            self.prompt = "CSAK > "

    def get_module_description(self, module_name):
        for filename in ["README.md", "description.txt"]:
            path = os.path.join(SCRIPTS_DIR, module_name, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if line.strip():
                            return line.strip()
        return "No description available"

    def get_tool_description(self, module_name, tool_name):
        path = os.path.join(SCRIPTS_DIR, module_name, f"{tool_name}.py")
        if not os.path.exists(path):
            return "No description available"
        try:
            with open(path, 'r') as f:
                content = f.read()
            docstring = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring:
                return docstring.group(1).strip().split("\n")[0]
            desc_match = re.search(r'description=["\'](.+?)["\']', content)
            return desc_match.group(1) if desc_match else "No description available"
        except:
            return "No description available"

    def do_list(self, args):
        """List all available modules and tools with numeric indexes in a grouped, colorized view."""
        if not os.path.exists(SCRIPTS_DIR):
            self.perror(f"Scripts directory not found: {SCRIPTS_DIR}")
            return
        self.tools_index.clear()
        idx = 0
        for module in sorted(d for d in os.listdir(SCRIPTS_DIR) if os.path.isdir(os.path.join(SCRIPTS_DIR, d))):
            mod_desc = self.get_module_description(module)
            self.poutput(f"Module: {Fore.MAGENTA}{module}{Style.RESET_ALL} - {mod_desc}")
            for script in sorted(f[:-3] for f in os.listdir(os.path.join(SCRIPTS_DIR, module)) if f.endswith('.py')):
                desc = self.get_tool_description(module, script)
                self.tools_index.append((module, script))
                self.poutput(
                    f"  [{Fore.GREEN}{idx}{Style.RESET_ALL}] {Fore.CYAN}{script}{Style.RESET_ALL} - {desc}"
                )
                idx += 1
            self.poutput("")

    def do_use(self, arg):
        """Select a tool by number or by path: use <num> | <module>/<tool>"""
        arg = arg.strip()
        if arg.isdigit():
            i = int(arg)
            try:
                m, t = self.tools_index[i]
            except (IndexError, TypeError):
                self.perror(f"No such index {i}")
                return
        elif '/' in arg:
            m, t = arg.split('/',1)
            if (m,t) not in self.tools_index:
                self.perror(f"No such tool {arg}")
                return
        else:
            self.perror("Usage: use <num> or use <module>/<tool>")
            return
        self.current_module,self.current_script = m,t
        self.script_options.clear()
        self.update_prompt()

    def do_show(self, arg):
        """Show subcommands: show options"""
        if arg.strip()=='options': return self._show_options()
        self.perror("Usage: show options")

    def _show_options(self):
        """Display options in table: name, default, required, value"""
        if not self.current_script:
            self.perror("No tool selected.")
            return
        path = os.path.join(SCRIPTS_DIR,self.current_module,f"{self.current_script}.py")
        if not os.path.exists(path):
            self.perror(f"Tool not found: {path}")
            return
        # collect args
        args=[]
        with open(path,'r') as f:
            for lin in f:
                if 'add_argument' in lin:
                    fs = re.findall(r'"([\-\w, ]+)"',lin)
                    # last flag as key
                    key = fs[-1].lstrip('-').split(',')[0]
                    default = re.search(r'default=(\S+)',lin)
                    req = re.search(r'required=(True|False)',lin)
                    helpm = re.search(r'help=["\'](.+?)["\']',lin)
                    args.append({
                        'option': key,
                        'default': default.group(1) if default else '',
                        'required': 'Yes' if req and req.group(1)=='True' else 'No',
                        'value': self.script_options.get(key,'')
                    })
        # table print
        cols=['Option','Default','Required','Value']
        # col widths
        w={c:len(c) for c in cols}
        for a in args:
            for c in cols:
                w[c]=max(w[c],len(str(a[c.lower()])))
        # header
        hdr='  '.join(c.ljust(w[c]) for c in cols)
        self.poutput(hdr)
        self.poutput('  '.join('-'*w[c] for c in cols))
        # rows
        for a in args:
            row='  '.join(str(a[c.lower()]).ljust(w[c]) for c in cols)
            self.poutput(row)

    def do_set(self, arg):
        """Set an option: set <opt> <val>"""
        parts=arg.split(None,1)
        if len(parts)!=2:
            self.perror("Usage: set <option> <value>")
            return
        k,v=parts
        # validate
        path=os.path.join(SCRIPTS_DIR,self.current_module,f"{self.current_script}.py")
        flags=[]
        with open(path) as f:
            for lin in f:
                if 'add_argument' in lin:
                    flags+=re.findall(r'"([\-\w, ]+)"',lin)
        valids={fl.lstrip('-').split(',')[0] for fl in flags}
        if k not in valids:
            self.perror("Invalid option. show options")
            return
        self.script_options[k]=v
        self.poutput(f"Set {k} = {v}")

    def do_run(self, args):
        """Run selected tool"""
        if not self.current_script:
            self.perror("No tool selected.")
            return
        sp=os.path.join(SCRIPTS_DIR,self.current_module,f"{self.current_script}.py")
        cmd=[sys.executable,sp]
        for k,v in self.script_options.items(): cmd+=[f"--{k}",v]
        self.poutput(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd)

    def complete_use(self,text,line,begidx,endidx):
        args=line.split()
        if len(args)<=1:
            return [str(i) for i in range(len(self.tools_index))]+[f"{m}/{t}" for m,t in self.tools_index]
        p=args[1]
        return [c for c in [str(i) for i in range(len(self.tools_index))]+[f"{m}/{t}" for m,t in self.tools_index] if c.startswith(p)]

if __name__=="__main__":
    MyConsole().cmdloop()
