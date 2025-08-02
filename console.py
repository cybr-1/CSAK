# import modules 
import os
import re
import cmd2
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# define scripts directory
SCRIPTS_DIR = "./modules"

class MyConsole(cmd2.Cmd):
    def __init__(self):
        super().__init__()

        # Hide built-in commands you don't want
        self.hidden_commands.extend([
            'alias', 'macro', 'run_script', 'run_pyscript',
            'shortcuts', 'edit', 'set', 'shell'
        ])

        self.current_module = None
        self.current_script = None
        self.script_params = {}
        self.script_options = {}
        self.update_prompt()

    def update_prompt(self):
        if self.current_script:
            self.prompt = f"secops toolkit ({Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) - {Fore.RED}{self.current_script}{Style.RESET_ALL} > "
        elif self.current_module:
            self.prompt = f"secops toolkit ({Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) > "
        else:
            self.prompt = "CSAK > "

    def do_list(self, args):
        """List all available modules and tools."""
        if not os.path.exists(SCRIPTS_DIR):
            print(f"{Fore.RED}Scripts directory not found: {SCRIPTS_DIR}{Style.RESET_ALL}")
            return

        modules = [d for d in os.listdir(SCRIPTS_DIR) if os.path.isdir(os.path.join(SCRIPTS_DIR, d))]
        if not modules:
            print(f"{Fore.RED}No modules found in {SCRIPTS_DIR}{Style.RESET_ALL}")
            return

        for module in sorted(modules):
            module_desc = self.get_module_description(module)
            print(f"{Fore.YELLOW}Module: {module}{Style.RESET_ALL} - {module_desc}")

            module_path = os.path.join(SCRIPTS_DIR, module)
            scripts = [f[:-3] for f in os.listdir(module_path) if f.endswith(".py")]

            if not scripts:
                print(f"  {Fore.YELLOW}No tools in this module{Style.RESET_ALL}\n")
            else:
                for script in sorted(scripts):
                    tool_desc = self.get_tool_description(module, script)
                    print(f"  {Fore.GREEN}↳ {script}{Style.RESET_ALL} - {tool_desc}")
                print("")

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

if __name__ == "__main__":
    console = MyConsole()
    console.cmdloop()
